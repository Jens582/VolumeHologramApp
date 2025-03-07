import numpy as np
from typing import Iterable
from rcwa.layer_data import LayerData


class Parameter:

    dtype = np.complex128

    def __init__(self):
  
        self.lam: float = 0.5
        self.theta_deg: float = 45.0
        self.phi_deg: float = 0.0
        self.harmonic_order_x: int = 5
        self.harmonic_order_y: int = 3       

        self.t_1x: float = 2*np.pi
        self.t_1y: float = 0.0
        self.t_2x: float = 0.0
        self.t_2y: float = 2*np.pi

        self.er_ref: np.complex_ = 1.0 + (0j)
        self.er_trn: np.complex_ = 1.0 + (0j)

        self.ur_ref: np.complex_ = 1.0 + (0j)
        self.ur_trn: np.complex_ = 1.0 + (0j)

        self.layers_data: Iterable[LayerData] = []

    @property
    def k0(self) -> float:
        return 2*np.pi/self.lam
    
    @property
    def n_ref(self) -> float:
        return np.sqrt(self.er_ref*self.ur_ref)
    
    @property
    def kx_inc(self) -> float:
        theta = np.deg2rad(self.theta_deg)
        phi = np.deg2rad(self.phi_deg)
        kx = self.k0*self.n_ref*np.sin(theta)*np.cos(phi)        
        return kx
    
    @property
    def ky_inc(self) -> float:
        theta = np.deg2rad(self.theta_deg)
        phi = np.deg2rad(self.phi_deg)
        ky = self.k0*self.n_ref*np.sin(theta)*np.sin(phi)
        return ky
    
    @property
    def kz_inc(self) -> float:
        theta = np.deg2rad(self.theta_deg)
        kz = self.k0*self.n_ref*np.cos(theta)
        return kz
    
    @property
    def dim_scattering_matrix_Sij(self) -> int:
        dim_x = 2*self.harmonic_order_x+1
        dim_y =  2*self.harmonic_order_y+1
        return 2*dim_x*dim_y


