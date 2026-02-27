import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output
from fem.analysis.solve import solve_static



# --- Create the model ---
E = 68 * 10**9
A =0.002**2
I = 0.02*0.02**3/12
EA = E*A
EI = E*I

P = 10000
model = Model()

model.add_node(0, 0.0, 0.0)
model.add_node(1, 1.0, 0.0)
model.add_node(2, 0.5,0.5)
model.add_node(3, 0,1)

model.add_element(0, 0, 1, 'beam', EA, EI)
model.add_element(1, 1, 2, 'beam', EA, EI)
model.add_element(2, 0, 2, 'beam', EA, EI)
model.add_element(3, 2, 3, 'beam', EA, EI)

model.add_load(1,0,P,0)
# model.add_spd(1,0.01, 0.01, 0)

model.add_spc(0, 1,1,0)
model.add_spc(2, 1,0,0)
model.add_spc(3, 1,1,0)

plot_input(model)

res = solve_static(model)
plot_output(res)







