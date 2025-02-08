import numpy as np
from typing import Union

from source.parameter_controller import ParameterControl
from source.data_container import DataContainer


from rcwa.volume_hologram_3D import VolumeHologram3D
from rcwa.hoe_thickness_dependence import HOEThicknessDependence


class HoeInLoop:
    """
    Manages the execution of holographic optical element (HOE) simulations in a loop.

    This class determines whether the simulation should be run with `VolumeHologram3D`
    or `HOEThicknessDependence`, initializes parameters, and computes diffraction efficiencies.
    """

    def __init__(self, parameter_control: ParameterControl):
        self.parameter_control: ParameterControl = parameter_control
        self.current_variable: str = parameter_control.current_variable
        self.dimX: int = 0
        self.dimY: int = 0
        self._hoe_parameters = parameter_control.hoe_parameters
        
        self._hoe: Union[VolumeHologram3D, HOEThicknessDependence] = None
        self._is_HOEThicknessDependence: bool = None
        
        self._set_hoe()
        self._fill_parameter_to_hoe()

    def get_start_value_container(self) -> DataContainer:        
        if not self._is_HOEThicknessDependence:
            variable = self.parameter_control.get_current_variable_values()
        else:
            thickness, max_steps, _ = self.parameter_control.get_variable_range(self.current_variable)
            one_cycle_length = self._hoe.get_cycle_length_z_direction()
            steps = self._hoe.get_cycle_count_for_thickness(thickness)
            variable = (np.arange(steps+1))*one_cycle_length                                
            self._hoe.initialize_cycle_calculation(thickness, max_steps)
        
        dimX = int(2*self._hoe.harmonic_order+1)
        dimY = 1
        dimZ = len(variable)
        self.dimX = dimX
        self.dimY = dimY

        text = self._get_parameter_text()
        pram_variable = self.current_variable
        data = DataContainer.create_empty(dimX, dimY, dimZ, variable, text, pram_variable)
        return data
    

    def get_Rs_Rp_Ts_Tp(self, value):    
        if self._is_HOEThicknessDependence:
            return self._get_Rs_Rp_Ts_Tp_HOEThicknessDependence(value)
        else:
            return self._get_Rs_Rp_Ts_Tp_VolumeHologram3D(value)
    
    def _get_error_values(self):
        error_value = np.full((self.dimY, self.dimX), np.nan)
        return error_value, error_value, error_value, error_value

    def _get_Rs_Rp_Ts_Tp_HOEThicknessDependence(self, value):        
        l, Rs, Rp, Ts, Tp = self._hoe.compute_next_cycle_efficiency()
        if abs(l-value) > 10E-8:            
            raise Exception("Wrong value!?")
        return Rs, Rp, Ts, Tp
    
    def _get_Rs_Rp_Ts_Tp_VolumeHologram3D(self, value):
        pram = self._hoe_parameters[self.current_variable]
        name = pram.attribute_name
        setattr(self._hoe, name, value)
        Rs, Rp, Ts, Tp = self._hoe.calc_rcwa()
        return Rs, Rp, Ts, Tp
        
        
    def _set_hoe(self):        
        if self.current_variable in ["cycles_thickness"]:
             self._hoe = HOEThicknessDependence()             
             self._is_HOEThicknessDependence = True             
        else:            
            self._hoe = VolumeHologram3D()
            self._is_HOEThicknessDependence = False

    def _fill_parameter_to_hoe(self):
        for item in self._hoe_parameters.items():
              key = item[0]
              value = item[1].value
              name = item[1].attribute_name
              if name is not None:                
                if not hasattr(self._hoe, name):
                    raise Exception("HOE as no parameter with name: " + name)
                else:
                     setattr(self._hoe, name, value)
        
    def _get_parameter_text(self):
        text = ""
        text = "Variable parameter: " + self.current_variable+"\n"
        pram_current = self._hoe_parameters[self.current_variable]
        start = pram_current.start
        end = pram_current.end
        steps = pram_current.steps

        label_start = pram_current.label_start
        label_end = pram_current.label_end
        label_steps = pram_current.label_steps

        text += f"{label_start}: {start}, {label_end}: {end}, {label_steps}: {steps}\n"
        for item in self._hoe_parameters.items():
              key = item[0]
              value = item[1].value
              name = item[1].attribute_name
              if name is not None:
                  text_pram = name+f": {value}\n"
                  text+= text_pram
        return text


  
        
        