from fem.analysis.stifness import stiffness_matrix


def assemble(model):
    for element in model.elements.values():
        k = stiffness_matrix(element, model.nodes)

    return k