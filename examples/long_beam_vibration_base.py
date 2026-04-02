
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output, animate_static, animate_modal, animate_static_v2, animate_forced_vibration
from fem.analysis.solve import solve_static, solve_modal, solve_vibration_force, solve_vibration_base
from fem.analysis.vibration_ import VibrationLoads, VibrationDisplacements

# --- Material / Section ---
E = 68000
a = 5
A = a**2
I = a * a**3 / 12
EA = E * A
EI = E * I
ro = 2700/1000**3
l = 500
mass = ro*a*a*l

node_n = 12

m = mass/node_n

model = Model()


for i in range(0,node_n):
    el_l = l/(node_n-1)
    model.add_node(i, el_l * i, 0, m)

for i in range(0,node_n-1):
    model.add_element(i, i, i+1, 'beam', EA, EI)

def input_disp(t):
    return np.where(t <= 1, np.sin(2*t*np.pi*0.5), 0)

def input_disp_2(t):
    return 0*t

vl = VibrationDisplacements()
vl.add_displacements([0,1], input_disp, input_disp, input_disp_2)


res = solve_vibration_base(model, vl.displacements)

