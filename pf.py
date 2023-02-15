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
    '''
    Clase para representar una línea de la red eléctrica.
    '''

    def __init__(self, from_bus, to_bus, X, R, from_Y, to_Y):

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.X = X
        self.R = R
        self.from_Y = from_Y
        self.to_Y = to_Y

if __name__ == "__main__":

    buses = {}
    lineas = []





    with open('data/nordico.txt') as f:
        for line in f:
            words = line.split(' ')

            # Saltarse líneas vacías (continúa a siguiente iteración)
            if len(words) == 0:
                continue

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
                buses[name] = 'PQ'

            # Aquellas que tienen compensadores en derivación
            elif words[0] == 'Compensador':
                name = words[3]
                buses[name].PL = 0.0
                buses[name].QL = float(words[6]) / Bus.S_base


            elif words[0] == 'Línea':
                from_bus = words[2]
                to_bus = words[4]
                R = words[8] #####Pasar a pu
                X = words[12] #####Pasar a pu
                B = words[17] #####Pasar a pu
                total_B = j*B
                lineas = Line(from_bus, to_bus, X, R, total_B, total_B)
                lineas.append(lineas)








    print(buses['g20'])     # Slack
    print(len(buses))
    print(lineas)
    