import numpy as np
from typing import Union, Optional, Hashable

from numpy.fft import fft2, fftshift
from numpy.linalg import inv
from scipy.linalg import expm

from rcwa.parameter import Parameter
from rcwa.layer_data import LayerData
from rcwa.scatter_matrix import ScatterMatrix
from rcwa.rcwa_help_function import build_pq_grid, build_kxy_norm

from rcwa.rcwa_exception import RCWAError


def calc_all_scatter_matrices_of_system(pram: Parameter) -> dict[Hashable, ScatterMatrix]:
    """
    Computes all scatter matrices for a given system.

    This function iterates over all layers defined in `pram.layers_data` and constructs the scatter 
    matrices for each layer. Additionally, the function computes the scatter matrices 
    for the reflection and transmission layers.

    Parameters:
    -----------
    pram : Parameter
        An instance of the `Parameter` class containing all system parameters, 
        including material properties and wave parameters.

    Returns:
    --------
    dict[Hashable, ScatterMatrix]
        A dictionary where the keys correspond to the layer identifiers 
        (including "S_ref" for reflection and "S_trn" for transmission) and 
        the values are instances of the `ScatterMatrix` class representing 
        the computed scatter matrices.

    """
    system_data = _ScatterMatrixSystemData(pram)
    V0, W0 = _eigen_vectors_vacuum_V0_W0(system_data)
    scatter_matrices_of_system = dict()  

    for data in pram.layers_data:
        eigen = _EigenValuesVectors(data, system_data)
        eigen.build_me()
        S = _build_scatter_matrix_inside_vacuum(eigen, V0, W0)
        scatter_matrices_of_system[data.identifier] = S
        del eigen

    S_ref, S_trn = _calculate_scatter_ref_trn(system_data, V0, W0)
    scatter_matrices_of_system["S_ref"] = S_ref
    scatter_matrices_of_system["S_trn"] = S_trn
    return scatter_matrices_of_system


class _ScatterMatrixSystemData:
    """
    Internal class that stores precomputed system data for scatter matrix calculations.
    """

    def __init__(self, pram: Parameter):
        self.pram: Parameter = pram

        self.grid_p: Optional[np.ndarray] = None
        self.grid_q: Optional[np.ndarray] = None

        self.kxn: Optional[np.ndarray] = None
        self.kyn: Optional[np.ndarray] = None
        self._fill_data()

    def _fill_data(self):
        pram = self.pram
        
        grid_p, grid_q = build_pq_grid(pram)
        self.grid_p: np.ndarray = grid_p
        self.grid_q: np.ndarray = grid_q

        kxn, kyn = build_kxy_norm(pram)
        self.kxn: np.ndarray = kxn
        self.kyn: np.ndarray = kyn
                

