import numpy as np

class Parameter:
    """
    Base class for HOE simulation parameters.

    This class represents a numerical parameter with an adjustable range and step size.
    It supports setting value constraints (`v_min`, `v_max`), formatting labels, 
    and generating evenly spaced variable values for simulations.

    """


    def __init__(self, value):
        self._value = value
        self.start = value
        self.end = value+1
        self.steps = 2
        self.name_hoe = None
        self.is_variable = True
        self.is_data_table = True

        self.v_min = float("-inf")
        self.v_max = float("inf") 

        self.label_start = "Start"           
        self.label_end = "End"           
        self.label_steps = "Steps"

        self.attribute_name = None           

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        before = self._value        
        try:            
            self._value = float(value)
            self.filter_me()            
        except:
            self._value = before
            

    def set_me(self, start, end, steps):
        before_start = self.start
        before_end = self.end
        before_steps = self.steps

        try:
            self.start = float(start)
            self.end = float(end)
            self.steps = int(steps)
            self.filter_me()
        except:
            self.start = before_start
            self.end = before_end
            self.steps = before_steps
    
    def filter_me(self):
        value = self.value
    
        if value < self.v_min:
            value = self.v_min

        if value > self.v_max:
                value = self.v_max
        
        self._value = value

        if self.start > self.end:
            v2 = self.end
            v1 = self.start
            self.start = v2
            self.end = v1

        if self.start == self.end:
            if self.end == self.v_max:  
                s = self.end -1
                e = self.start            
            else:
                s = self.start
                e = self.end+1
            self.start = s
            self.end = e
                   
        if self.start < self.v_min:
            self.start = self.v_min
        if self.end > self.v_max:
            self.end = self.v_max
        if self.steps < 2:
            self.steps = 2    
       
    def get_variable_values(self):
        return np.linspace(self.start, self.end, int(self.steps))

class ParameterInt(Parameter):

    def __init__(self, value):
        super().__init__(value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        before = self._value        
        try:
            self._value = int(value)
            self.filter_me()
        except:
            self._value = before

    def set_me(self, start, end, steps):
        before_start = self.start
        before_end = self.end
        before_steps = self.steps

        try:
            self.start = int(start)
            self.end = int(end)
            self.steps = int(steps)
            self.filter_me()
        except:
            self.start = before_start
            self.end = before_end
            self.steps = before_steps

class ParameterFloat(Parameter):

    def __init__(self, value):        
        super().__init__(value)

class ParameterBool(Parameter):

    def __init__(self, value):
        self._value = True
        self.value = value
        self.name_hoe = None
        self.is_variable = True
        self.is_data_table = True
        
        self.label_start = "Start"           
        self.label_end = "End"           
        self.label_steps = "Steps"
        self.attribute_name = None 
   
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        before = self._value
        if value in ["Yes", "yes", "Y", 1, "YES", "True", "TRUE", "true"]:
            self._value = True
            return
        if value in ["No", "no", "NO", 0,"N", "False", "FALSE", "false"]:
            self._value = False
            return
        self._value = before

    def set_me(self, start, end, steps):
        raise Exception("Not allowed as variable")

class ParameterCyclesThickness(Parameter):

    def __init__(self, value):
        super().__init__(value)
        self.is_data_table = False
        self.label_start = "Thickness"
        self.label_end = "Max Steps"
        self.label_steps = "---"
        self.start = 100.0
        self.end = 1000
        self.steps = 0

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        before = self._value
        try:
            v = int(value)
            if v < 1:
                v = 1
            self._value = 1
        except:
            self._value = before
        
    def set_me(self, start, end, steps):
        before_start = self.start
        before_end = self.end
        before_steps = self.steps
        try:
            if start < 1:
                start = 1
            if end < 2:
                end=2
            
            self.start = (start)
            self.end = int(end)
            self.steps = int(steps)
        except:
            self.start = before_start
            self.end = before_end
            self.steps = before_steps