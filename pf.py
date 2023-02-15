import numpy as np

class Bus:

    def __init__(self, name: str, Vb: float, V: float) -> None:

        self.name = name    # str
        self.Vb = Vb    # kV
        self.V = V      # pu

    def __str__(self):

        return f'Soy la barra {self.name} con Vb = {self.Vb} y V = {self.V}'

buses = {}

with open('data/nordico.txt') as f:
    for line in f:
        words = line.split(' ')

        # Saltarse líneas vacías (continúa a siguiente iteración)
        if len(words) == 0:
            continue

        # Identificar barras (no va a dar error porque len(words) es al menos 1)
        if words[0] == 'Barra':
            name = words[2]
            Vb = float(words[7])

            buses[name] = Bus(name=name, Vb=Vb, V=np.nan)

        elif words[0] == 'Generador':
            name = words[3]
            V = float(words[12]) / buses[name].Vb
            buses[name].V = V

print(buses['g1'])