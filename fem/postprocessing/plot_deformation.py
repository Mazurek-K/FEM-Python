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
    nodal_displacements = result.nodal_displacements # [x,y,rot]
    plt.figure()

    # Assign new positions to nodes in the model , also a rotation
    for node_id, node_prop in model.nodes.items():
        node_disp  = nodal_displacements[node_id]

        # node_prop.x = node_prop.x + node_disp[0] * scale_factor
        node_prop.x_disp_scal = node_disp[0] * scale_factor
        # node_prop.y = node_prop.y + node_disp[1] * scale_factor
        node_prop.y_disp_scal = node_disp[1] * scale_factor
        node_prop.rot_scal = node_disp[2] * scale_factor

    # Plot elements
    for element in model.elements.values():

        node_i = element.node_i
        node_j = element.node_j
        el_len = np.sqrt((node_j.x - node_i.x)**2 + (node_j.y - node_i.y)**2 )

        # Project onto the undeformed element
        undef = [(node_j.x - node_i.x)/el_len , (node_j.y - node_i.y)/el_len ]
        i_disp = [node_i.x_disp_scal, node_i.y_disp_scal]
        j_disp = [node_j.x_disp_scal, node_j.y_disp_scal]
        proj_i_x = np.dot(i_disp, undef)
        proj_j_x = np.dot(j_disp, undef)

        normal = [-undef[1], undef[0]]
        proj_i_y = np.dot(i_disp, normal)
        proj_j_y = np.dot(j_disp, normal)

        def N1(x, L):
            return 1 - 3 * (x / L) ** 2 + 2 * (x / L) ** 3

        def N2(x, L):
            return x * (1 - x / L) ** 2

        def N3(x, L):
            return 3 * (x / L) ** 2 - 2 * (x / L) ** 3

        def N4(x, L):
            return (x**2 / L) * (x/L - 1)

        if element.el_type == 'beam':
            color = 'r'
            n_points = 10
            s = np.linspace(0, el_len, n_points)  # along the length

            # local displacements
            v1 = proj_i_y
            v2 = proj_j_y
            theta1 = node_i.rot_scal
            theta2 = node_j.rot_scal

            v_local = (v1 * N1(s, el_len) - theta1 * N2(s, el_len) +  # minus signs!!!
                       v2 * N3(s, el_len) - theta2 * N4(s, el_len))

            # To be reviewed (some AI help)
            x_axial = np.linspace(node_i.x + proj_i_x * undef[0], node_j.x + proj_j_x * undef[0], n_points)
            y_axial = np.linspace(node_i.y + proj_i_x * undef[1], node_j.y + proj_j_x * undef[1], n_points)

            x_def = x_axial + v_local * normal[0]
            y_def = y_axial + v_local * normal[1]

            plt.plot(x_def, y_def, color)

        else:
            color = 'b'
            x = [node_i.x + node_i.x_disp_scal, node_j.x + node_j.x_disp_scal]
            y = [node_i.y + node_i.y_disp_scal, node_j.y + node_j.y_disp_scal]

            plt.plot(x, y, color)

    # Plot nodes
    for node in model.nodes.values():
        plt.plot(node.x + node.x_disp_scal, node.y + node.y_disp_scal, 'o')
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


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def animate_static_v2(result, max_scale=10, n_frames=60):
    model = result.model
    nodal_displacements = result.nodal_displacements

    # Pre-define Shape Functions
    def N1(xi):
        return 1 - 3 * xi ** 2 + 2 * xi ** 3

    def N2(xi, L):
        return L * xi * (1 - xi) ** 2

    def N3(xi):
        return 3 * xi ** 2 - 2 * xi ** 3

    def N4(xi, L):
        return L * (xi ** 3 - xi ** 2)

    fig, ax = plt.subplots()
    scales = max_scale * np.sin(np.linspace(0, np.pi, n_frames))

    element_data = []  # Stores (line_object, element, points_count)

    # ---- INITIAL DRAW ----
    for element in model.elements.values():
        color = 'r' if element.el_type == 'beam' else 'b'
        n_pts = 30 if element.el_type == 'beam' else 2
        line, = ax.plot([], [], color, lw=1.5)
        element_data.append((line, element, n_pts))

    node_plots = []
    for node in model.nodes.values():
        point, = ax.plot([], [], 'ko', ms=4)
        node_plots.append((point, node))

    # Static plot setup
    all_x = [n.x for n in model.nodes.values()]
    all_y = [n.y for n in model.nodes.values()]
    pad_x, pad_y = 0.2 * (max(all_x) - min(all_x) or 1), 0.2 * (max(all_y) - min(all_y) or 1)
    ax.set_xlim(min(all_x) - pad_x, max(all_x) + pad_x)
    ax.set_ylim(min(all_y) - pad_y-500, max(all_y) + pad_y+500)
    ax.set_aspect('equal')
    ax.grid(True)

    # ---- UPDATE FUNCTION ----
    def update(frame):
        scale = scales[frame]
        updated_artists = []

        for line, element, n_pts in element_data:
            ni, nj = element.node_i, element.node_j
            di, dj = nodal_displacements[ni.id], nodal_displacements[nj.id]
            L = np.sqrt((nj.x - ni.x) ** 2 + (nj.y - ni.y) ** 2)

            # Local vectors
            t = np.array([(nj.x - ni.x) / L, (nj.y - ni.y) / L])  # Tangent
            n_vec = np.array([-t[1], t[0]])  # Normal

            if element.el_type == 'beam':
                xi_vals = np.linspace(0, 1, n_pts)
                s = xi_vals * L

                # Project scaled displacements to local normal (v) and tangent (u_axial)
                v1, v2 = np.dot(di[:2], n_vec) * scale, np.dot(dj[:2], n_vec) * scale
                u1a, u2a = np.dot(di[:2], t) * scale, np.dot(dj[:2], t) * scale

                # Apply rotation fix (- sign)
                th1, th2 = di[2] * scale, dj[2] * scale

                # Calculate transverse deflection
                v_local = (v1 * N1(xi_vals) - th1 * N2(xi_vals, L) +
                           v2 * N3(xi_vals) - th2 * N4(xi_vals, L))

                # Coordinates: Base + Axial + Transverse
                x_pts = (ni.x + s * t[0]) + (u1a * (1 - xi_vals) + u2a * xi_vals) * t[0] + v_local * n_vec[0]
                y_pts = (ni.y + s * t[1]) + (u1a * (1 - xi_vals) + u2a * xi_vals) * t[1] + v_local * n_vec[1]
                line.set_data(x_pts, y_pts)
            else:
                # Simple truss/line
                xi = [0, 1]
                x_pts = [ni.x + di[0] * scale, nj.x + dj[0] * scale]
                y_pts = [ni.y + di[1] * scale, nj.y + dj[1] * scale]
                line.set_data(x_pts, y_pts)

            updated_artists.append(line)

        for point, node in node_plots:
            d = nodal_displacements[node.id]
            point.set_data([node.x + d[0] * scale], [node.y + d[1] * scale])
            updated_artists.append(point)

        return updated_artists

    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=40, blit=True)
    plt.show()


