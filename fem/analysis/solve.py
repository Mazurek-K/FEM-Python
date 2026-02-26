import numpy as np
from fem.analysis import assemble_stiffness,assemble_forces,assemble_spcs, compute_dof

def solve_static(model):
    n, dof_dict = compute_dof(model)

    k_global = assemble_stiffness(model,n, dof_dict)
    force_global = assemble_forces(model, n,dof_dict)
    spc_global = assemble_spcs(model, n, dof_dict)


