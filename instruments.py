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
        calib = pd.read_csv('C:/Users/PPMS_J/Documents/Data/Bai/python_experiment_procedure/in-situ-strain-control/rt_thermometer-rxx-10ua_heater-rxx-10ua.dat', sep='\t')
        R = calib['Bridge 1 Resistance (ohms)']
        T = calib['Temperature (K)']
        calib_func = interpolate.interp1d(T,R,fill_value='extrapolate')
        ts = np.linspace(180,300,2000)
        self.translate_T = interpolate.interp1d(calib_func(ts), ts)
#set measurement to auto range and auto decide what current to source
        self.manager.write(":resistance:range:AUTO 1")
        self.manager.write(":resistance:MODE AUTO")
    
    def read_T(self):
        reading = self.manager.query(':measure:resistance?')
        R = float(reading.split(',')[2])
        if R < 4e6:
            return self.translate_T(R)
        else:
            return 180

class Heater():
    INSTRUMENT_NAME = "MODEL 2410"
    def __init__(self,rm,gpib_addr = "01"):
        self.manager = rm.open_resource('GPIB0::' + gpib_addr + '::INSTR')
        if self.INSTRUMENT_NAME not in self.manager.query('*IDN?'):
            raise(self.INSTRUMENT_NAME +" not detected in address: " + gpib_addr)
        self.manager.write(":configure:voltage")
#set range and compliance
        self.manager.write(":voltage:range maximum")
        self.manager.write(":source:function:mode current")
        self.manager.write(":source:current:range maximum")
    
    def heat(self,current):
        self.manager.write(":source:current:level:immediate:amplitude " + str(current))