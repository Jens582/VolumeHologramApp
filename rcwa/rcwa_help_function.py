import numpy as np
from rcwa.parameter import Parameter

def build_pq_grid(pram: Parameter) -> tuple[np.ndarray]:
    hx = np.linspace(-pram.harmonic_order_x, pram.harmonic_order_x, 2*pram.harmonic_order_x+1)
    hy = np.linspace(-pram.harmonic_order_y, pram.harmonic_order_y, 2*pram.harmonic_order_y+1)
    grid_p, grid_q = np.meshgrid(hx, hy)
    return grid_p, grid_q

def build_kxy_norm(pram: Parameter) -> tuple[np.ndarray]:
    grid_p, grid_q = build_pq_grid(pram)
    ps = grid_p.flatten()
    qs = grid_q.flatten()
    
    kxd = (pram.kx_inc-ps*pram.t_1x-qs*pram.t_2x)/pram.k0
    kyd = (pram.ky_inc-ps*pram.t_1y-qs*pram.t_2y)/pram.k0
    dim = kyd.shape[0]
    kxn = np.zeros((dim, dim), dtype=pram.dtype)
    kyn = np.zeros((dim, dim), dtype=pram.dtype)

    np.fill_diagonal(kxn, kxd)
    np.fill_diagonal(kyn, kyd)
    return kxn, kyn

def build_kz_norm_ref_trn(pram: Parameter) -> tuple[np.ndarray]:
    pre_ref = np.conjugate(pram.er_ref) * np.conjugate(pram.ur_ref)
    pre_trn = np.conjugate(pram.er_trn) * np.conjugate(pram.ur_trn)
    kxn, kyn = build_kxy_norm(pram)
    kzn_ref = -_calc_kz_norm_sqrt(pre_ref, kxn, kyn)
    kzn_trn = _calc_kz_norm_sqrt(pre_trn, kxn, kyn)
    return kzn_ref, kzn_trn

def _calc_kz_norm_sqrt(pre: complex, kxn: np.ndarray, kyn: np.ndarray) -> np.ndarray:        
    dim = kxn.shape[0]
    I = np.eye(dim, dtype=Parameter.dtype)
    square = pre*I - (kxn**2 + kyn**2)
    sqrt = np.sqrt(square)
    return np.conjugate(sqrt)
