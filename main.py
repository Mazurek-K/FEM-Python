from fem.mesh.mesh_create import Model
from fem.analysis.assemble import assemble

EA = 100
P = 100
model = Model()

model.add_node(1, 0.0, 0.0)
model.add_node(2, 1.0, 0.0)
model.add_node(3, 0.5,0.5)
model.add_node(4, 0,1)

model.add_element(1, 1, 2, 'truss', EA, 0)
model.add_element(2, 2, 3, 'truss', EA, 0)
model.add_element(3, 1, 3, 'truss', EA, 0)
model.add_element(4, 3, 4, 'truss', EA, 0)

model.add_load(2,0,P)

model.add_spc(1, dof=0)
model.add_spc(1, dof=1)
model.add_spc(3, dof=0)
model.add_spc(4, dof=0)
model.add_spc(4, dof=1)

model.plot_input()

k = assemble(model)
print(k)

