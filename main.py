import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input
from fem.analysis.solve import solve_static



# --- Create the model ---
E = 68 * 10**9
A =0.02**2
I = 0.02*0.02**3/12
EA = E*A
EI = E*I

P = 100
model = Model()

model.add_node(0, 0.0, 0.0)
model.add_node(1, 1.0, 0.0)
model.add_node(2, 0.5,0.5)
model.add_node(3, 0,1)

model.add_element(0, 0, 1, 'truss', EA, EI)
model.add_element(1, 1, 2, 'truss', EA, EI)
model.add_element(2, 0, 2, 'truss', EA, EI)
model.add_element(3, 2, 3, 'truss', EA, EI)

model.add_load(1,0,P,0)

model.add_spc(0, 1,1,0)
model.add_spc(2, 1,1,0)
model.add_spc(3, 1,1,0)

plot_input(model)

u = solve_static(model)
print(u)