class _EigenValuesVectors:
    """
    Computes eigenvalues and eigenvectors for a given layer in the system.
    """

    def __init__(self, data: LayerData, system_data: _ScatterMatrixSystemData):
        self.system_data: _ScatterMatrixSystemData = system_data
        self.er: Union[np.complex_, np.ndarray] = data.er
        self.ur: Union[np.complex_, np.ndarray] = data.ur
        self.Li:float = data.Li
        
        self.erc: Optional[np.ndarray] = None
        self.urc: Optional[np.ndarray] = None

        self.Q: Optional[np.ndarray] = None
        self.P: Optional[np.ndarray] = None
        self.Omega2: Optional[np.ndarray] = None

        self.W: Optional[np.ndarray] = None
        self.V: Optional[np.ndarray] = None
        self.Lam: Optional[np.ndarray] =None
        self.arg: Optional[np.ndarray] = None

    def build_me(self) -> None:        
        self._build_convolution_matrices()        
        self._build_Q_P_Omega2()        
        self._build_V_W_Lam()

    def _build_convolution_matrices(self) -> None:
        self.erc = self._build_convolution_matrix_from_er_ur(self.er)
        self.urc = self._build_convolution_matrix_from_er_ur(self.ur)

    def _build_convolution_matrix_from_er_ur(self,e_or_mu) -> np.ndarray:
        system_data = self.system_data
        if type(e_or_mu) is not np.ndarray:
            return np.eye(system_data.kxn.shape[0], dtype=system_data.pram.dtype)*e_or_mu
        dim = e_or_mu.shape[0]*e_or_mu.shape[1]
        spec = fftshift(fft2(e_or_mu))/dim
        ps = system_data.grid_p.flatten()
        qs = system_data.grid_q.flatten()
        total = len(ps)
        convolution_matrix = np.zeros((total, total), dtype=system_data.pram.dtype)
        for n in range(total):
            p = ps[n]
            q = qs[n]
            vec = self._get_row_from_spectrum_for_convolution(spec, p, q)
            convolution_matrix[n, :] = vec
        return convolution_matrix

    def _get_row_from_spectrum_for_convolution(self, spectrum: np.ndarray, p:int, q:int) -> np.ndarray:
            system_data = self.system_data
            shape = spectrum.shape
            mx = int((shape[1]-1)/2)
            my = int((shape[0]-1)/2)

            sy = int(my+ q - system_data.pram.harmonic_order_y)
            sx = int(mx+ p - system_data.pram.harmonic_order_x)

            ey = int(my+ q + system_data.pram.harmonic_order_y+1)
            ex = int(mx+ p + system_data.pram.harmonic_order_x+1)

            return spectrum[sy:ey, sx:ex].flatten()[::-1]

    def _build_Q_P_Omega2(self) -> None:
        system_data = self.system_data
        erc_inv = inv(self.erc)
        urc_inv = inv(self.urc)
        
        q00 = system_data.kxn @ urc_inv @ system_data.kyn
        q01 = self.erc - (system_data.kxn @ urc_inv @ system_data.kxn)
        q10 = (system_data.kyn @ urc_inv @ system_data.kyn) - self.erc
        q11 = -system_data.kyn @ urc_inv @ system_data.kxn

        p00 = system_data.kxn @ erc_inv @ system_data.kyn
        p01 = self.urc - (system_data.kxn @ erc_inv @ system_data.kxn)
        p10 = (system_data.kyn @ erc_inv @ system_data.kyn) - self.urc
        p11 = -system_data.kyn @ erc_inv @ system_data.kxn

        Q = _combine_matrix(q00, q01, q10, q11) 
        P = _combine_matrix(p00, p01, p10, p11)
        Omega2 = P @ Q
        
        self.Q = Q
        self.P = P
        self.Omega2 = Omega2
        
    def _build_V_W_Lam(self) -> None:
        dia = np.diagonal(self.Omega2)    
        temp = self.Omega2.copy()
        dim = len(dia) 
        np.fill_diagonal(temp, np.zeros((dim, dim), dtype=Parameter.dtype))
        if (np.abs(temp).sum()) < 10E-8:
            eigenvalues = dia
            #check for zero
            dia_abs = np.abs(dia)
            zero = np.any(dia_abs < 10E-9)
            if zero:
                raise RCWAError("KZ is zero", "Change incident angle or grating")
            W = np.eye(dim, dtype=Parameter.dtype)             
        else:
            eigenvalues, W = np.linalg.eig(self.Omega2)
        lam_dia = np.sqrt(eigenvalues)
        Lam = np.zeros((dim, dim), dtype=Parameter.dtype)
        np.fill_diagonal(Lam, lam_dia)
        Lam_inv = inv(Lam)
        V = self.Q @ W @ Lam_inv

        self.W = W
        self.V = V
        self.Lam = Lam
        Li = self.Li
        k0 = self.system_data.pram.k0
        arg = -Lam*k0*Li
        self.arg = arg
    
