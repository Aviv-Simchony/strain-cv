import pandas as pd
from scipy import interpolate
import numpy as np

class Thermometer():
    INSTRUMENT_NAME = "MODEL 2400"
    def __init__(self,rm, gpib_addr = "02"): #TODO Make me more generic
        self.manager = rm.open_resource('GPIB0::' + gpib_addr + '::INSTR')
        if self.INSTRUMENT_NAME not in self.manager.query('*IDN?'):
            raise(self.INSTRUMENT_NAME +" not detected in address: " + gpib_addr)
        self.manager.write(":configure:resistance")
        A = 3.9083e-3
        B = -5.775e-7
        C = -4.183e-12
        R0 = 1e3
        ts_table = np.linspace(-273,100,5000)
        rs_table = R0*(1+A*ts_table+B*ts_table**2+C*(ts_table-100)*ts_table**3)
        self.table = interpolate.interp1d(rs_table, ts_table, fill_value='extrapolate')
        
#set measurement to auto range and auto decide what current to source
        self.manager.write(":resistance:range:AUTO 1")
        self.manager.write(":resistance:MODE AUTO")
    
    def read_T(self):
        reading = self.manager.query(':measure:resistance?')
        R = float(reading.split(',')[2])
        return self.translate_T(R)
    
    def translate_T(self,R):
        return self.table(R)+273

class Heater():
    INSTRUMENT_NAME = "MODEL 2410"
    def __init__(self,rm,gpib_addr = "01"):
        self.manager = rm.open_resource('GPIB0::' + gpib_addr + '::INSTR')
        if self.INSTRUMENT_NAME not in self.manager.query('*IDN?'):
            raise(self.INSTRUMENT_NAME +" not detected in address: " + gpib_addr)
        self.manager.write(":configure:voltage")
        self.manager.write(":source:function:mode current")
    
    def heat(self,current):
        self.manager.write(":source:current:level:immediate:amplitude " + str(current))
        self.manager.query(':measure:voltage?')