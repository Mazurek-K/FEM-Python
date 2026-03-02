
import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output
from fem.analysis.solve import solve_static

# --- Material / Section ---
E = 72
l2= 1732
l1 = 1000
P = -10
A= 1600
EA = E * A
EI = None
m = 0.0001


model = Model()

# -------------------------------------------------
# Geometry: Pratt-type bridge
# -------------------------------------------------
l = 360     #


model.add_node(0, 0,0,m)
model.add_node(1, l2, 0.0,m)
model.add_node(2, l2/2,l1/2,m)
model.add_node(3, 0,l1,m)




model.add_element(0, 0, 1, 'truss', EA, EI)
model.add_element(1, 1, 2, 'truss', EA, EI)
model.add_element(2, 0, 2, 'truss', EA, EI)
model.add_element(3, 2, 3, 'truss', EA, EI)



model.add_load(1,0,P,0)

# model.add_spd(1,0.01, 0.01, 0)

model.add_spc(0, 1,1,0)
model.add_spc(3, 1,1,0)
model.add_spc(2, 1,0,0)

plot_input(model)

res = solve_static(model)
plot_output(res,50)
print(res.nodal_displacements)