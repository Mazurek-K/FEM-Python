import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output, animate_static, animate_modal, animate_static_v2, animate_forced_vibration
from fem.analysis.solve import solve_static, solve_modal, solve_vibration_force
from fem.analysis.vibration_ import VibrationLoads

# --- Material / Section ---
E = 10000
a = np.sqrt(10)
A = a**2
I = a * a**3 / 12

EA = E * A
EI = E * I
m = 0.0001

P = -100

# Parameters
panel_length = 360
height = 360

n_panels = 6        # number of Pratt patterns
n_sub = 5           # elements per member



def add_subdivided_member(model, n1, n2, n_sub, EA, EI):

    start = model.nodes[n1]
    end = model.nodes[n2]

    x1, y1 = start.x, start.y
    x2, y2 = end.x, end.y

    last = n1

    for i in range(1, n_sub):
        t = i / n_sub
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)

        new_id = len(model.nodes)
        model.add_node(new_id, x, y, m)

        model.add_element(len(model.elements), last, new_id, 'beam', EA, EI)

        last = new_id

    model.add_element(len(model.elements), last, n2, 'beam', EA, EI)

# Build Model

model = Model()

top_nodes = []
bot_nodes = []

# create nodes
for i in range(n_panels + 1):

    x = i * panel_length

    top_id = len(model.nodes)
    model.add_node(top_id, x, height, m)
    top_nodes.append(top_id)

    bot_id = len(model.nodes)
    model.add_node(bot_id, x, 0, m)
    bot_nodes.append(bot_id)

# Top chord
for i in range(n_panels):
    add_subdivided_member(model, top_nodes[i], top_nodes[i+1], n_sub, EA, EI)

# Bottom chord
for i in range(n_panels):
    add_subdivided_member(model, bot_nodes[i], bot_nodes[i+1], n_sub, EA, EI)

# Verticals
for i in range(n_panels + 1):
    add_subdivided_member(model, top_nodes[i], bot_nodes[i], n_sub, EA, EI)

# Pratt diagonals
# for i in range(n_panels):
#
#     if i % 2 == 0:
#         add_subdivided_member(model, bot_nodes[i], top_nodes[i+1], n_sub, EA, EI)
#     else:
#         add_subdivided_member(model, top_nodes[i], bot_nodes[i+1], n_sub, EA, EI)

# Loads
def input_force1(t):
    return np.where(t <= 1, -0.1*np.sin(2*t*np.pi*0.5), 0)

vl = VibrationLoads()
loaded_node = bot_nodes[-1]
vl.add_load(loaded_node, 0, input_force1, 0)  # Pass the function and its arguments


# Supports
model.add_spc(bot_nodes[0], 1,1,0)
model.add_spc(top_nodes[0], 1,1,0)

# Solve

res = solve_vibration_force(model, vl.loads, time=15, damping=0.01)
animate_forced_vibration(res, max_scale=10)

# print(res.U_t[-1,:])
y  = res.U_t[-1,:]
x = np.linspace(0,5,y.shape[0])
plt.plot(x,y)
plt.show()
