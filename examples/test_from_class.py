
import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output
from fem.analysis.solve import solve_static

# --- Material / Section ---
E = 10000
a = np.sqrt(10)
A = a**2
I = a * a**3 / 12
EA = E * A
EI = E * I

P = -100 # vertical downward load

model = Model()

# -------------------------------------------------
# Geometry: Pratt-type bridge
# -------------------------------------------------
l = 360     #


model.add_node(0, 2*l, l)
model.add_node(1, 2*l, 0.0)
model.add_node(2, l,l)
model.add_node(3, l,0)
model.add_node(4, 0,l)
model.add_node(5, 0,0)



model.add_element(0, 0, 1, 'truss', EA, EI)
model.add_element(1, 0, 2, 'truss', EA, EI)
model.add_element(2, 0, 3, 'truss', EA, EI)
model.add_element(3, 1, 2, 'truss', EA, EI)
model.add_element(4, 1, 3, 'truss', EA, EI)
model.add_element(5, 2, 3, 'truss', EA, EI)
model.add_element(6, 2, 4, 'truss', EA, EI)
model.add_element(7, 2, 5, 'truss', EA, EI)
model.add_element(8, 3, 4, 'truss', EA, EI)
model.add_element(9, 3, 5, 'truss', EA, EI)



model.add_load(1,0,P,0)
model.add_load(3,0,P,0)

# model.add_spd(1,0.01, 0.01, 0)

model.add_spc(4, 1,1,0)
model.add_spc(5, 1,1,0)

plot_input(model)

res = solve_static(model)
plot_output(res,10)
print(res.nodal_displacements)