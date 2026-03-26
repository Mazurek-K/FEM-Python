import numpy as np
from numpy.matlib import zeros
from scipy.linalg import eigh   # for symmetric matrices
import math
from scipy.fft import fft, fftfreq
from scipy.integrate import cumulative_trapezoid

from fem.analysis import (assemble_stiffness,assemble_forces,assemble_spcs, compute_dof,
                          assemble_spds, assemble_mass, assemble_vibration_forces, assemble_base)
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

class Results_vibration:
    def __init__(self, model):
        self.model = model
        self.U_t  = []
        self.dof_dict = {}
        self.times = []  # Time values corresponding to each column of U_t




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



def solve_vibration_force(model, loads, time = 5, damping =0.01, method = 'MAM'):

    # TODO: Add modal mass check
    # TODO: Mode  Acceleration method
    # TODO: Add log file/ stream

    """
        Solves the dynamic response of a structural model under vibration loads using modal analysis.

        This function constructs global stiffness and mass matrices, applies boundary conditions,
        and computes the system's time-domain response using the Mode Acceleration Method (MAM).
        The solution involves:
        - Frequency analysis of input loads via FFT to determine significant forcing frequencies.
        - Model reduction to free-free degrees of freedom and modal projection.
        - Time integration of modal equations using the Duhamel integral.
        - Reconstruction of physical displacements via Mode Displacement Method (MDM).

        Parameters:
            model: Structural model object containing geometry, material properties, and connectivity.
            loads: Dictionary of applied vibration forces (callable functions or constants).
            time: Time length of the simulation: int [seconds]
            damping: Coefficients of lower modes to compute Raleigh damping
            method: (Optional) Solution method. Default is 'MAM' (Mode Acceleration Method).

        Returns:
            result (Results_vibration): Object containing:
                - U_t: Displacement matrix over time for all degrees of freedom.
                - dof_dict: Dictionary mapping degrees of freedom to nodes.
                - times: Time vector for the computed response.

        Notes:
            - Assumes 2% damping (xi = 0.02) for all modes.
            - Time integration uses the Duhamel integral for accuracy.
            - Safety factor (sf = 1) can be adjusted to include higher frequencies.
        """

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
    fft_frequency  = 200
    N = fft_frequency * time # number of fourier check time steps
    T = (1 / N) * time # step size
    x = np.linspace(0.0, N * T, N, endpoint=False)

    for force in force_global.functions.values():
        if callable(force):
            # Compute FFT
            yf = fft(force(x))
            xf = fftfreq(N, T)[:N // 2]
            y_values = 2.0 / N * np.abs(yf[0:N // 2])

            # 1% of the peak amplitude threshold (the smaller the value the more precise the solution will be)
            threshold = 0.01 * np.max(y_values)

            # Find frequencies above threshold
            indicies = np.where(y_values >= threshold)[0]

            # Highest significant frequency
            max_considered_freq = xf[indicies[-1]]
            sf = 1 # safety factor
            omega_max = 2 * np.pi * max_considered_freq *sf  # Convert frequency to angular frequency


    # Model reduction to free-free
    constrained_dofs = np.where((spc_global != 0) | (spd_global != 0))[0]
    free_dofs = np.setdiff1d(np.arange(n), constrained_dofs)
    n_free = free_dofs.size

    # Partition matrices - free-free
    K_ff = k_global[np.ix_(free_dofs, free_dofs)]
    M_ff = m_global[np.ix_(free_dofs, free_dofs)]
    # --- Compute the selected low frequency eigenvalues/vectors ---
    eigvals, eigvecs = eigh(K_ff, M_ff, subset_by_value=[0, omega_max **2])

    # Angular velocities considered
    omegas = np.sqrt(eigvals)

    # time vector to consider: 5s with 10*max forcing frequency
    time_end = time
    time_n = int(time_end * np.floor(omega_max / (2 * np.pi))) * 10
    timespace = np.linspace(0, time_end, time_n)

    # Forcing values over time
    force_values = []
    for force in force_global.functions.values():
        if callable(force):
            force_values.append(force(timespace))
        else:
            force_values.append(np.ones_like(timespace)*force)
    force_matrix = np.vstack(force_values)

    # Partition force - free-free
    F_f = force_matrix[np.ix_(free_dofs)] # columns of consecutive forces in time

    # Projection into modal space
    U_l = eigvecs
    n_reduced = U_l.shape[1] # size of the reduced problem

    projected_M = U_l.T @ M_ff @ U_l
    projected_K = U_l.T @ K_ff @ U_l
    projected_F = np.empty((n_reduced, 0))  # Start with 0 columns

    for col in F_f.T:
        projected_col = U_l.T @ col
        projected_col = projected_col.reshape(-1, 1)

        # Stack horizontally
        projected_F = np.hstack((projected_F, projected_col))

    # simplifying the matrix, i guess it is not diagonal since numerical inaccuracies - TBC
    diag_M = np.diag(projected_M)
    diag_K = np.diag(projected_K)
    diag_M = np.diag(diag_M)
    diag_K = np.diag(diag_K)

    # Introduce damping terms using the simplified Raleigh model
    if n_reduced >=2:
        a_omegas = np.array([[1/omegas[0], omegas[0]], [1/omegas[1], omegas[1]]])
        b_xis = np.array([damping, damping]).reshape(-1,1)
        alphabeta = np.linalg.solve(a_omegas, b_xis)
        C = alphabeta[0] * diag_M + alphabeta[1] * diag_K

        xi = []
        for i in range(0,n_reduced ): xi.append (C[i,i]/(2* diag_M[i,i] * omegas[i] ))
    else:
        print("Not enough modes to compute Raleigh damping. Default value used. ")
        xi = np.ones(n_reduced) * damping

    # Initialize Q
    Q = np.zeros((n_reduced, time_n))

    # Precompute constants
    for i in range(n_reduced):
        m_i = diag_M[i, i]
        omega_i = omegas[i]
        xi_i = xi[i]
        omega_i_d = omega_i * np.sqrt(1 - xi_i ** 2)
        const_term = 1 / (m_i * omega_i_d)

        # Precompute modal forces for all time steps
        modal_forces = np.zeros(time_n)
        for j in range(time_n):
            modal_forces[j] = U_l[:, i].T @ F_f[:, j]

        # Compute Duhamel integral for each time step  to obtain q_i
        for j in range(time_n):
            t = timespace[j]
            # Integrate from tau=0 to tau=t
            integrand = np.array([
                np.exp(-xi_i * omega_i * (t - tau)) *
                np.sin(omega_i_d * (t - tau)) *
                modal_forces[k]
                for k, tau in enumerate(timespace[:j + 1])
            ])
            integral = cumulative_trapezoid(integrand, timespace[:j + 1], initial=0)
            Q[i, j] = const_term * integral[-1]


    # --- Mode Displacement Method (MDM) ---
    u_t = np.zeros((n_free,time_n))
    for i_t, t in enumerate(timespace):
        uiq = np.zeros((n_free,1))
        for i in range(0,n_reduced):
            col =  U_l[:,i] * Q[i,i_t]
            uiq += col.reshape(-1,1)

        u_t[:,i_t] = uiq.flatten()

    # Combine to global result array
    u_t_full = np.zeros((n,time_n))
    u_t_full[free_dofs, :] = u_t

    # Assign results
    result = Results_vibration(model)
    result.U_t = u_t_full
    result.dof_dict = dof_dict
    result.times = timespace
    return result



def solve_vibration_base(model, base_movements, time = 5, damping =0.01):
    # -------- SOLVER --------

    # Construct matrices
    n, dof_dict = compute_dof(model)
    k_global = assemble_stiffness(model, n, dof_dict)
    m_global = assemble_mass(model, n, dof_dict)

    base_global, spc_global = assemble_base(base_movements, n, dof_dict)

    # Prepare the Fourier input frequency check
    # checked over 5s with frequency = 200Hz
    fft_frequency = 200
    N = fft_frequency * time  # number of fourier check time steps
    T = (1 / N) * time  # step size
    x = np.linspace(0.0, N * T, N, endpoint=False)

    for disp in base_global.functions.values():
        if callable(disp):
            # Compute FFT
            yf = fft(disp(x))
            xf = fftfreq(N, T)[:N // 2]
            y_values = 2.0 / N * np.abs(yf[0:N // 2])

            # 1% of the peak amplitude threshold (the smaller the value the more precise the solution will be)
            threshold = 0.01 * np.max(y_values)

            # Find frequencies above threshold
            indicies = np.where(y_values >= threshold)[0]

            # Highest significant frequency
            max_considered_freq = xf[indicies[-1]]
            sf = 1  # safety factor
            omega_max = 2 * np.pi * max_considered_freq * sf  # Convert frequency to angular frequency


    # Model reduction to junction - junction
    junction_dofs = np.where((spc_global != 0) )[0]
    free_dofs = np.setdiff1d(np.arange(n), junction_dofs)
    n_free = free_dofs.size

    # Partition matrices - internal - internal, junction - junction
    K_ii = k_global[np.ix_(free_dofs, free_dofs)]
    M_ii = m_global[np.ix_(free_dofs, free_dofs)]

    K_jj = k_global[np.ix_(junction_dofs, junction_dofs)]
    M_jj = m_global[np.ix_(junction_dofs, junction_dofs)]

    K_ij = k_global[np.ix_(free_dofs, junction_dofs)]
    M_ij = m_global[np.ix_(free_dofs, junction_dofs)]

    K_ji = k_global[np.ix_(junction_dofs, free_dofs)]
    M_ji = m_global[np.ix_(junction_dofs, free_dofs)]

    # The NJ-th column of the matrix S corresponds to the static shape of deformation of the
    # structure when it is subjected to an imposed unitary displacement of the NJ-th DOF.

    S = -np.linalg.inv(K_ii) @ K_ij

    # time vector to consider: 5s with 10*max forcing frequency
    time_end = time
    time_n = int(time_end * np.floor(omega_max / (2 * np.pi))) * 10
    timespace = np.linspace(0, time_end, time_n)

    for t in timespace:
        pass

