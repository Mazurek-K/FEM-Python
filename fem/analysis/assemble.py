from fem.analysis.stifness import stiffness_matrix
import numpy as np

def assemble(model):
    n = 9
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

        id_node_i = element.node_i
        id_node_j = element.node_j

        k_aa = k[0:dof_pn, 0:dof_pn]
        k_ab = k[0:dof_pn, dof_pn:dof_pn + dof_pn]
        k_ba = k[dof_pn:dof_pn + dof_pn, 0:dof_pn]
        k_bb = k[dof_pn:dof_pn + dof_pn, dof_pn:dof_pn + dof_pn]


        # node_i = model.nodes.get(id_node_i)
        # node_j = model.nodes.get(id_node_j)



    return k_global