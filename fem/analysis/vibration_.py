class Load:
    def __init__(self, id_node, value_x, value_y, value_rxy):
        self.id_node = id_node
        self.value_x = value_x
        self.value_y = value_y
        self.value_rxy = value_rxy



class Vibration_loads:
    def __init__(self):
        self.loads = []

    def add_load(self, id_node, value_x, value_y, value_rxy):
        load = Load(id_node, value_x, value_y, value_rxy)
        self.loads.append(load)