import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

def plot_input(model):

    plt.figure()

    # Plot elements
    for element in model.elements.values():

        node_i = element.node_i
        node_j = element.node_j

        if element.el_type == 'beam':
            color = 'r'
        else:
            color = 'b'
        x = [node_i.x, node_j.x]
        y = [node_i.y, node_j.y]

        plt.plot(x, y, color)

    # Plot nodes
    for node in model.nodes.values():
        plt.plot(node.x, node.y, 'o')
        plt.text(node.x, node.y, f'{node.id}')

    # Plot loads
    # for load in model.loads:
    #     node = model.nodes[load.id_node]
    #
    #     plt.arrow(node.x, node.y,
    #               load.value_x * 0.001,
    #               load.value_y * 0.001,
    #               head_width=0.05)

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


def plot_output(result,scale_factor):
    model = result.model
    nodal_displacements = result.nodal_displacements

    plt.figure()

    for node_id, node_prop in model.nodes.items():
        node_disp  = nodal_displacements[node_id]

        node_prop.x = node_prop.x + node_disp[0] * scale_factor
        node_prop.y = node_prop.y + node_disp[1] * scale_factor

    # Plot elements
    for element in model.elements.values():

        node_i = element.node_i
        node_j = element.node_j

        if element.el_type == 'beam':
            color = 'r'
        else:
            color = 'b'
        x = [node_i.x, node_j.x]
        y = [node_i.y, node_j.y]

        plt.plot(x, y, color)

    # Plot nodes
    for node in model.nodes.values():
        plt.plot(node.x, node.y, 'o')
        plt.text(node.x, node.y, f'{node.id}')

    # Plot loads
    # for load in model.loads:
    #     node = model.nodes[load.id_node]
    #     plt.arrow(node.x, node.y,
    #               load.value_x * 0.001,
    #               load.value_y * 0.001,
    #               head_width=0.05)

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


def animate_static(result, max_scale=10, n_frames=60):

    model = result.model
    nodal_displacements = result.nodal_displacements

    max_x = max(node.x for node in model.nodes.values())
    max_y = max(node.y for node in model.nodes.values())
    min_x = min(node.x for node in model.nodes.values())
    min_y = min(node.y for node in model.nodes.values())
    diff_x = abs(max_x - min_x)
    diff_y = abs(max_y - min_y)


    # Store original coordinates
    original_coords = {}
    for node_id, node in model.nodes.items():
        original_coords[node_id] = (node.x, node.y)

    fig, ax = plt.subplots()

    # Create scale factor variation
    scales = max_scale * np.sin(np.linspace(0, np.pi, n_frames))

    element_lines = []
    node_plots = []

    # ---- INITIAL DRAW ----
    for element in model.elements.values():
        color = 'r' if element.el_type == 'beam' else 'b'
        xi0, yi0 = original_coords[element.node_i.id]
        xj0, yj0 = original_coords[element.node_j.id]
        line, = ax.plot([xi0, xj0], [yi0, yj0], color)
        element_lines.append((line, element))

    for node in model.nodes.values():
        x0, y0 = original_coords[node.id]
        point, = ax.plot([x0], [y0], 'o')
        node_plots.append((point, node))

    for spc in model.spcs:
        node = model.nodes[spc.id_node]
        ax.plot(node.x, node.y, 's')

    ax.set_aspect('equal')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Animated Structure")
    plt.xlim(min_x - 0.1*abs(diff_x),max_x +0.1*abs(diff_x) )
    plt.ylim(min_y - 0.1*abs(diff_y), max_y + 0.1*abs(diff_y))
    ax.grid(True)

    # ---- UPDATE FUNCTION ----
    def update(frame):
        scale = scales[frame]

        # Update element lines
        for (line, element) in element_lines:

            node_i = element.node_i
            node_j = element.node_j

            xi0, yi0 = original_coords[node_i.id]
            xj0, yj0 = original_coords[node_j.id]

            di = nodal_displacements[node_i.id]
            dj = nodal_displacements[node_j.id]

            xi = xi0 + di[0] * scale
            yi = yi0 + di[1] * scale
            xj = xj0 + dj[0] * scale
            yj = yj0 + dj[1] * scale

            line.set_data([xi, xj], [yi, yj])

        # Update node positions
        for (point, node) in node_plots:
            x0, y0 = original_coords[node.id]
            d = nodal_displacements[node.id]

            x = x0 + d[0] * scale
            y = y0 + d[1] * scale

            point.set_data([x], [y])

        return [l[0] for l in element_lines] + [p[0] for p in node_plots]

    # --- ANIMATION ---
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=40,
        blit=True
    )

    plt.show()


