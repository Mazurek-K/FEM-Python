import math
import numpy as np

def stiffness_matrix(element):

    node_i = element.node_i
    node_j = element.node_j

    x = [node_i.x, node_j.x]
    y = [node_i.y, node_j.y]
    lx = x[1] - x[0]
    ly = y[1] - y[0]

    l = math.sqrt(lx**2 + ly**2)
    if l == 0:
        raise ValueError("Zero length element.")

    c = lx/l
    s = ly/l

    if element.el_type == 'truss':
        EA = element.EA

        T = np.array([
            [c,s ,0 , 0], [0,0, c, s]
        ])

        k_local = (EA / l) * np.array([[1,-1], [-1,1]])
        k = T.T @ k_local @ T

    elif element.el_type == 'beam':
        EA = element.EA
        EI = element.EI

        T = np.array([
            [c, s, 0, 0, 0, 0],
            [-s, c, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, c, s, 0],
            [0, 0, 0, -s, c, 0],
            [0, 0, 0, 0, 0, 1]
        ])

        k_aa = np.array([
            [EA/l,0, 0 ], [0, 12*EI / l**3, -6*EI/ l**2], [0, -6*EI/ l**2, 4*EI/l]
        ])
        k_ab = np.array([
            [-EA/l, 0,0], [0, -12*EI/l**3, -6*EI/l**2], [0, 6*EI/l**2, 2*EI /l ]
        ])
        k_bb = np.array([
            [EA/l, 0, 0], [0, 12*EI/l**3, 6*EI/l**2], [0, 6*EI/l**2, 4*EI/l]
        ])
        k_local = np.block([
            [k_aa, k_ab],
            [k_ab.T, k_bb]
        ])


        k = T.T @ k_local @ T

    else:
        raise ValueError("Incorrect element type")
    return k
