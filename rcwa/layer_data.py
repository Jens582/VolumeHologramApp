import numpy as np
from typing import Union, Hashable
from rcwa.rcwa_exception import RCWAWrongParameterError

class LayerData:

    def __init__(self,
                 er: Union[np.complex128, np.ndarray], 
                 ur: Union[np.complex128, np.ndarray],
                 Li: float,
                 identifier: Hashable):
        
        if type(er) == np.ndarray:
            dimx = er.shape[1]
            dimy = er.shape[0]
            if ((dimx %  2) == 0) or ((dimy %  2) == 0):
                raise RCWAWrongParameterError("Dimensions of er and ur must be odd!", "Set nx and ny odd")

        self.er: Union[np.complex_, np.ndarray] = er
        self.ur: Union[np.complex_, np.ndarray] = ur
        self.Li: float = Li
        self.identifier: Hashable = identifier 