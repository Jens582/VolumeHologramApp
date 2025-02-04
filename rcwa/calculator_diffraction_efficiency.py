import numpy as np
from numpy.linalg import inv
from typing import Optional

from rcwa.scatter_matrix import ScatterMatrix
from rcwa.parameter import Parameter
from rcwa.rcwa_help_function import build_kz_norm_ref_trn, build_kxy_norm, build_pq_grid


def calculate_efficiency_Rs_Rp_Ts_Tp(pram: Parameter, S_global: ScatterMatrix) -> tuple[np.ndarray]:
    """
    Computes the diffraction efficiency from the global scatter matrix (S_global) of a system.


    Parameters:
    -----------
    pram : Parameter
        An instance of the Parameter class containing the system's physical properties 
        such as refractive indices, angles, and wave vectors.
    S_global : ScatterMatrix
        An instance of the ScatterMatrix class representing the global scatter matrix of the system.

    Returns:
    --------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        - Rs : np.ndarray
            2D array representing the reflection efficiency for S-polarization (in percentage).
        - Rp : np.ndarray
            2D array representing the reflection efficiency for P-polarization (in percentage).
        - Ts : np.ndarray
            2D array representing the transmission efficiency for S-polarization (in percentage).
        - Tp : np.ndarray
            2D array representing the transmission efficiency for P-polarization (in percentage).
    """        
    calculator = _CalculatorDiffractionEfficiency(pram, S_global)
    calculator.calc_efficiency()
    return calculator.Rs, calculator.Rp, calculator.Ts, calculator.Tp


class _CalculatorDiffractionEfficiency:

    def __init__(self, pram: Parameter, S_global: ScatterMatrix):
        self.pram: Parameter = pram
        self.S_global: ScatterMatrix = S_global

        self.Rs: Optional[np.ndarray] = None
        self.Rp: Optional[np.ndarray] = None
        self.Ts: Optional[np.ndarray] = None
        self.Tp: Optional[np.ndarray] = None

        kzn_ref, kzn_trn = build_kz_norm_ref_trn(pram)

        self.kzn_ref: np.ndarray = kzn_ref 
        self.kzn_trn: np.ndarray = kzn_trn 
    
    def calc_efficiency(self) -> None:
        # sx_i, sy_i are the incident electric field for i = S,P 
        sx_s, sy_s = self._calc_sx_sy_for_s_pol()
        sx_p, sy_p = self._calc_sx_sy_for_p_pol()
        Rs_vec, Ts_vec = self._calc_efficiency(sx_s, sy_s)
        Rp_vec, Tp_vec = self._calc_efficiency(sx_p, sy_p)
        self._reshape_ref_trn_into_grid( Rs_vec, Rp_vec, Ts_vec, Tp_vec)

    def _reshape_ref_trn_into_grid(self, Rs_vec, Rp_vec, Ts_vec, Tp_vec) -> None:
        grid_p, grid_q = build_pq_grid(self.pram)
        shape = grid_p.shape
        
        self.Rs = 100*Rs_vec.reshape(shape)
        self.Rp = 100*Rp_vec.reshape(shape)
        self.Ts = 100*Ts_vec.reshape(shape)
        self.Tp = 100*Tp_vec.reshape(shape)

    def _calc_efficiency(self, sx: np.ndarray, sy: np.ndarray) -> tuple[np.ndarray]:
        kxn, kyn = build_kxy_norm(self.pram)
        dim = kxn.shape[0]
        i_x = int((dim-1)/2)
        i_y = i_x + dim
        S = self.S_global                

        c_inc = np.zeros((2*dim,1) , dtype=Parameter.dtype)
        c_inc[i_x] = sx
        c_inc[i_y] = sy

        c_ref = S.S11 @ c_inc
        c_trn = S.S21 @ c_inc

        rx = c_ref[:dim,0]
        ry = c_ref[dim:,0]

        tx = c_trn[:dim,0]
        ty = c_trn[dim:,0]

        kzn_ref = self.kzn_ref
        kzn_trn = self.kzn_trn

        rz = -inv(kzn_ref) @ ( (kxn @ rx) + (kyn @ ry) )
        tz = -inv(kzn_trn) @ ( (kxn @ tx) + (kyn @ ty) )

        R_temp = np.abs(rx)**2 + np.abs(ry)**2 + np.abs(rz)**2
        T_temp = np.abs(tx)**2 + np.abs(ty)**2 + np.abs(tz)**2

        up = -(kzn_ref/self.pram.ur_ref).real
        kzn_inc = self.pram.kz_inc/self.pram.k0 
        down = (kzn_inc/self.pram.ur_ref).real
        pre = up/down
        R = pre @ R_temp

        up = (kzn_trn/self.pram.ur_trn).real
        kzn_inc = self.pram.kz_inc/self.pram.k0 
        down = (kzn_inc/self.pram.ur_ref).real
        pre = up/down
        T = pre @ T_temp
        return R, T
   
    def _rot_matrix_z(self) -> np.ndarray:
        phi = self.pram.phi_deg
        phi_rad = np.deg2rad(phi)
        cos = np.cos(phi_rad)
        sin = np.sin(phi_rad)
        rot = np.eye(3)
        rot[0,0] = cos
        rot[1,1] = cos
        rot[0,1] = -sin
        rot[1,0] = sin
        return rot

    def _calc_sx_sy_for_p_pol(self) -> tuple[float]:
        """
        Calculate the electric field for P polarization
        """
        theta = self.pram.theta_deg
        theta_rad = np.deg2rad(theta)
        cos = np.cos(theta_rad)
        sin = np.sin(theta_rad)
        vec = np.zeros((3,1))
        vec[0,0] = cos
        vec[2,0] = sin
        rot = self._rot_matrix_z()
        vec_rot = rot @ vec
        return vec_rot[0,0] , vec_rot[1,0]

    def _calc_sx_sy_for_s_pol(self) -> tuple[float]:
        """
        Calculate the electric field for S polarization
        """
        theta = self.pram.theta_deg
        theta_rad = np.deg2rad(theta)
        cos = np.cos(theta_rad)
        sin = np.sin(theta_rad)
        vec = np.zeros((3,1))
        vec[1,0] = 1.0
        
        rot = self._rot_matrix_z()
        vec_rot = rot @ vec
        return vec_rot[0,0], vec_rot[1,0]





