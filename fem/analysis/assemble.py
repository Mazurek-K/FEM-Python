from fem.analysis.stifness import stiffness_matrix
import numpy as np


def assemble(model):
    def compute_dof(model):

        largest_dof = 0
        dof_array = {}

        # Decide global DOF per node based on model elements
        dof_per_node = 3 if any(e.el_type == 'beam' for e in model.elements.values()) else 2

        # Assign DOF-s sequentially to nodes
        for node_id in sorted(model.nodes):
            dof_array[node_id] = list(range(largest_dof, largest_dof + dof_per_node))
            largest_dof += dof_per_node

        total_dof = largest_dof
        dof_array = dof_array  # store in model for later use

        return total_dof, dof_array

    n , dof_array = compute_dof(model)
    k_global = np.zeros((n,n))
    print(dof_array)
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
        dofs_i = dof_array[node_i.id]
        dofs_j = dof_array[node_j.id]

        # assemble full element DOF list
        element_dofs = dofs_i[:dof_pn] + dofs_j[:dof_pn]

        # add to global matrix
        for a in range(len(element_dofs)):
            for b in range(len(element_dofs)):
                k_global[element_dofs[a], element_dofs[b]] += k[a, b]


    return k_global