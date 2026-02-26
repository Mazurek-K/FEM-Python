import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000)

from fem.mesh.mesh_create import Model
from fem.analysis.assemble import assemble
from fem.postprocessing.plot_deformation import plot_input



# --- Create the model ---
EA = 100
P = 100
model = Model()

model.add_node(0, 0.0, 0.0)
model.add_node(1, 1.0, 0.0)
model.add_node(2, 0.5,0.5)
model.add_node(3, 0,1)

model.add_element(0, 0, 1, 'truss', EA, 0)
model.add_element(1, 1, 2, 'truss', EA, 0)
model.add_element(2, 0, 2, 'truss', EA, 0)
model.add_element(3, 2, 3, 'beam', EA, 5)

model.add_load(1,0,P)

model.add_spc(0, dof=0)
model.add_spc(0, dof=1)
model.add_spc(2, dof=0)
model.add_spc(3, dof=0)
model.add_spc(3, dof=1)

plot_input(model)

# --- Create the stiffness
print(assemble(model))
# for element in model.elements.values():
#     print(element.stiffness_matrix)


# for node in model.nodes.values():
    # elements = node.elements
    # for el in elements:
    #     print (el.id)
    # print("\n")