def animate_modal(result, i_mode = 0, max_scale=1, n_frames=60):

    model = result.model
    # if any(e.el_type == "beam" for e in model.elements.values()):
    #     raise ValueError("Beam elements are not supported yet.")

    displacements = result.modes[:, i_mode]
    nodal_displacements = {}
    for node_id, dof_indices in result.dof_dict.items():
        nodal_displacements[node_id] = displacements[dof_indices]

    max_x = max(node.x for node in model.nodes.values())
    max_y = max(node.y for node in model.nodes.values())
    min_x = min(node.x for node in model.nodes.values())
    min_y = min(node.y for node in model.nodes.values())
    diff_x = abs(max_x - min_x)
    diff_y = abs(max_y - min_y)

    # Store original coordinates
    original_coords = {}
    for node_id, node in model.nodes.items():
        original_coords[node_id] = (node.x, node.y)

    fig, ax = plt.subplots()

    # Create scale factor variation
    scales = max_scale * np.sin(np.linspace(0, 2*np.pi, n_frames))

    element_lines = []
    node_plots = []

    # ---- INITIAL DRAW ----
    for element in model.elements.values():
        color = 'r' if element.el_type == 'beam' else 'b'
        xi0, yi0 = original_coords[element.node_i.id]
        xj0, yj0 = original_coords[element.node_j.id]
        line, = ax.plot([xi0, xj0], [yi0, yj0], color)
        element_lines.append((line, element))

    for node in model.nodes.values():
        x0, y0 = original_coords[node.id]
        point, = ax.plot([x0], [y0], 'o')
        node_plots.append((point, node))

    for spc in model.spcs:
        node = model.nodes[spc.id_node]
        ax.plot(node.x, node.y, 's')

    ax.set_aspect('equal')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Animated Structure")
    border_ratio = 0.2
    plt.xlim(min_x - border_ratio * abs(diff_x), max_x + border_ratio * abs(diff_x))
    plt.ylim(min_y - border_ratio * abs(diff_y), max_y + border_ratio * abs(diff_y))
    ax.grid(True)

    # ---- UPDATE FUNCTION ----
    def update(frame):
        scale = scales[frame]

        # Update element lines
        for (line, element) in element_lines:
            node_i = element.node_i
            node_j = element.node_j

            xi0, yi0 = original_coords[node_i.id]
            xj0, yj0 = original_coords[node_j.id]

            di = nodal_displacements[node_i.id]
            dj = nodal_displacements[node_j.id]

            xi = xi0 + di[0] * scale
            yi = yi0 + di[1] * scale
            xj = xj0 + dj[0] * scale
            yj = yj0 + dj[1] * scale

            line.set_data([xi, xj], [yi, yj])

        # Update node positions
        for (point, node) in node_plots:
            x0, y0 = original_coords[node.id]
            d = nodal_displacements[node.id]

            x = x0 + d[0] * scale
            y = y0 + d[1] * scale

            point.set_data([x], [y])

        return [l[0] for l in element_lines] + [p[0] for p in node_plots]

    # --- ANIMATION ---
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=40,
        blit=True
    )

    plt.show()
