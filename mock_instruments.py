
class Thermometer():
    
    def __init__(self):
        self.T = 180.0
    
    def read_T(self):
        return self.T
    
    def change_T(self,amount):
        self.T += amount
    

class Heater():
    def __init__(self, thermometer):
        self.thermometer = thermometer
    
    def heat(self,amount=1):
        self.thermometer.change_T(amount)
    
    def chill(self,amount=1):
        self.thermometer.change_T(-amount)