def _build_scatter_matrix_inside_vacuum(eigen: _EigenValuesVectors, V0:np.ndarray, W0: np.ndarray) -> ScatterMatrix:
    """
    Computes the scatter matrix for a layer inside a vacuum.
    """
    Wi = eigen.W
    Vi = eigen.V
    Li = eigen.Li
    arg = eigen.arg

    Wi_inv = inv(Wi)
    Vi_inv = inv(Vi)

    A = (Wi_inv @ W0) + (Vi_inv @ V0)
    B = (Wi_inv @ W0) - (Vi_inv @ V0)
    A_inv = inv(A)

    X = expm(arg)

    Mul = inv(A - (X @ B @ A_inv @ X @ B))
    S11_Second = (X @ B @ A_inv @ X @ A) - B
    S12_Second = X @ (A - (B @ A_inv @ B) )

    S11 = Mul @ S11_Second
    S12 = Mul.copy() @ S12_Second
    S = ScatterMatrix()
    S.S11 = S11
    S.S12 = S12
    S.S22 = S11
    S.S21 = S12
    return S
     

def _eigen_vectors_vacuum_V0_W0(system_data: _ScatterMatrixSystemData) -> tuple[np.ndarray]:
    
    """
    Computes the eigenvectors for the vacuum reference layer.
    """

    er = 1.0 + (0.0j) 
    ur = 1.0 + (0.0j) 
    Li = 1.0
    data: LayerData = LayerData(er, ur, Li, "vac")
    
    eigen = _EigenValuesVectors(data, system_data)
    eigen.build_me()
    V0 = eigen.V
    W0 = eigen.W
    return V0, W0
    

def _calculate_scatter_ref_trn(system_data: _ScatterMatrixSystemData, V0:np.ndarray, W0: np.ndarray) -> tuple[ScatterMatrix]:        
    """
    Computes the scatter matrices for the reflection and transmission regions.

    This function calculates the scatter matrices for the top (reflection) and 
    bottom (transmission) interfaces of the system

    """
    er_ref = system_data.pram.er_ref
    ur_ref = system_data.pram.ur_ref
    Li_ref = 1.0
    data_ref = LayerData(er_ref, ur_ref, Li_ref, "ref")
    
    er_trn = system_data.pram.er_trn
    ur_trn = system_data.pram.ur_trn
    Li_trn = 1.0
    data_trn = LayerData(er_trn, ur_trn, Li_trn, "trn")        

    eigen_ref = _EigenValuesVectors(data_ref, system_data)
    eigen_ref.build_me()

    eigen_trn = _EigenValuesVectors(data_trn, system_data)
    eigen_trn.build_me()

    V_ref = eigen_ref.V
    W_ref = eigen_ref.W 
    V_trn = eigen_trn.V
    W_trn = eigen_trn.W 

    V0_inv = inv(V0)
    W0_inv = inv(W0)

    A_ref = (W0_inv @ W_ref) + (V0_inv @ V_ref)
    B_ref = (W0_inv @ W_ref) - (V0_inv @ V_ref)
    A_ref_inv = inv(A_ref)

    A_trn = (W0_inv @ W_trn) + (V0_inv @ V_trn)
    B_trn = (W0_inv @ W_trn) - (V0_inv @ V_trn)
    A_trn_inv = inv(A_trn)

    S_ref = ScatterMatrix()
    S_ref.S11 = - (A_ref_inv @ B_ref)
    S_ref.S12 = 2*A_ref_inv 
    S_ref.S21 = 0.5 * ( A_ref - (B_ref @ A_ref_inv @ B_ref) )
    S_ref.S22 = B_ref @ A_ref_inv

    S_trn = ScatterMatrix()
    S_trn.S11 = B_trn @ A_trn_inv 
    S_trn.S12 = 0.5 * (A_trn - (B_trn @ A_trn_inv @ B_trn))
    S_trn.S21 = 2 * A_trn_inv
    S_trn.S22 = - (A_trn_inv @ B_trn)

    return S_ref, S_trn
    

def _combine_matrix(a00: np.ndarray, a01: np.ndarray, a10: np.ndarray, a11: np.ndarray) -> np.ndarray:
    ab = np.hstack((a00,a01))
    cd = np.hstack((a10,a11))
    return np.vstack((ab,cd))
    
