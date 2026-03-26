from fem.analysis.stifness import stiffness_matrix
import numpy as np


def compute_dof(model):
    """
    Compute the degrees of freedom (DOF) for each node in a structural model.

    This function assigns sequential DOF indices to each node in the model.
    The number of DOFs per node depends on the type of elements in the model:
    - 3 DOFs per node if the model contains beam elements (e.g., [u_x, u_y, θ_z]).
    - 2 DOFs per node otherwise (e.g., [u_x, u_y]).

    Args:
        model: A model object containing:
            - `nodes`: A dictionary of node IDs.
            - `elements`: A dictionary of elements, each with an `el_type` attribute.

    Returns:
        tuple: (total_dof, dof_dict)
            - `total_dof`: Total number of DOFs in the model.
            - `dof_dict`: A dictionary mapping each node ID to its list of DOF indices.

    Example:
        >> elements = {1: Element('beam'), 2: Element('truss')}  # Mixed element types
        >> model = Model(nodes, elements)
        >> compute_dof(model)
            (9, {0: [0, 1, 2], 1: [3, 4, 5], 2: [6, 7, 8]})
    """
    largest_dof = 0
    dof_dict = {}  # dof for each node assign  dof-s

    # Decide global DOF per node based on model elements
    dof_per_node = 3 if any(e.el_type == 'beam' for e in model.elements.values()) else 2

    # Assign DOF-s sequentially to nodes
    for node_id in sorted(model.nodes):
        dof_dict[node_id] = list(range(largest_dof, largest_dof + dof_per_node))
        largest_dof += dof_per_node

    total_dof = largest_dof

    return total_dof, dof_dict


def assemble_stiffness(model, n, dof_dict):

    k_global = np.zeros((n,n))

    for element in model.elements.values():
        k = stiffness_matrix(element)
        element.stiffness_matrix = k

        if element.el_type == 'beam':
            dof_pn = 3
        elif element.el_type == 'truss':
            dof_pn = 2
        else:
            raise ValueError("Incorrect element type")

        node_i = element.node_i
        node_j = element.node_j

        # global DOF indices
        dofs_i = dof_dict[node_i.id]
        dofs_j = dof_dict[node_j.id]

        # assemble full element DOF list
        element_dofs = dofs_i[:dof_pn] + dofs_j[:dof_pn]

        # add to global matrix
        for a in range(len(element_dofs)):
            for b in range(len(element_dofs)):
                k_global[element_dofs[a], element_dofs[b]] += k[a, b]


    return k_global


def assemble_forces(model, n, dof_dict):

    global_force = np.zeros(n)

    for load in model.loads:
        node_id = load.id_node
        load_values = [load.value_x, load.value_y, load.value_rxy]

        dofs = dof_dict[node_id]

        for i in range(len(dofs)):
            global_force[dofs[i]] += load_values[i]

    return global_force


def assemble_spcs(model, n, dof_dict):
    global_spcs = np.zeros(n)

    for spc in model.spcs:
        node_id = spc.id_node
        spc_values = [spc.value_x, spc.value_y, spc.value_rxy]

        dofs = dof_dict[node_id]

        for i in range(len(dofs)):
            global_spcs[dofs[i]] += spc_values[i]

    return global_spcs


def assemble_spds(model, n, dof_dict):
    global_spds = np.zeros(n)

    for spd in model.spds:
        node_id = spd.id_node
        spd_values = [spd.value_x, spd.value_y, spd.value_rxy]

        dofs = dof_dict[node_id]

        for i in range(len(dofs)):
            global_spds[dofs[i]] += spd_values[i]

    return global_spds


def assemble_mass(model, n, dof_dict):
    # only a lumped mass so far, improvement needed

    mass_matrix = np.zeros([n,n])
    for node in model.nodes.values():
        mass  = node.m
        node_id = node.id
        dofs = dof_dict[node_id]
        for i in range(len(dofs)):
            mass_matrix[dofs[i], dofs[i]] = mass
    return mass_matrix



def assemble_vibration_forces(vibr_loads, n, dof_dict):
    """
    Assembles vibration forces into a container mapping DOFs to force values.

    Args:
        vibr_loads: List of vibration loads (each with id_node, value_x, value_y, value_rxy).
        n: Total number of DOFs.
        dof_dict: Maps node IDs to their DOF indices.

    Returns:
        ForceContainer: Object with `functions` dict: {dof_index: force_value}. Equal to 0 if no force is present.
    """

    class ForceContainer:
        def __init__(self, n):
            self.functions = {}  # Key: DOF index, Value: function

        def add_force(self, dof, func):
            self.functions[dof] = func

    force_container = ForceContainer(n)

    for i in range (0,n):
        force_container.add_force(i, 0)


    for load in vibr_loads:
        node_id = load.id_node
        dofs = dof_dict[node_id]
        load_values = [load.value_x, load.value_y, load.value_rxy]

        for i in range(len(dofs)):
            force_container.add_force(dofs[i], load_values[i])

    return force_container


def assemble_base(vibr_displacements, n, dof_dict):

    class DisplacementContainer:
        def __init__(self, n):
            self.functions = {}  # Key: DOF index, Value: function

        def add_displacement(self, dof, func):
            self.functions[dof] = func

    displacement_container = DisplacementContainer(n)
    global_spcs = np.zeros(n)

    for i in range (0,n):
        displacement_container.add_displacement(i, 0)


    for disp in vibr_displacements:
        node_id = disp.id_node
        dofs = dof_dict[node_id]
        load_values = [disp.value_x, disp.value_y, disp.value_rxy]

        for i in range(len(dofs)):
            displacement_container.add_displacement(dofs[i], load_values[i])


    # Mark DOFs that have a function
    for dof, val in displacement_container.functions.items():
        if callable(val):
            global_spcs[dof] = 1

    return displacement_container, global_spcs
