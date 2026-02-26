import numpy as np

class Node:
    def __init__(self, id, x,y):
        self.id = id
        self.x = x
        self.y = y

        self.elements = [] # related to elements

class Element:
    def __init__(self, id, node_i, node_j, el_type, EA, EI):
        self.id = id
        self.node_i = node_i
        self.node_j = node_j
        self.el_type = el_type # truss: 0; beam: 1
        self.EA = EA
        self.EI = EI

        self.stiffness_matrix = None # related to stiffness

class Load:
    def __init__(self, id_node, value_x, value_y):
        self.id_node = id_node
        self.value_x = value_x
        self.value_y = value_y

class SPC:
    def __init__(self, id_node, dof):
        self.id_node = id_node
        self.dof = dof


class Model:
    def __init__(self):
        self.nodes = {}
        self.elements = {}
        self.loads  = []
        self.spcs = []


    def add_node(self, id, x,y ):
        self.nodes[id] = Node(id, x,y)

    def add_element(self, id, id_node_i, id_node_j, el_type, EA, EI):
        node_i = self.nodes[id_node_i]
        node_j = self.nodes[id_node_j]

        element = Element(id, node_i, node_j, el_type, EA, EI)
        self.elements[id] = element

        # Link nodes to elements
        node_i.elements.append(element)
        node_j.elements.append(element)



    def add_load(self, id_node, value_x=0.0, value_y=0.0):
        load = Load(id_node, value_x, value_y)
        self.loads.append(load)

    def add_spc(self, id_node, dof):
        spc = SPC(id_node, dof)
        self.spcs.append(spc)





