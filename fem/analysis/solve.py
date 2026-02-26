import numpy as np
from fem.analysis import assemble_stiffness,assemble_forces,assemble_spcs, compute_dof

def solve_static(model):
    n, dof_dict = compute_dof(model)

    k_global = assemble_stiffness(model, n, dof_dict)
    force_global = assemble_forces(model, n, dof_dict)
    spc_global = assemble_spcs(model, n, dof_dict)

    free_dofs = np.where(spc_global == 0)[0]

    K_ff = k_global[np.ix_(free_dofs, free_dofs)]
    F_f = force_global[free_dofs]

    u_f = np.linalg.solve(K_ff, F_f)

    u = np.zeros_like(force_global)
    u[free_dofs] = u_f

    return u