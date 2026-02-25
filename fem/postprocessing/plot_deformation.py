import matplotlib.pyplot as plt

def plot_input(model):

    plt.figure()

    # Plot elements
    for element in model.elements.values():

        node_i = element.node_i
        node_j = element.node_j

        x = [node_i.x, node_j.x]
        y = [node_i.y, node_j.y]

        plt.plot(x, y, 'r')

    # Plot nodes
    for node in model.nodes.values():
        plt.plot(node.x, node.y, 'o')
        plt.text(node.x, node.y, f'{node.id}')

    # Plot loads
    for load in model.loads:
        node = model.nodes[load.id_node]

        plt.arrow(node.x, node.y,
                  load.value_x * 0.001,
                  load.value_y * 0.001,
                  head_width=0.05)

    # Plot SPCs
    for spc in model.spcs:
        node = model.nodes[spc.id_node]
        plt.plot(node.x, node.y, 's')

    plt.gca().set_aspect('equal')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Structure")
    plt.grid(True)
    plt.show()