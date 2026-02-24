import math
import numpy as np

def stiffness_matrix(element, nodes):

    id_node_i = element.node_i
    id_node_j = element.node_j

    node_i = nodes.get(id_node_i)
    node_j = nodes.get(id_node_j)

    x = [node_i.x, node_j.x]
    y = [node_i.y, node_j.y]
    lx = x[1] - x[0]
    ly = y[1] - y[0]

    l = math.sqrt(lx**2 + ly**2)

    c = lx/l
    s = ly/l
    if element.type == 'truss':
        EA = element.EA
        T = np.matrix([
            [c,s ,0 , 0], [0, 0, c, s]
        ])
        k_local = (EA / l) * np.matrix([[1,-1], [-1,1]])
        k = T.T * k_local * T

    elif element.type == 'beam':
        EA = element.EA
        EJ = element.EJ

        T = np.matrix([[c,s ,0 , 0], [-s,c,0], [0,0,1]])
        k_aa = np.matrix([
            [EA/l,0, 0 ], [0, 12*EJ / l**3, -6*EJ/ l**2], [0, 6*EJ/ l**2, 4*EJ/l]
        ])
        k_ab = np.matrix([
            [-EA/l, 0,0], [0, -12*EJ/l**3, -6*EJ/l**2], [0, 6*EJ/l**2, 2*EJ /l ]
        ])
        k_bb = np.matrix([
            [EA/l, 0, 0], [0, 12*EJ/l**3, 5*EJ/l**2], [0, 6*EJ/l**2, 4*EJ/l]
        ])
        k_local = np.bmat([
            [k_aa, k_ab],
            [k_ab.T, k_bb]
        ])

        k = T.T * k_local * T

    else:
        k = None
    return k
