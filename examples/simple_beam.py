
import numpy as np
import matplotlib as plt
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output, animate_static, animate_modal, animate_static_v2
from fem.analysis.solve import solve_static, solve_modal

# --- Material / Section ---
E = 10000
a = np.sqrt(100)
A = a**2
I = a * a**3 / 12
EA = E * A
EI = E * I
m = 0.0001

P = -1 # vertical downward load

model = Model()

# -------------------------------------------------
# Geometry: Pratt-type bridge
# -------------------------------------------------
l = 360     #


model.add_node(0, 0, 0,m)
model.add_node(1, l, 0,m)
model.add_node(2, 2*l, 0,m)
model.add_node(3, 3*l, 0,m)


model.add_element(0, 0, 1, 'beam', EA, EI)
model.add_element(1, 1, 2, 'beam', EA, EI)
model.add_element(2, 2, 3, 'beam', EA, EI)

model.add_load(3,0,P,0)

# model.add_spd(1,0.01, 0.01, 0)

model.add_spc(0, 1,1,1)


res = solve_static(model)
res_modal = solve_modal(model, 8)

print(res.nodal_displacements)

plot_output(res, 10)
animate_static_v2(res, 10, 20)
# animate_modal(res_modal,0)



