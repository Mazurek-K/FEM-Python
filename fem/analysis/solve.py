import numpy as np
from fem.analysis import assemble_stiffness,assemble_forces,assemble_spcs, compute_dof, assemble_spds
from colorama import init, Fore, Style
init()  # initialize colorama


class Results:
    def __init__(self, model):
        self.model = model
        self.nodal_displacements = {}
        self.nodal_forces = {}



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
        result = Results(model)

        for node_id, dof_indices in dof_dict.items():
            result.nodal_displacements[node_id] = u[dof_indices]

        return result



def solve_modal(model):
    pass