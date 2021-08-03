from objects.Moveable import Moveable

class CircleCarrier(Moveable):
    def __init__(self, dot_map):
        super().__init__(dot_map)
        self.render_mode = "shape"

    @property
    def shape(self):
        return "circle"

    def update(self):
        # Inherited from super class, need to call supermethod in proper order
        super().update()