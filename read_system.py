import numpy as np

# ------------
# Asignación 1
# ------------
# Leer el archivo nordico.txt y crear un modelo eléctrico
# de la red.

class MyBus:
    # Todas las cantidades en pu suponen una base de 100 MVA.
    S_base = 100    # MVA
    def __init__(self,
                 name: str,
                 V: float,
                 phase: float,
                 PL: float,
                 QL: float,
                 Vb: float,
                 G: float,
                 B: float,
                 bus_type: str) -> None:

        self.name = name    # Identificador (label)
        self.V = V          # pu
        self.phase = phase  # rad
        self.PL = PL        # MW consumidos en pu
        self.QL = QL        # Mvar consumidos en pu
        self.Vb = Vb        # kV
        self.G = G          # Conductancia
        self.B = B          # Susceptancia
        self.bus_type = bus_type    # Ya sea 'Slack', 'PV' o 'PQ'

    def __str__(self):
        """Información.

        Mostrar atributos de la instancia particular.
        """
        return f'{self.__dict__}'

class MyLine:
    def __init__(
            self,
            from_bus: MyBus,
            to_bus: MyBus,
            R: float,
            X: float,
            # from_Y: complex,
            # to_Y: complex,
            total_G: float,
            total_B: float) -> None:

        self.from_bus = from_bus    # Barra de inicio
        self.to_bus = to_bus        # Barra final
        self.R = R                  # Resistencia pu
        self.X = X                  # Reactancia pu
        # Admitancias de derivación
        # self.from_Y = from_Y        # Mitad al inicio
        # self.to_Y = to_Y            # Otra mitad al final
        self.total_G = total_G
        self.total_B = total_B

    def __str__(self):
        """Información.

        Mostrar atributos de la instancia particular.
        """
        return f'{self.__dict__}'

class MyTransformer:
    """Transformador con relación de transformación no nominal.

    Modela los transformadores de dos devanados cuando su relación
    de transformación no es nominal, es decir los cambiadores de tomas
    no se encuentran en la posición que garantiza la relación de
    transformación nominal por lo tanto no es posible modelarlos como
    una instancia de la clase ``Line``.

    """
    def __init__(
            self,
            from_bus: MyBus,
            to_bus: MyBus,
            R: float,
            X: float,
            n: float,
            MVA: float):

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.R = R              # Resistencia pu base propia del transformador
        self.X = X              # Reactancia  pu base propia del transformador
        self.n = n              # Relación de transformación
        self.MVA = MVA          # Capacidad

    def __str__(self):
        """Información.

        Mostrar atributos de la instancia particular.
        """
        return f'{self.__dict__}'

