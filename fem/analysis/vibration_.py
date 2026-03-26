class Load:
    def __init__(self, id_node, value_x, value_y, value_rxy):
        self.id_node = id_node
        self.value_x = value_x
        self.value_y = value_y
        self.value_rxy = value_rxy



class VibrationLoads:
    def __init__(self):
        self.loads = []

    def add_load(self, id_node, value_x, value_y, value_rxy):
        load = Load(id_node, value_x, value_y, value_rxy)
        self.loads.append(load)

#######

class Displacement:
    def __init__(self, id_node, value_x, value_y, value_rxy):
        self.id_node = id_node
        self.value_x = value_x
        self.value_y = value_y
        self.value_rxy = value_rxy


class VibrationDisplacements:
    def __init__(self):
        self.displacements = []

    def add_displacements(self, nodes,  value_x = 0, value_y = 0, value_rxy = 0):
        for i, node in enumerate(nodes):
            disp = Displacement(node, value_x, value_y, value_rxy)
            self.displacements.append(disp)




