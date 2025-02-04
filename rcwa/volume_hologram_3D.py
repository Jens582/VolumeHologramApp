import numpy as np
import pandas as pd
from typing import Hashable
from rcwa.parameter import Parameter
from rcwa.layer_data import LayerData
from rcwa.calculator_scatter_matrix import calc_all_scatter_matrices_of_system
from rcwa.calculator_scatter_matrix import ScatterMatrix
from rcwa.calculator_diffraction_efficiency import calculate_efficiency_Rs_Rp_Ts_Tp
from rcwa.rcwa_help_function import build_pq_grid
from rcwa.rcwa_exception import RCWAWrongParameterError

class VolumeHologram3D():

    """
    A class for simulating a 3D volume hologram using RCWA (Rigorous Coupled Wave Analysis).

    This class constructs a volume hologram model and calculates diffraction efficiencies.

    Attributes:
    -----------
    lam : float
        Wavelength of the incident light, given in the chosen unit system. 
    theta_deg : float
        Incident angle in degrees.
    phi_deg : float
        Azimuthal angle in degrees.
    harmonic_order : int
        Maximum harmonic order for RCWA calculations.
    er_trn, ur_trn : complex
        Relative permittivity and permeability of the transmission medium.
    theta_rec1, theta_rec2 : float
        Recording angles of the hologram in degrees.
    phi_rec1, phi_rec2 : float
        Azimuthal recording angles in degrees.
    n : float
        Refractive index of the hologram material.
    dn : float
        Modulation strength of the refractive index.
    lam_hoe : float
        Wavelength used during hologram recording.
    n_z : int
        Number of layers in the z-direction.
    thickness : float
        Total thickness of the hologram, given in the chosen unit system.
    nz_steps_per_cycle : bool
        Steps in z direction for a cycle or complete thickness.
    add_ar_layer : bool
        Whether to add an anti-reflection (AR) layer.

    """

    def __init__(self):
        # System parameter
        self.lam: float = 0.5
        self.theta_deg: float = 45.0
        self.phi_deg: float = 0.0
        self.harmonic_order: int = 5
        
        self.er_trn: complex = complex(1,0)        
        self.ur_trn: complex = complex(1,0) 

        # Parameter for hologram creation 
        self.theta_rec1: float = 30.0
        self.theta_rec2: float = 20.0

        self.phi_rec1: float = 0.0
        self.phi_rec2: float = 0.0

        self.n: float = 1.5
        self.dn: float = 0.01
        self.lam_hoe: float = 0.5
    
        self.n_z: int = 101        
        self.thickness: float = 20.0
        
        self.nz_steps_per_cycle: bool = False
        self.add_ar_layer: bool = True  

        #For calculations
        self._dx: float = 1.0
        self._dy: float = 1.0
        self._dz: float = 1.0
        self._n_x: int = 101    
        self._rcwa_parameter: Parameter = None   

    @property
    def _k0_hoe(self) -> float:
        return 2*np.pi/self.lam_hoe  

    def calc_rcwa(self) -> tuple[np.ndarray]:
        """
        Computes the diffraction efficiencies of the volume hologram using RCWA.
        Returns:
        --------
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            - Rs : Reflection efficiency for s-polarization.
            - Rp : Reflection efficiency for p-polarization.
            - Ts : Transmission efficiency for s-polarization.
            - Tp : Transmission efficiency for p-polarization.
        """

        accumulated_scatter_matrices = self.get_accumulated_scatter_matrices()
        pram = self._rcwa_parameter

        # To build the device:
        # n = thickness/ periods length 
        # # n = 2**powers + rest                
        powers = self._divide_thickness_in_powers_of_two()
        device = ScatterMatrix.unity(pram.dim_scattering_matrix_Sij)
        if len(powers)!=0:
            for x in range(max(powers)+1):
                if x != 0:
                    temp = ScatterMatrix.redheffer_star_product(temp, temp)
                else:
                    temp = accumulated_scatter_matrices["full"] # one periods length    
                if x in powers:
                    device = ScatterMatrix.redheffer_star_product(device, temp)

        #-------------------------
        # rest part 
        rest = self._get_thickness_rest(powers)
        if rest is not None:
            numerical_keys = [k for k in accumulated_scatter_matrices.keys() if type(k)!=str]
            closest_key = min(numerical_keys, key=lambda k: abs(k - rest))        
            temp = accumulated_scatter_matrices[closest_key]
            device = ScatterMatrix.redheffer_star_product(device, temp)
        #----------------------------

        S_Global = self._build_S_Global(accumulated_scatter_matrices, device)
        Rs, Rp, Ts, Tp = calculate_efficiency_Rs_Rp_Ts_Tp(pram,S_Global)
        return Rs, Rp, Ts, Tp
    
    def ref_trn_dataframe(self, order_max: int) -> pd.DataFrame:
        """
        Generates a DataFrame containing reflection and transmission efficiency data.


        Parameters:
        -----------
        order_max : int
            Maximum diffraction order to include in the output.

        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the reflection and transmission efficiencies for 
            different diffraction orders. 
        """

        Rs, Rp, Ts, Tp = self.calc_rcwa()
        grid_p, grid_q = build_pq_grid(self._rcwa_parameter)

        data = dict()
        data["Order"] = grid_p.flatten()        
        data["Es"] = Rs.flatten() + Ts.flatten()
        data["Ep"] = Rp.flatten() + Tp.flatten() 
        data["Rs"] = Rs.flatten()
        data["Ts"] = Ts.flatten()
        data["Rp"] = Rp.flatten()
        data["Tp"] = Tp.flatten()

        df = pd.DataFrame(data)
        df = df[df["Order"].abs() <= order_max]        

        sum_row = df.sum()  
        df = pd.concat([pd.DataFrame([sum_row]), df], ignore_index=True)
        index = list(np.arange(len(df)-1))
        index.insert(0,"Sum")
        df.index = index

        return df

    def calc_er3D_ur3D(self) -> None:
        # coordinates are in rotated system
        mesh_x, mesh_y, mesh_z = self._calc_grid()
        modulation_n = self._get_modulation_of_n(mesh_x, mesh_y, mesh_z)
        er3D = (modulation_n**2).astype(np.complex128)        
        ur3D = np.ones(er3D.shape, dtype=np.complex128)
        return er3D, ur3D

    def get_grating_vec(self) -> np.ndarray:
        kn_rec1, kn_rec2 = self._get_kn_record()
        g = kn_rec1 - kn_rec2 
        return g 

    def get_grating_vec_rot(self):
        g = self.get_grating_vec()
        g_pre = np.sqrt(g[0]**2+g[1]**2)
        g_rot = np.array([g_pre, 0, g[2]])
        return g_rot
    
    def get_angle_coordinate_rotation(self):
        g = self.get_grating_vec()
        rad = np.arctan2(g[1],g[0])
        alpha = np.rad2deg(rad)
        return alpha

    def get_cycle_length_z_direction(self) -> float:        
        gz = np.abs(self.get_grating_vec()[2])
        return 2*np.pi/gz
    
    def get_accumulated_scatter_matrices(self) -> dict[Hashable, ScatterMatrix]:
        """
        Accumulate all scatter matrices.
        S[length_i] = S_0 * S_1 *....* S_i. * Redheffer Star Product
        """
        self._build_rcwa_pram()
        pram = self._rcwa_parameter
        scatter_matrices_of_system = self._calc_scatter_matrices_of_system(pram)
        scatter_matrices_per_length: dict[Hashable, ScatterMatrix] = dict()
        scatter_matrices_per_length["S_ref"] = scatter_matrices_of_system["S_ref"]
        scatter_matrices_per_length["S_trn"] = scatter_matrices_of_system["S_trn"]
        scatter_matrices_per_length["ar"] = scatter_matrices_of_system["ar"]
        dimS = pram.dim_scattering_matrix_Sij
        device = ScatterMatrix.unity(dimS)
        length = 0.0        
        scatter_matrices_per_length[length] = device
        for i in range(self.n_z):               
            s_next = scatter_matrices_of_system[i]
            device = ScatterMatrix.redheffer_star_product(device, s_next)
            length += self._dz            
            scatter_matrices_per_length[length] = device
        
        scatter_matrices_per_length["full"] = device 
        return scatter_matrices_per_length


    def _build_rcwa_pram(self) -> None:
        rcwa_pram: Parameter = Parameter()
        rcwa_pram.lam = self.lam        
        rcwa_pram.theta_deg = self.theta_deg
        #Rotate the system, so that gy = 0
        alpha = self.get_angle_coordinate_rotation()
        rcwa_pram.phi_deg = self.phi_deg-alpha
        rcwa_pram.harmonic_order_x = self.harmonic_order
        rcwa_pram.harmonic_order_y = 0

        grating_vec_rot = self.get_grating_vec_rot()
        rcwa_pram.t_1x = abs(grating_vec_rot[0])
        rcwa_pram.t_1y = 0.0
        rcwa_pram.t_2x = 0.0
        rcwa_pram.t_2y = 0.0

        rcwa_pram.er_ref = complex(1,0)
        rcwa_pram.ur_ref = complex(1,0)
        
        rcwa_pram.er_trn = self.er_trn
        rcwa_pram.ur_trn = self.ur_trn
        self._rcwa_parameter =  rcwa_pram

    def _divide_thickness_in_powers_of_two(self) -> list[int]:
        """
        Function for fast thickness calculation. 
        The normalized thickness is divided by a power of two, normalized to the cycle length.
        """
        if not self.nz_steps_per_cycle:
            return [0]
        grating_vec = self.get_grating_vec()
        length =abs( 2*np.pi/grating_vec[2])
        thickness = self.thickness
        n=int(thickness/length)
        powers = list()
        if n==0:
            return powers
        more = True
        while more:
            x = int(np.log2(n))
            powers.append(x)
            n-= 2**x
            if n == 0:
                more = False                
        return sorted(powers)

    def _get_thickness_rest(self, powers: list[int]) -> float:        
        if not self.nz_steps_per_cycle:
            return None
        grating_vec = self.get_grating_vec()
        length =abs( 2*np.pi/grating_vec[2])
        rest = self.thickness - (2**np.array(powers)).sum()*length
        return rest

    def _calc_scatter_matrices_of_system(self, pram: Parameter) -> dict[Hashable, ScatterMatrix]:
        er3D, ur3D = self.calc_er3D_ur3D()      
        layers_data: list[LayerData] = list()
        for i in range(self.n_z):
            data = LayerData(er3D[:,:,i], ur3D[:,:,i], self._dz, i)
            layers_data.append(data)
        layers_data.append(self._anti_reflex_layer(pram))
        pram.layers_data = layers_data      
        scatter_matrices_of_system = calc_all_scatter_matrices_of_system(pram)      
        return scatter_matrices_of_system

    def _get_modulation_of_n(self, grid_x, grid_y, grid_z) -> np.ndarray:
        g = self.get_grating_vec_rot()
        gx = g[0]
        gy = g[1]
        gz = g[2]        
        arg = grid_x*gx + grid_y*gy + grid_z*gz
        cos = np.cos(arg)
        modulation = (1+cos)*0.5
        modulation = cos
        return modulation*self.dn+self.n
       
    def _get_kn_record(self) -> tuple[np.ndarray]:
        k_rec1, k_rec2 = self._get_k0_record()
        kn = self.n*self._k0_hoe
        kz_rec1 = np.sqrt(kn**2 - k_rec1[0]**2- k_rec1[1]**2)*np.sign(k_rec1[2])
        kz_rec2 = np.sqrt(kn**2 - k_rec2[0]**2- k_rec2[1]**2)*np.sign(k_rec2[2])
        kn_rec1 = np.array([k_rec1[0], k_rec1[1], kz_rec1])
        kn_rec2 = np.array([k_rec2[0], k_rec2[1], kz_rec2])
        return kn_rec1, kn_rec2

    def _get_k0_record(self)-> tuple[np.ndarray]:
        theta_rec1_rad = np.deg2rad(self.theta_rec1)
        theta_rec2_rad = np.deg2rad(self.theta_rec2)

        phi_rec1_rad = np.deg2rad(self.phi_rec1)
        phi_rec2_rad = np.deg2rad(self.phi_rec2)

        k_ref = np.array([
            np.sin(theta_rec1_rad)*np.cos(phi_rec1_rad),
            np.sin(theta_rec1_rad)*np.sin(phi_rec1_rad),
            np.cos(theta_rec1_rad)
            ])*self._k0_hoe
        
        k_obj = np.array([
            np.sin(theta_rec2_rad)*np.cos(phi_rec2_rad),
            np.sin(theta_rec2_rad)*np.sin(phi_rec2_rad),
            np.cos(theta_rec2_rad)
            ])*self._k0_hoe
        
        return k_ref, k_obj
    
    def _set_spacing_of_grids_rot_system(self) -> None:
        g_rot = self.get_grating_vec_rot()
        #-------------------------------------------
        if abs(g_rot[0]) < 10E-8:
            self._n_x = 3
            self.dx = 100*self.lam/self._n_x
        else:
            self._n_x = 101
            l = abs(2*np.pi/g_rot[0])
            self._dx = l/self._n_x
        
        if abs(g_rot[1]) > 10E-8:
            raise RCWAWrongParameterError("Grating vector in y-direction is too big", "Rotation of coordinate system failed")
            
        #-------------------------------------------
        if self.nz_steps_per_cycle:
            if abs(g_rot[2]) < 10E-8:
                raise RCWAWrongParameterError("Grating vector in z-direction is too small", "Do not set nz_steps_per_cycle")
            l = abs(2*np.pi/g_rot[2])
            self._dz = l/self.n_z            
        else:
            self._dz = self.thickness/self.n_z
       
    def _calc_grid(self) -> tuple[np.ndarray]:
        self._set_spacing_of_grids_rot_system()
        x = np.arange(self._n_x)*self._dx
        y = np.arange(3)*self.lam*100
        z = np.arange(self.n_z)*self._dz
        mesh_x, mesh_y, mesh_z = np.meshgrid(x,y,z)
        return mesh_x, mesh_y, mesh_z
    
    def _anti_reflex_layer(self, pram: Parameter) -> LayerData:
        n_ar = np.sqrt(self.n)
        theta = np.deg2rad(pram.theta_deg)
        sin_ar = np.sin(theta)/n_ar
        cos_ar = np.sqrt(1-sin_ar**2)
        l = self.lam_hoe/(4*n_ar*cos_ar)
        layer = LayerData((n_ar**2+(0j)), 1.0+(0j), l, "ar")
        return layer

    def _build_S_Global(self, scatter_matrices_per_length: dict[Hashable, ScatterMatrix], device: ScatterMatrix) -> ScatterMatrix:
        S_ref = scatter_matrices_per_length["S_ref"]
        S_trn = scatter_matrices_per_length["S_trn"]
        S_ar = scatter_matrices_per_length["ar"]
        
        if self.add_ar_layer:
            device = ScatterMatrix.redheffer_star_product(device, S_ar)
            device = ScatterMatrix.redheffer_star_product(S_ar, device)
            
        device = ScatterMatrix.redheffer_star_product(device, S_trn)
        S_Global = ScatterMatrix.redheffer_star_product(S_ref, device)
        return S_Global

    
        

            
        
    
        

    


    