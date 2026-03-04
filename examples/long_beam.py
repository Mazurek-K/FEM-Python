
import numpy as np
import matplotlib as plt
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output, animate_static, animate_modal, animate_static_v2
from fem.analysis.solve import solve_static, solve_modal, solve_vibration_force
from fem.analysis.vibration_ import Vibration_loads

# --- Material / Section ---
E = 10000
a = np.sqrt(100)
A = a**2
I = a * a**3 / 12
EA = E * A
EI = E * I
m = 0.0001
P = -1

model = Model()
node_n = 50
l = 500

for i in range(0,node_n):
    el_l = l/(node_n-1)
    model.add_node(i, el_l * i, 0, m)

for i in range(0,node_n-1):
    model.add_element(i, i, i+1, 'beam', EA, EI)

def input_force(t):
    return np.where(t <= 1, np.sin(10*t/np.pi), 0)


model.add_spc(0, 1,1,1)

vl = Vibration_loads()
vl.add_load(node_n-1, 0, input_force, 0)  # Pass the function and its arguments
res = solve_vibration_force(model, vl.loads)






