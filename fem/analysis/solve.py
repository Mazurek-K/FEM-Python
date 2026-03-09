import numpy as np
from scipy.linalg import eigh   # for symmetric matrices
import math
from scipy.fft import fft, fftfreq


from fem.analysis import (assemble_stiffness,assemble_forces,assemble_spcs, compute_dof,
                          assemble_spds, assemble_mass, assemble_vibration_forces)
from colorama import init, Fore, Style
init()  # initialize colorama


class Results_static:
    def __init__(self, model):
        self.model = model
        self.nodal_displacements = {}
        self.nodal_forces = {}

class Results_modal:
    def __init__(self, model):
        self.model = model
        self.omega  = []
        self.modes = []
        self.dof_dict = {}


def solve_static(model):
    n, dof_dict = compute_dof(model)

    k_global = assemble_stiffness(model, n, dof_dict)
    force_global = assemble_forces(model, n, dof_dict)
    spc_global = assemble_spcs(model, n, dof_dict)
    spd_global = assemble_spds(model, n, dof_dict)

    constrained_dofs = np.where((spc_global != 0) | (spd_global != 0))[0]
    free_dofs = np.setdiff1d(np.arange(n), constrained_dofs)

    # Constrained dofs
    u_c = spd_global[constrained_dofs]

    # Partition matrices
    K_ff = k_global[np.ix_(free_dofs, free_dofs)]
    K_fc = k_global[np.ix_(free_dofs, constrained_dofs)]

    F_f = force_global[free_dofs]

    rank = np.linalg.matrix_rank(K_ff)
    n_f = len(F_f)
    if rank != n_f:
        print("Rank of K_ff: ", rank)
        print("Number of prescribed forces: ", n_f)
        print(Fore.RED + "Could not solve " + Style.RESET_ALL)
        return None
    else:
        # RHS
        F_mod = F_f - K_fc @ u_c

        # Solve
        u_f = np.linalg.solve(K_ff, F_mod)

        # Reconstruct displacement
        u = np.zeros(n)
        u[free_dofs] = u_f
        u[constrained_dofs] = u_c

        # Constuct results
        result = Results_static(model)


        for node_id, dof_indices in dof_dict.items():
            result.nodal_displacements[node_id] = u[dof_indices]

        return result



def solve_modal(model, n_modes):
    n, dof_dict = compute_dof(model)

    k_global = assemble_stiffness(model, n, dof_dict)
    m_global  = assemble_mass(model, n, dof_dict)

    spc_global = assemble_spcs(model, n, dof_dict)
    spd_global = assemble_spds(model, n, dof_dict)

    constrained_dofs = np.where((spc_global != 0) | (spd_global != 0))[0]
    free_dofs = np.setdiff1d(np.arange(n), constrained_dofs)

    # Partition matrices
    K_ff = k_global[np.ix_(free_dofs, free_dofs)]
    M_ff = m_global[np.ix_(free_dofs, free_dofs)]


    if n_modes >= len(free_dofs):
        n_modes = len(free_dofs)

    eigvals, eigvecs = eigh(K_ff, M_ff, subset_by_index=[0, n_modes - 1])
    omega = np.sqrt(eigvals)

    # Sort
    idx = np.argsort(omega)
    omega = omega[idx]
    modes_full = np.zeros((n, len(omega)))
    modes_full[free_dofs, :] = eigvecs[:, idx]


    results = Results_modal(model)
    results.omega = omega
    results.modes = modes_full
    results.dof_dict = dof_dict

    return results


def solve_vibration_force(model, loads,  method = 'MAM'):
    # Force loaded case

    # Split into loaded and unloaded part, take the first one

    # 1) Modal response method
    # 2) Direct response analysis

    # -> 1) -> Normal modes approach
    # Mode displacement method (MDM)/ Mode acceleration method (MAM)
    # method  = 'MAM' or 'MDM'

    # -------- SOLVER --------


    # Construct matrices
    n, dof_dict = compute_dof(model)
    k_global = assemble_stiffness(model, n, dof_dict)
    m_global  = assemble_mass(model, n, dof_dict)
    spc_global = assemble_spcs(model, n, dof_dict)
    spd_global = assemble_spds(model, n, dof_dict)

    # Vibration loads
    force_global = assemble_vibration_forces(loads, n, dof_dict)


    # Prepare the Fourier input frequency check
    # checked over 5s with frequency = 200Hz
    N = 1000 # number of fourier check time steps
    T = (1 / N) * 5 # step size
    x = np.linspace(0.0, N * T, N, endpoint=False)
    max_omegas = []
    for force in force_global.functions.values():
        if callable(force):
            # Compute FFT
            yf = fft(force(x))
            xf = fftfreq(N, T)[:N // 2]
            y_values = 2.0 / N * np.abs(yf[0:N // 2])

            # 5% of the peak amplitude threshold
            threshold = 0.05 * np.max(y_values)

            # Find frequencies above threshold
            indicies = np.where(y_values >= threshold)[0]

            # Highest significant frequency
            max_considered_freq = xf[indicies[-1]]
            sf = 1.2 # safety factor
            omega_max = 2 * np.pi * max_considered_freq *sf  # Convert frequency to angular frequency
            max_omegas.append(omega_max)

    # Maximum forcing angular velocity to consider
    omega_max = max(max_omegas)

    # Model reduction to free-free
    constrained_dofs = np.where((spc_global != 0) | (spd_global != 0))[0]
    free_dofs = np.setdiff1d(np.arange(n), constrained_dofs)

    # Partition matrices - free-free
    K_ff = k_global[np.ix_(free_dofs, free_dofs)]
    M_ff = m_global[np.ix_(free_dofs, free_dofs)]

    # --- Compute the selected low frequency eigenvalues/vectors ---
    eigvals, eigvecs = eigh(K_ff, M_ff, subset_by_value=[0, omega_max **2])

    # time vector to consider: 5s with 10*max forcing frequency
    time_end = 5
    time_n = int(time_end * np.floor(omega_max / (2 * np.pi))) * 10
    t = np.linspace(0, time_end, time_n)

    # Forcing values over time
    force_values = []
    for force in force_global.functions.values():
        if callable(force):
            force_values.append(force(t))
        else:
            force_values.append(np.ones_like(t)*force)
    force_matrix = np.vstack(force_values)

    # Partition force - free-free
    F_f = force_matrix[np.ix_(free_dofs)]

    # Projection into modal space
    U_l = eigvecs
    projected_M = U_l.T @ M_ff @ U_l
    projected_K = U_l.T @ K_ff @ U_l

    for col in F_f.T:
        projected_F = np.hstack(U_l.T * col)

    # simplifying the matrix, i guess it is not diagonal since numerical inaccuracies - TBC
    diag_M = np.diag(projected_M)
    diag_K = np.diag(projected_K)
    diag_M = np.diag(diag_M)
    diag_K = np.diag(diag_K)

    n = U_l.shape[1] # size of the reduced problem








