import numpy as np
import matplotlib.pyplot as plt

class Node:
    def __init__(self, id, x,y):
        self.id = id
        self.x = x
        self.y = y

class Element:
    def __init__(self, id, node_i, node_j, type, EA, EI):
        self.node_i = node_i
        self.node_j = node_j
        self.type = type # truss: 0; beam: 1
        self.EA = EA
        self.EI = EI

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

    def add_element(self, id, node_i, node_j, type, EA, EI):
        self.elements[id] = Element(id, node_i, node_j, type, EA, EI)

    def add_load(self, id_node, value_x=0.0, value_y=0.0):
        load = Load(id_node, value_x, value_y)
        self.loads.append(load)

    def add_spc(self, id_node, dof):
        spc = SPC(id_node, dof)
        self.spcs.append(spc)

    def plot_input(self):

        plt.figure()
        for element in self.elements.values():
            node_i = self.nodes[element.node_i]
            node_j = self.nodes[element.node_j]

            x = [node_i.x, node_j.x]
            y = [node_i.y, node_j.y]

            plt.plot(x, y, 'r')

        for node in self.nodes.values():
            plt.plot(node.x, node.y, 'o')
            plt.text(node.x, node.y, f'{node.id}')

        # Plot loads
        for load in self.loads:
            node = self.nodes[load.id_node]
            plt.arrow(node.x, node.y,
                      load.value_x * 0.001,
                      load.value_y * 0.001,
                      head_width=0.05)

        # Plot SPCs (small squares)
        for spc in self.spcs:
            node = self.nodes[spc.id_node]
            plt.plot(node.x, node.y, 's')

        plt.gca().set_aspect('equal')
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Structure")
        plt.grid(True)
        plt.show()

#