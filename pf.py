import numpy as np
import scipy
import tabulate
import warnings

class Bus:
    '''
    Clase para representar una barra de la red eléctrica.
    '''

    def __init__(self, V, theta, PL, QL, G, B, Vb, bus_type, name):

        self.V = V
        self.theta = theta
        self.PL = PL
        self.QL = QL
        self.G = G
        self.B = B
        self.Vb = Vb
        self.bus_type = bus_type
        self.name = name
        self.P_to_network = np.nan
        self.Q_to_network = np.nan

    def __str__(self):
        return f'{self.name}'

    def get_phasor_V(self):
        '''
        Devolver tensión de la barra en forma fasorial.
        '''

        return self.V*np.exp(1j*self.theta)

class Line:
    '''
    Clase para representar una línea de la red eléctrica.
    '''

    def __init__(self, from_bus, to_bus, X, R, from_Y, to_Y, in_operation):

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.X = X
        self.R = R
        self.from_Y = from_Y
        self.to_Y = to_Y
        self.in_operation = in_operation

    def __str__(self):
        return f'{self.from_bus} -> {self.to_bus}'

class Transformer:
    '''
    Clase para representar transformador con cambiador de tomas.
    '''

    def __init__(self, from_bus, to_bus, R, X, n, MVA, Sbase):
        '''
        R y X están en pu de base propia, n está en pu.

        Se suponen la siguiente convención:

        from   n:1   R+jX      to
        |------0 0---xxxx------|
        '''

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.R = R * Sbase / MVA
        self.X = X * Sbase / MVA
        self.n = n

    def get_pi_model(self):
        '''
        Devuelve parámetros del modelo pi.
        '''

        Y = 1/(self.R + 1j*self.X)
        Y_series = Y/self.n
        from_Y = Y/self.n**2 - Y_series
        to_Y = Y - Y_series

        return Y_series, from_Y, to_Y

