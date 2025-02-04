import numpy as np
from typing import Hashable
import math
from rcwa.calculator_scatter_matrix import ScatterMatrix
from rcwa.calculator_diffraction_efficiency import calculate_efficiency_Rs_Rp_Ts_Tp
from rcwa.volume_hologram_3D import VolumeHologram3D
from rcwa.rcwa_exception import RCWAError
from numbers import Number

class HOEThicknessDependence(VolumeHologram3D):
    """
    Class for analyzing the efficiency dependence on the thickness of a volume holographic optical element (HOE).

    This class extends `VolumeHologram3D` and provides methods to compute diffraction efficiencies 
    for different thicknesses using Rigorous Coupled-Wave Analysis (RCWA).

    """
    def __init__(self):
        super().__init__()
        self._current_length = 0.0
        self._device: ScatterMatrix = None
        self._S_one_cycle: ScatterMatrix = None
        self._l_one_cycle:float = 0.0
        self._accumulated_scatter_matrices: dict[Hashable, ScatterMatrix] = None
        self._max_steps:int = None
        self._current_step:int = 0

    def compute_efficiency_per_step(self, nz: int, thickness: float) -> tuple[np.ndarray]:
        """
        Computes diffraction efficiencies for a volume hologram at discrete thickness steps.

        The step size is determined by `thickness / nz`. Each step represents 
        an incremental increase in thickness, and efficiencies are computed iteratively.

        Parameters:
        -----------
        nz : int
            Number of thickness steps.
        thickness : float
            Total thickness of the hologram.

        Returns:
        --------
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            - thickness_values : np.ndarray
                Array of thickness values for each step.
            - Rs_values : np.ndarray
                Reflection efficiencies for s-polarized light.
            - Rp_values : np.ndarray
                Reflection efficiencies for p-polarized light.
            - Ts_values : np.ndarray
                Transmission efficiencies for s-polarized light.
            - Tp_values : np.ndarray
                Transmission efficiencies for p-polarized light.
        """
        self.n_z = nz
        self.thickness = thickness
        self.nz_steps_per_cycle = False

        accumulated_scatter_matrices = self.get_accumulated_scatter_matrices()
        keys = accumulated_scatter_matrices.keys()

        only_numbers = sorted([num for num in keys if isinstance(num, Number)])
        dimz = len(only_numbers)
        dimx = 2*self.harmonic_order+1 
        dimy = 3

        Rs_values = np.ones((dimy, dimx, dimz), dtype=np.float32)*np.NAN
        Rp_values = np.ones((dimy, dimx, dimz), dtype=np.float32)*np.NAN
        Ts_values = np.ones((dimy, dimx, dimz), dtype=np.float32)*np.NAN
        Tp_values = np.ones((dimy, dimx, dimz), dtype=np.float32)*np.NAN

        pram = self._rcwa_parameter
        for i in range(dimz):
            num = only_numbers[i]
            next_S = accumulated_scatter_matrices[num]            
            S_global = self._build_S_Global(accumulated_scatter_matrices, next_S)
            Rs, Rp, Ts, Tp = calculate_efficiency_Rs_Rp_Ts_Tp(pram,S_global)
            Rs_values[:,:,i] = Rs 
            Rp_values[:,:,i] = Rp
            Ts_values[:,:,i] = Ts
            Tp_values[:,:,i] = Tp
        
        thickness_values = np.array(only_numbers)
        return thickness_values, Rs_values, Rp_values, Ts_values, Tp_values
    
    def compute_efficiency_per_cycle(self, thickness, max_steps=None) -> tuple[np.ndarray]:
        """
            Computes diffraction efficiencies for a volume hologram in multiples of the grating cycle length.

            The method iterates over thickness values in increments of the grating cycle length 
            until the total thickness is reached.

            Parameters:
            -----------
            thickness : float
                Total thickness of the hologram.
            max_steps : int, optional
                Maximum allowed steps in the iteration. If `None`, no step limit is applied.

            Returns:
            --------
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
                - thickness_values : np.ndarray
                    Array of thickness values for each cycle.
                - Rs_values : np.ndarray
                    Reflection efficiencies for s-polarized light.
                - Rp_values : np.ndarray
                    Reflection efficiencies for p-polarized light.
                - Ts_values : np.ndarray
                    Transmission efficiencies for s-polarized light.
                - Tp_values : np.ndarray
                    Transmission efficiencies for p-polarized light.
            """
        self.initialize_cycle_calculation(thickness, max_steps)
                
        steps = self.get_cycle_count_for_thickness(thickness) +1       

        dimx = 2*self.harmonic_order+1 
        dimy = 1 
        Rs_values = np.full((dimy, dimx, steps), np.nan, dtype=np.float32)
        Rp_values = np.full((dimy, dimx, steps), np.nan, dtype=np.float32)
        Ts_values = np.full((dimy, dimx, steps), np.nan, dtype=np.float32)
        Tp_values = np.full((dimy, dimx, steps), np.nan, dtype=np.float32)
        thickness_values = np.full(steps, np.nan, dtype=np.float32)         

        for i in range(steps):
            l, Rs, Rp, Ts, Tp = self.compute_next_cycle_efficiency()
            Rs_values[:,:,i] = Rs 
            Rp_values[:,:,i] = Rp
            Ts_values[:,:,i] = Ts
            Tp_values[:,:,i] = Tp
            thickness_values[i] = l         

        return thickness_values, Rs_values, Rp_values, Ts_values, Tp_values

    def initialize_cycle_calculation(self, thickness, max_steps=None):
        """
        Initializes efficiency calculations for a volume hologram in steps of full grating cycles.

        This method prepares the class for iterative calculations using `compute_next_cycle_efficiency()`. 
        
        Parameters:
        -----------
        thickness : float
            Total thickness of the hologram.
        max_steps : int, optional
            Maximum allowed steps in the iteration. If `None`, no step limit is applied.
        
        """
        check = self._is_within_max_steps(thickness, max_steps)       
        if not check:
            raise RCWAError("Too many steps for this thickness", "Increase max_steps")
        self.nz_steps_per_cycle = True
        self._l_one_cycle = self.get_cycle_length_z_direction()
        self._accumulated_scatter_matrices = self.get_accumulated_scatter_matrices()
        self._S_one_cycle  = self._accumulated_scatter_matrices["full"]
        self._current_length = 0.0        
        self._max_steps = max_steps
        self._current_step = -1
        self.thickness = thickness
        self.nz_steps_per_cycle = True
        self._device = None
  


    def compute_next_cycle_efficiency(self):
        """
        Computes diffraction efficiencies for the next incremental cycle step.

        This method should be called iteratively after `initialize_cycle_calculation()`.
        Each call increases the thickness by one grating cycle and returns updated efficiencies.

        Returns:
        --------
        tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            - l : float
                Current accumulated thickness after this step.
            - Rs : np.ndarray
                Reflection efficiencies for s-polarized light.
            - Rp : np.ndarray
                Reflection efficiencies for p-polarized light.
            - Ts : np.ndarray
                Transmission efficiencies for s-polarized light.
            - Tp : np.ndarray
                Transmission efficiencies for p-polarized light.

        """
        self._current_step += 1

        if (self._max_steps is not None) and (self._current_step > self._max_steps):
            raise RCWAError("Too many steps", "Increase max_steps")

        l = self._current_length        
        S_one_cycles = self._S_one_cycle
        device = self._device
        pram = self._rcwa_parameter
        accumulated_scatter_matrices = self._accumulated_scatter_matrices

        if device is None:
            dims = self._rcwa_parameter.dim_scattering_matrix_Sij
            device = ScatterMatrix.unity(dims)
        else:        
            device = ScatterMatrix.redheffer_star_product(device, S_one_cycles)            
            l+=self._l_one_cycle

        S_global = self._build_S_Global(accumulated_scatter_matrices, device)
        Rs, Rp, Ts, Tp = calculate_efficiency_Rs_Rp_Ts_Tp(pram,S_global)
        self._device = device
        self._current_length = l
        
        return l, Rs, Rp, Ts, Tp

    def get_cycle_count_for_thickness(self, thickness):
        """
        Computes the number of full grating cycles within a given thickness.

        Parameters:
        -----------
        thickness : float
            Total thickness of the hologram.

        Returns:
        --------
        int
            Number of full cycles that fit within the given thickness.
        
        """
        l_one_cycle = self.get_cycle_length_z_direction()
        if l_one_cycle == 0:
            raise RCWAError("Cycle length is zero", "Check grating vector or parameters")
        n_cycle =  math.ceil(thickness/l_one_cycle) 
        return n_cycle

    def _is_within_max_steps(self, thickness, max_steps):
        if max_steps is None:
            return True
        steps = self.get_cycle_count_for_thickness(thickness)
        if steps > max_steps:
            return False
        return True
        




