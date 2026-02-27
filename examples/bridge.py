
import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.model_create import Model
from fem.postprocessing.plot_deformation import plot_input, plot_output
from fem.analysis.solve import solve_static

# --- Material / Section ---
E = 68 * 10**9
A = 0.003**2
I = 0.03 * 0.03**3 / 12
EA = E * A
EI = E * I

P = -100000  # vertical downward load

model = Model()

# -------------------------------------------------
# Geometry: Pratt-type bridge
# -------------------------------------------------
L = 10.0      # total span
H = 2.0       # truss height
n_panels = 10 # number of panels

dx = L / n_panels

# --- Bottom chord nodes ---
for i in range(n_panels + 1):
    model.add_node(i, i * dx, 0.0)

# --- Top chord nodes ---
top_offset = n_panels + 1
for i in range(n_panels + 1):
    model.add_node(top_offset + i, i * dx, H)

# -------------------------------------------------
# Elements
# -------------------------------------------------
el_id = 0

# Bottom chord
for i in range(n_panels):
    model.add_element(el_id, i, i + 1, 'beam', EA, EI)
    el_id += 1

# Top chord
for i in range(n_panels):
    model.add_element(el_id, top_offset + i, top_offset + i + 1, 'beam', EA, EI)
    el_id += 1

# Vertical members
for i in range(n_panels + 1):
    model.add_element(el_id, i, top_offset + i, 'beam', EA, EI)
    el_id += 1

# Diagonal members (Pratt configuration)
for i in range(n_panels):
    if i % 2 == 0:
        model.add_element(el_id, i, top_offset + i + 1, 'beam', EA, EI)
    else:
        model.add_element(el_id, i + 1, top_offset + i, 'beam', EA, EI)
    el_id += 1

# -------------------------------------------------
# Loads
# -------------------------------------------------
mid_node = n_panels // 2
model.add_load(mid_node, 0.0, P, 0.0)

# -------------------------------------------------
# Boundary Conditions
# -------------------------------------------------
# Left support: pinned (Ux = Uy = 0)
model.add_spc(0, 1, 1, 1)

# Right support: roller (Uy = 0)
model.add_spc(n_panels, 0, 1, 0)


plot_input(model)

res = solve_static(model)
plot_output(res)