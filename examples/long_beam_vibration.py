
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output, animate_static, animate_modal, animate_static_v2, animate_forced_vibration
from fem.analysis.solve import solve_static, solve_modal, solve_vibration_force
from fem.analysis.vibration_ import Vibration_loads

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

node_n = 40

m = mass/node_n

model = Model()


for i in range(0,node_n):
    el_l = l/(node_n-1)
    model.add_node(i, el_l * i, 0, m)

for i in range(0,node_n-1):
    model.add_element(i, i, i+1, 'beam', EA, EI)

def input_force1(t):
    return np.where(t <= 1, 0.7*np.sin(2*t*np.pi*0.5), 0)

def input_force2(t):
    return np.where(t <= 1, -19*np.sin(2*t*np.pi), 0)

model.add_spc(0, 1,1,1)

vl = Vibration_loads()
vl.add_load(node_n-1, 0, input_force1, 0)  # Pass the function and its arguments
vl.add_load(node_n-20,0, input_force2 , 0)  # Pass the function and its arguments

res = solve_vibration_force(model, vl.loads)
animate_forced_vibration(res)

# print(res.U_t[-1,:])
y  = res.U_t[-1,:]
x = np.linspace(0,5,y.shape[0])
plt.plot(x,y)
plt.show()

