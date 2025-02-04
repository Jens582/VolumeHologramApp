import numpy as np
from numpy.linalg import inv
from rcwa.parameter import Parameter

class ScatterMatrix:

    def __init__(self):
        self.S11: np.ndarray = None
        self.S12: np.ndarray = None
        self.S21: np.ndarray = None
        self.S22: np.ndarray = None

    def clone_me(self) -> "ScatterMatrix":
        clone = ScatterMatrix()
        clone.S11 = np.copy(self.S11)
        clone.S12 = np.copy(self.S12)
        clone.S21 = np.copy(self.S21)
        clone.S22 = np.copy(self.S22)
        return clone

    @staticmethod
    def redheffer_star_product(SA: "ScatterMatrix", SB: "ScatterMatrix") -> "ScatterMatrix":
        dim = SA.S11.shape[0]
        I = np.eye(dim, dtype=Parameter.dtype)       
        SAB = ScatterMatrix()
        
        
        bracket_1 = inv(I - (SB.S11 @ SA.S22))
        bracket_2 = inv(I - (SA.S22 @ SB.S11))
        #SAB11        
        second = SA.S12 @ bracket_1 @ (SB.S11 @ SA.S21)
        SAB.S11 = SA.S11 + second

        #SAB12 
        SAB.S12 = SA.S12 @ bracket_1 @ SB.S12

        #SAB21
        SAB.S21 = SB.S21 @ bracket_2 @ SA.S21

        #SAB22
        second = SB.S21 @ bracket_2 @ (SA.S22 @ SB.S12)
        SAB.S22 = SB.S22 + second

        return SAB
    
    @staticmethod
    def unity(dim_Sij: int) -> "ScatterMatrix":
        S = ScatterMatrix()
        S.S11 = np.zeros((dim_Sij, dim_Sij), dtype=Parameter.dtype)
        S.S21 = np.eye(dim_Sij, dtype=Parameter.dtype)
        S.S12 = np.eye(dim_Sij, dtype=Parameter.dtype)
        S.S22 = np.zeros((dim_Sij, dim_Sij), dtype=Parameter.dtype)
        return S


