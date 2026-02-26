from fem.analysis.stifness import stiffness_matrix
import numpy as np


def compute_dof(model):
    largest_dof = 0
    dof_dict = {}  # dof for each node assign  dof-s
    force_array = {}  # force component for each dof
    spc_array = {}  # spc for each dof

    # Decide global DOF per node based on model elements
    dof_per_node = 3 if any(e.el_type == 'beam' for e in model.elements.values()) else 2

    # Assign DOF-s sequentially to nodes
    for node_id in sorted(model.nodes):
        dof_dict[node_id] = list(range(largest_dof, largest_dof + dof_per_node))
        largest_dof += dof_per_node

    total_dof = largest_dof

    return total_dof, dof_dict


def assemble_stiffness(model, n, dof_dict):

    k_global = np.zeros((n,n))

    for element in model.elements.values():
        k = stiffness_matrix(element)
        element.stiffness_matrix = k

        if element.el_type == 'beam':
            dof_pn = 3
        elif element.el_type == 'truss':
            dof_pn = 2
        else:
            raise ValueError("Incorrect element type")

        node_i = element.node_i
        node_j = element.node_j

        # global DOF indices
        dofs_i = dof_dict[node_i.id]
        dofs_j = dof_dict[node_j.id]

        # assemble full element DOF list
        element_dofs = dofs_i[:dof_pn] + dofs_j[:dof_pn]

        # add to global matrix
        for a in range(len(element_dofs)):
            for b in range(len(element_dofs)):
                k_global[element_dofs[a], element_dofs[b]] += k[a, b]


    return k_global


def assemble_forces(model, n, dof_dict):

    global_force = np.zeros(n)

    for load in model.loads:
        node_id = load.id_node
        load_values = [load.value_x, load.value_y, load.value_rxy]

        dofs = dof_dict[node_id]

        for i in range(len(dofs)):
            global_force[dofs[i]] += load_values[i]

    return global_force


def assemble_spcs(model, n, dof_dict):
    global_spcs = np.zeros(n)

    for spc in model.spcs:
        node_id = spc.id_node
        load_values = [spc.value_x, spc.value_y, spc.value_rxy]

        dofs = dof_dict[node_id]

        for i in range(len(dofs)):
            global_spcs[dofs[i]] += load_values[i]

    return global_spcs

