from math import pi, sin
import matplotlib.pyplot as plt
import numpy as np

class psu_mock:
    def __init__(self, resistance, voltage):
        self.resistance = resistance
        self.voltage = voltage
        self.w = 0.1*pi
        self.rng = np.random.default_rng()
    
    def get_voltage(self, t):
        return self.voltage*sin(self.w*t)+self.rng.normal(loc=0, scale=10)
    def get_current(self, t):
        return self.get_voltage(t)/self.resistance
    
    def graph(self):
        time_space = np.arange(0, 100, 0.1)
        plt.plot(time_space, list(map(lambda x: self.get_voltage(x), time_space)) )
        plt.plot(time_space, list(map(self.get_current, time_space)))
        plt.show()
    
class Filter:
    def __init__(self, initial_value):
        n = 5
        self.initial_value = initial_value
        self.h = np.empty([n, n])
        self.k = np.empty([n, n])
        self.xk = np.empty([n, n])
    
    # def xhat_k(y):
    #     self.xk+self.k(y-self.h*self.x)
    
if __name__ == "__main__":
    print("Creating PSU")
    psu = psu_mock(10, 110)
    psu.graph()