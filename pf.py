import numpy as np


class Bus:
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

class Line:
    def __init__(
            self,
            from_bus: Bus,
            to_bus: Bus,
            R: float,
            X: float,
            from_Y: complex,
            to_Y: complex,
            operation: bool) -> None:

        self.from_bus = from_bus    # Barra de inicio
        self.to_bus = to_bus        # Barra final
        self.R = R                  # Resistencia pu
        self.X = X                  # Reactancia pu
        # Admitancias de derivación
        self.from_Y = from_Y        # Mitad al inicio
        self.to_Y = to_Y            # Otra mitad al final
        self.operation = operation  # True: It is in operation

    def __str__(self):
        """Información.

        Mostrar atributos de la instancia particular.
        """
        return f'{self.__dict__}'

class Transformer:
    """Transformador con relación de transformación no nominal.

    Modela los transformadores de dos devanados cuando su relación
    de transformación no es nominal, es decir los cambiadores de tomas
    no se encuentran en la posición que garantiza la relación de
    transformación nominal por lo tanto no es posible modelarlos como
    una instancia de la clase ``Line``.

    """
    def __init__(
            self,
            from_bus: Bus,
            to_bus: Bus,
            R: float,
            X: float,
            from_Y: complex,
            to_Y: complex,
            c: float):

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.X = X              # Reactancia  pu base 100 MVA
        self.R = R              # Resistencia pu base 100 MVA
        self.from_Y = from_Y    # Rama derivada a la entrada
        self.to_Y = to_Y        # Rama derivada a la salida
        self.c = c      # Relación de transformación 1/n en pu

    def __str__(self):
        """Información.

        Mostrar atributos de la instancia particular.
        """
        return f'{self.__dict__}'

if __name__ == "__main__":

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

                buses[name] = Bus(
                    name=name, V=np.nan, phase=np.nan, PL=np.nan,
                    QL=np.nan,  Vb=Vb, G=np.nan, B=np.nan, bus_type=np.nan
                )

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
                    buses[name].PL = -float(words[7]) / Bus.S_base
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
                buses[name].PL = float(words[5]) / Bus.S_base
                # Reactiva
                buses[name].QL = float(words[8]) / Bus.S_base
                # Tipo
                buses[name].bus_type = 'PQ'

            # Aquellas que tienen compensadores en derivación
            elif words[0] == 'Compensador':
                name = words[3]
                buses[name].G = 0.0
                buses[name].B = float(words[6]) / Bus.S_base

            # Crear instancias de líneas
            elif words[0] == 'Línea':
                name_from = words[2]
                name_to = words[4]
                # Crear instancia
                line = Line(
                    from_bus=buses[name_from],
                    to_bus=buses[name_to],
                    R=float(words[8]) / buses[name_from].Vb,
                    X=float(words[12]) / buses[name_from].Vb,
                    from_Y=float(words[17]) / buses[name_from].Vb,
                    to_Y=float(words[17]) / buses[name_from].Vb,
                    operation=True
                )
                # Almacenar en lista
                lines.append(line)

            # Crear instancias de transformadores
            elif words[0] == 'Transformador':
                name_from = words[2]
                name_to = words[4]
                # Impedancia en base nueva
                Z_old = float(words[8])/100 + 1j*float(words[12])/100
                Sb_old = float(words[21])   # Capacidad
                Z_new = (Z_old*Bus.S_base) / (Sb_old)
                # Crear instancia
                transformer = Transformer(
                    from_bus=buses[name_from],
                    to_bus=buses[name_to],
                    R=Z_new.real,
                    X=Z_new.imag,
                    from_Y=np.nan,
                    to_Y=np.nan,
                    c = 1/((float(words[16]))*(100))
                )
                # Almacenar en lista
                transformers.append(transformer)