def animate_static(result, max_scale=10, n_frames=60):
    model = result.model
    nodal_displacements = result.nodal_displacements
    fig, ax = plt.subplots()

    # Pre-calculate limits
    all_x = [n.x for n in model.nodes.values()]
    all_y = [n.y for n in model.nodes.values()]
    pad = 0.2 * max(max(all_x) - min(all_x), max(all_y) - min(all_y), 1.0)
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)
    ax.set_aspect('equal')
    ax.grid(True)

    scales = max_scale * np.sin(np.linspace(0, np.pi, n_frames))

    # Lists to store plot objects (Artists)
    element_artists = []
    node_artists = []

    # ---- INITIAL DRAW ----
    for element in model.elements.values():
        color = 'r' if element.el_type == 'beam' else 'b'
        # Draw empty lines to be updated later
        line, = ax.plot([], [], color, lw=1.5)
        element_artists.append((line, element))

    for node in model.nodes.values():
        point, = ax.plot([], [], 'ko', ms=4)
        node_artists.append((point, node))

    # ---- UPDATE FUNCTION ----
    def update(frame):
        current_scale = scales[frame]

        # 1. Update Elements
        for line, element in element_artists:
            ni, nj = element.node_i, element.node_j
            di = nodal_displacements[ni.id] * current_scale
            dj = nodal_displacements[nj.id] * current_scale

            if element.el_type == 'beam':
                L = np.sqrt((nj.x - ni.x) ** 2 + (nj.y - ni.y) ** 2)
                t = np.array([(nj.x - ni.x) / L, (nj.y - ni.y) / L])  # Tangent
                n_vec = np.array([-t[1], t[0]])  # Normal CCW

                # Project displacements to local normal
                v1, v2 = np.dot(di[:2], n_vec), np.dot(dj[:2], n_vec)
                # Rotations (with sign fix for CCW normal)
                th1, th2 = di[2], dj[2]

                s = np.linspace(0, L, 30)
                xi = s / L

                # Hermite Shape Functions with Rotation Sign Fix (-)
                v_local = (v1 * (1 - 3 * xi ** 2 + 2 * xi ** 3) -
                           th1 * (s * (1 - xi) ** 2) +
                           v2 * (3 * xi ** 2 - 2 * xi ** 3) -
                           th2 * (s * (xi ** 2 - xi)))

                # Calculate global positions (Base chord + Transverse)
                x_base = np.linspace(ni.x + di[0], nj.x + dj[0], 30)
                y_base = np.linspace(ni.y + di[1], nj.y + dj[1], 30)

                line.set_data(x_base + v_local * n_vec[0],
                              y_base + v_local * n_vec[1])
            else:
                # Truss/Link
                line.set_data([ni.x + di[0], nj.x + dj[0]],
                              [ni.y + di[1], nj.y + dj[1]])

        # 2. Update Nodes
        for point, node in node_artists:
            d = nodal_displacements[node.id] * current_scale
            point.set_data([node.x + d[0]], [node.y + d[1]])

        # Return all updated objects for blitting
        return [item[0] for item in element_artists] + [item[0] for item in node_artists]

    # --- ANIMATION ---
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=50, blit=True)
    plt.show()
    return ani  # Keep reference to prevent garbage collection


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