class System:
    '''
    Clase para representar una red eléctrica.
    '''

    def __init__(self, Sb=100, name=''):

        self.slack = None
        self.buses = []
        self.non_slack_buses = []
        self.PQ_buses = []
        self.PV_buses = []
        self.lines = []
        self.transformers = []
        self.Sb = Sb
        self.name = name
        self.status = 'unsolved'

    def organize_buses(self):
        '''
        Organizar las barras en este orden: slack, PQ, PV.
        '''

        # Ordenar barras que no son la oscilante
        self.non_slack_buses = self.PQ_buses + self.PV_buses

        # Colocar barra oscilante al principio
        if self.slack != None:
            self.buses = [self.slack] + self.non_slack_buses
        else:
            self.buses = self.non_slack_buses

    def store_bus(self, bus):
        '''
        Almacenar barra en las listas correspondientes y organizarlas.
        '''

        if bus.bus_type == 'Slack':
            self.slack = bus
        elif bus.bus_type == 'PQ':
            self.PQ_buses.append(bus)
        elif bus.bus_type == 'PV':
            self.PV_buses.append(bus)

        self.organize_buses()

    def add_slack(self, V, Vb, theta=0, PL=0, QL=0, G=0, B=0, name=''):
        '''
        Agregar barra oscilante a la red.
        '''

        bus = Bus(V, theta, PL, QL, G, B, Vb, 'Slack', name)
        self.store_bus(bus)

        return bus

    def add_PQ(self, PL, QL, Vb, G=0, B=0, name=''):
        '''
        Agregar barra PQ a la red.
        '''

        bus = Bus(1, 0, PL, QL, G, B, Vb, 'PQ', name)
        self.store_bus(bus)

        return bus

    def add_PV(self, PL, V, Vb, QL=0, G=0, B=0, name=''):
        '''
        Agregar barra PV a la red.
        '''

        bus = Bus(V, 0, PL, 0, G, B, Vb, 'PV', name)
        self.store_bus(bus)

        return bus

    def add_transformer(self, from_bus, to_bus, R, X, n, MVA, Sbase=100):

        t = Transformer(from_bus, to_bus, R, X, n, MVA, Sbase)
        self.transformers.append(t)

        return t

    def add_line(self, from_bus, to_bus, X, R=0, total_G=0, total_B=0):
        '''
        Agregar línea a la red.
        '''

        total_Y = total_G + 1j*total_B
        line = Line(from_bus,
                    to_bus,
                    X,
                    R,
                    total_Y/2,
                    total_Y/2,
                    in_operation=True)
        self.lines.append(line)

        return line

    def build_Y(self):
        '''
        Construir matriz de admitancias nodales.
        '''

        # Inicializar matriz de admitancias
        N = len(self.buses)
        self.Y = np.zeros([N, N], dtype=complex)

        # Agregar contribuciones de las barras
        for i, bus in enumerate(self.buses):
            self.Y[i, i] += bus.G + 1j*bus.B

        # Agregar contribuciones de las líneas
        for line in self.lines:
            if line.in_operation:
                # Obtener índices
                i = self.buses.index(line.from_bus)
                j = self.buses.index(line.to_bus)
                # Obtener admitancia serie
                Y_series = 1/(line.R + 1j*line.X)
                # Agregar contribuciones
                self.Y[i, i] += line.from_Y + Y_series
                self.Y[j, j] += line.to_Y + Y_series
                self.Y[i, j] -= Y_series
                self.Y[j, i] -= Y_series

        # Agregar contribuciones de transformadores
        for trafo in self.transformers:
            # Obtener índices
            i = self.buses.index(trafo.from_bus)
            j = self.buses.index(trafo.to_bus)
            # Obtener admitancias
            Y_series, from_Y, to_Y = trafo.get_pi_model()
            # Agregar contribuciones
            self.Y[i, i] += from_Y + Y_series
            self.Y[j, j] += to_Y + Y_series
            self.Y[i, j] -= Y_series
            self.Y[j, i] -= Y_series

    def build_dS_dV(self):
        '''
        Construir eficientemente las derivadas parciales de la potencia de las barras.

        Ver detalles en https://matpower.org/docs/TN2-OPF-Derivatives.pdf
        '''

        V = np.array([bus.V*np.exp(1j*bus.theta) for bus in self.buses])
        ib = range(len(V))
        Ybus = scipy.sparse.csr_matrix(self.Y)

        Ibus = Ybus*V
        diagV = scipy.sparse.csr_matrix((V, (ib, ib)))
        diagIbus = scipy.sparse.csr_matrix((Ibus, (ib, ib)))
        diagVnorm = scipy.sparse.csr_matrix((V/np.abs(V), (ib, ib)))

        dS_dVm = diagV*np.conj(Ybus*diagVnorm) + np.conj(diagIbus)*diagVnorm
        dS_dVa = 1j*diagV*np.conj(diagIbus - Ybus*diagV)

        dS_dVm = dS_dVm.toarray()
        dS_dVa = dS_dVa.toarray()

        return dS_dVm, dS_dVa

    def build_J(self):
        '''
        Construir matriz jacobiana.
        '''

        dS_dVm, dS_dVa = self.build_dS_dV()

        M = len(self.PQ_buses)
        J11 = dS_dVa[1:, 1:].real
        J12 = dS_dVm[1:, 1:M+1].real
        J21 = dS_dVa[1:M+1, 1:].imag
        J22 = dS_dVm[1:M+1, 1:M+1].imag

        self.J = np.vstack([np.hstack([J11, J12]), np.hstack([J21, J22])])

    def S_towards_network(self):
        '''
        Devolver la potencia compleja que fluye hacia la red desde cada barra.
        '''

        V = np.array([bus.V*np.exp(1j*bus.theta) for bus in self.buses])
        ib = range(len(V))
        Ybus = scipy.sparse.csr_matrix(self.Y)

        Ibus = Ybus*V
        diagV = scipy.sparse.csr_matrix((V, (ib, ib)))

        S_to_network = diagV*np.conj(Ybus*np.asmatrix(V).T)

        return S_to_network

    def update_S(self, x):
        '''
        Update P and Q consumption at all buses.

        To get the power demanded by an injector at a PQ bus, recall that it's
        possible to call get_P() and get_Q(), which will use the most recent
        voltage to get P and Q.
        '''

        # Get power going to the network
        SL = - self.S_towards_network()

        # Add it as an attribute to the bus
        for (i, bus) in enumerate(self.buses):
            bus.P_to_network = - SL[i, 0].real
            bus.Q_to_network = - SL[i, 0].imag

    def build_F(self):
        '''
        Construir vector de diferencias de potencia (mismatch) de las barras PQ.
        '''

        # Determinar potencia inyectada
        S_injected = np.array([[-bus.PL - 1j*bus.QL] for bus in self.buses],
                              dtype=complex)

        # Determinar diferencias de potencia
        delta_S = self.S_towards_network() - S_injected

        # Construir vector de diferencias de potencia
        M = len(self.PQ_buses)
        F00 = delta_S[1:, 0].real
        F10 = delta_S[1:M+1, 0].imag

        self.F = np.vstack([F00, F10])

    def update_v(self, x):
        '''
        Actualizar tensión y ángulo de las barras.
        '''

        # Actualizar ángulos
        for i, bus in enumerate(self.non_slack_buses):
            bus.theta = x[i, 0]

        # Actualizar magnitudes
        for i, bus in enumerate(self.PQ_buses):
            bus.V = x[len(self.non_slack_buses)+i, 0]

    def run_pf(self, tol=1e-12, max_iters=20):
        '''
        Correr estudio de flujo de potencia usando el método de Newton-Raphson.
        '''

        # Construir matriz de admitancias nodales
        self.build_Y()

        # Asegurar 'flat start'
        x0 = len(self.non_slack_buses)*[0] + len(self.PQ_buses)*[1]
        x0 = np.array([x0], dtype=float).T

        # Inicializar variables de iteración
        x = x0
        iters = 0

        # Inicializar atributos
        self.update_v(x)
        self.build_F()
        self.build_J()

        # Aplicar método de Newton-Raphson
        while np.max(np.abs(self.F)) > tol and iters < max_iters:
            # Actualizar variables
            x -= np.matmul(np.linalg.inv(self.J), self.F)
            iters += 1
            # Actualizar atributos
            self.update_v(x)
            self.build_F()
            self.build_J()

        # Update complex powers
        self.update_S(x)

        # Update status
        if iters < max_iters:
            tol_W = round(tol*self.Sb*1e6, 3)
            self.status = 'solved (max |F| < ' + str(tol_W) + ' W) ' \
                        + 'in ' + str(iters) + ' iterations'
            return True
        else:
            self.status = 'non-convergent after ' + str(iters) + ' iterations'
            warnings.warn('Newton-Raphson did not converge after ' \
                         + str(iters) + ' iterations.')
            return False

    def __str__(self):
        '''
        Display system data in tabular form.

        The net load can vary depending on the method chosen for simulating
        capacitors.

        If they were considered shunt admittances, they will not
        contribute to the net load, because it's as if they were part of the
        network, not a device that is connected to the bus.

        If, instead, they were considered as injectors, they will contribute
        to the net load.

        In any case, this does not affect the voltages. It's only a matter of
        displaying results.
        '''

        # Fetch data
        data = [[self.buses.index(bus) + 1,
                 bus.name,
                 bus.bus_type,
                 bus.Vb,
                 bus.V,
                 np.rad2deg(bus.theta),
                 self.get_bus_load(bus, attr='P'),
                 self.get_bus_load(bus, attr='Q'),
                 self.get_bus_generation(bus, attr='P'),
                 self.get_bus_generation(bus, attr='Q')]
                for bus in self.buses]

        # Define headers
        headers = ['\n\nBus', '\n\nName', '\n\nType', 'Nominal\nvoltage\n(kV)',
                   '\nVoltage\n(pu)', '\nPhase\n(degrees)',
                   '\nLoad\n(MW)', '\nLoad\n(Mvar)',
                   '\nGeneration\n(MW)', '\nGeneration\n(Mvar)']

         # Build tables
        precision = (0, 0, 0, '.1f', '.4f', '.2f', '.3f', '.3f', '.3f', '.3f')
        table = tabulate.tabulate(data, headers=headers, floatfmt=precision)

        # Possibly add a filler name for the system
        if self.name == '':
            display_name = str(len(self.buses)) + '-bus system'
        else:
            display_name = self.name

        # Report the status (including convergence and number of iterations)
        display_status = "Status: " + self.status

        # Build output string
        output_str = '\n' + display_name + '\n\n' + display_status \
                   + '\n\n' + table + '\n'

        return output_str

    def get_bus_load(self, bus, attr='P', tol=1e-6):
        '''
        Return a string with total load.
        '''

        # Add loads from PL
        total_load = self.Sb*getattr(bus, attr + 'L')

        return total_load if abs(total_load) > tol else None

    def get_bus_generation(self, bus, attr='P', tol=1e-4):
        '''
        Return a string with total generation.
        '''

        return self.Sb*getattr(bus, attr + '_to_network') if bus.bus_type != 'PQ' else None

if __name__ == '__main__':

    # Probar implementación con sistema de prueba (Duncan Glover, ejemplo 6.9)

    sys = System()

    b1 = sys.add_slack(V=1.0, Vb=15, name='B1')
    b2 = sys.add_PQ(PL=8, QL=2.8, Vb=345, name='B2')
    b3 = sys.add_PV(V=1.05, PL=0.8-5.2, Vb=15, name='B3')
    b4 = sys.add_PQ(PL=0, QL=0, Vb=345, name='B4')
    b5 = sys.add_PQ(PL=0, QL=0, Vb=345, name='B5')

    sys.add_line(from_bus=b2, to_bus=b4, R=0.009, X=0.1, total_B=1.72)
    sys.add_line(from_bus=b2, to_bus=b5, R=0.0045, X=0.05, total_B=0.88)
    sys.add_line(from_bus=b4, to_bus=b5, R=0.00225, X=0.025, total_B=0.44)

    sys.add_line(from_bus=b1, to_bus=b5, R=0.0015, X=0.02)
    sys.add_line(from_bus=b3, to_bus=b4, R=0.00075, X=0.01)

    # sys.run_pf()