if __name__ == "__main__":

    import pf
    import matplotlib.pyplot as plt
    buses = {}
    lines = []
    transformers = []

    with open('data/nordico.txt') as f:
        for line in f:
            words = line.split(' ')

            # Saltarse líneas vacías (continúa a siguiente iteración)
            if len(words) == 0:
                continue

            # Crear instancias de barras
            # Identificar barras
            if words[0] == 'Barra':
                name = words[2]
                Vb = float(words[7])

                buses[name] = MyBus(
                    name=name, V=np.nan, phase=np.nan, PL=0,
                    QL=0,  Vb=Vb, G=0, B=0, bus_type='PQ'
                )

            elif words[0] == 'La':
                name = words[2]
                bus = buses[name]
                bus.pf_results_V = float(words[5])

            # Pasar atributos según su tipo:
            #
            # De generación:
            elif words[0] == 'Generador':
                name = words[3]
                # Slack
                if name == 'g20':
                    V = float(words[12]) / buses[name].Vb
                    buses[name].V = V
                    buses[name].phase = 0.0
                    buses[name].bus_type = 'Slack'
                else:
                    # Potencia injectada: negativa por ser de generación
                    buses[name].PL -= float(words[7]) / MyBus.S_base
                    # Tensión (magnitud) en pu:
                    V = float(words[12]) / buses[name].Vb
                    buses[name].V = V
                    # Tipo
                    buses[name].bus_type = 'PV'

            # De carga:
            elif words[0] == 'Carga':
                name = words[3]
                # Potencia injectada: positiva por ser de carga
                # Activa
                buses[name].PL += float(words[5]) / MyBus.S_base
                # Reactiva
                buses[name].QL += float(words[8]) / MyBus.S_base
                # # Tipo
                # buses[name].bus_type = 'PQ'

            # Aquellas que tienen compensadores en derivación
            elif words[0] == 'Compensador':
                name = words[3]
                buses[name].B = float(words[6]) / MyBus.S_base

            # Crear instancias de líneas
            elif words[0] == 'Línea':
                name_from = words[2]
                name_to = words[4]
                Vb = buses[name_from].Vb
                Sb = buses[name_from].S_base
                B_half = float(words[17]) * 1e-6 * Vb**2 / Sb
                # Crear instancia
                line = MyLine(
                    from_bus=buses[name_from],
                    to_bus=buses[name_to],
                    R=float(words[8]) * Sb / Vb**2,
                    X=float(words[12]) * Sb / Vb**2,
                    total_G=0,
                    total_B=2*B_half,
                    # from_Y=float(words[17]) / buses[name_from].Vb,
                    # to_Y=float(words[17]) / buses[name_from].Vb,
                )
                # Almacenar en lista
                lines.append(line)

            # Crear instancias de transformadores
            elif words[0] == 'Transformador':
                name_from = words[2]
                name_to = words[4]
                # Impedancia en base nueva
                R = float(words[8])/100
                X = float(words[12])/100
                n = float(words[16]) / 100  # Relación de vueltas
                capacidad = float(words[21])   # Capacidad nominal
                # Crear instancia
                transformer = MyTransformer(
                    from_bus=buses[name_from],
                    to_bus=buses[name_to],
                    R=R,
                    X=X,
                    n=n,
                    MVA=capacidad
                )
                # Almacenar en lista
                transformers.append(transformer)

    # Definir el nordic
    sys = pf.System()

    # Definir barras
    for bus_name, bus in buses.items():

        if bus.bus_type == 'Slack':
            b = sys.add_slack(V=bus.V, Vb=bus.Vb, name=bus.name)

        elif bus.bus_type == 'PQ':
            b = sys.add_PQ(PL=bus.PL,
                           QL=bus.QL,
                           Vb=bus.Vb,
                           G=bus.G,
                           B=bus.B,
                           name=bus.name)

        elif bus.bus_type == 'PV':
            b = sys.add_PV(V=bus.V,
                           PL=bus.PL,
                           QL=bus.QL,
                           Vb=bus.Vb,
                           G=bus.G,
                           B=bus.B,
                           name=bus.name)
            
        bus.associated_pf_bus = b

    # Definir líneas
    for ln in lines:
        sys.add_line(from_bus=ln.from_bus.associated_pf_bus,
                     to_bus=ln.to_bus.associated_pf_bus,
                     X=ln.X,
                     R=ln.R,
                     total_G=0,
                     total_B=ln.total_B)

    # Definir transformadores
    for tx in transformers:
        sys.add_transformer(from_bus=tx.to_bus.associated_pf_bus,
                            to_bus=tx.from_bus.associated_pf_bus,
                            R=tx.R,
                            X=tx.X,
                            n=tx.n,
                            MVA=tx.MVA,
                            Sbase=100)
        
    # Correr fujo de potencia
    sys.run_pf()

    # ------------
    # Asignación 2
    # ------------
    # Conduzca un estudio de flujos de potencia y compare
    # las tensiones calculadas con las presentadas al final
    # del archivo nordico.txt

    # Verificar resultados
    for bus_name, bus in buses.items():
        error = abs(bus.associated_pf_bus.V - bus.pf_results_V)
        print(f'El error para {bus_name} es {error} pu')

    # ------------
    # Asignación 3
    # ------------
    # Análisis de cargabilidad

    # Zona central
    loads = ['1', '2', '3', '4', '5', '41', '42', '43', '46', '47', '51']
    central_PQ = {}
    for b in loads:
        central_PQ[b] = buses[b].associated_pf_bus

    # Taza
    lambd = 1
    delta = 0.001
    lambds = []
    # Respuesta de tensiones
    tensiones = {v: [] for v in central_PQ}
    # Aumentar carga
    while sys.run_pf():
        # Anexar lambds
        lambds.append(lambd)
        # Anexar tensión resultante
        for (name, bus) in central_PQ.items():
            tensiones[name].append(bus.V)
        # Quitar incremento anterior
        for (n, bus) in central_PQ.items():
            bus.PL /= lambd
            bus.QL /= lambd
        # Actualizar lambd
        lambd += delta
        # Aumentar cada carga
        for (name, bus) in central_PQ.items():
            bus.PL *= lambd
            bus.QL *= lambd

    plt.figure()
    for name, v in tensiones.items():
        plt.plot(lambds, tensiones[name], label=name)
    plt.xlabel('$\lambda$')
    plt.ylabel('Tensión [pu]')
    plt.title('Análisis de cargabilidad')
    plt.legend()
    plt.show()

    # # ------------
    # # Asignación 4
    # # ------------
    # # Análisis de contingencia: Prueba n - 1
    # # Nota: Volver a correr el programa para ésta prueba.

    # for ln in sys.lines:
    #     ln.in_operation = False
    #     if not sys.run_pf():
    #         # Líneas críticas
    #         print(f'Desconección de línea {ln}')
    #     ln.in_operation = True