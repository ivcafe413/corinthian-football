from objects.BaseObject import BaseObject

class Moveable(BaseObject):
    """ Game Object that is able to be moved (passed a vector for the next update)"""
    def __init__(self, dot_map):
        super().__init__(dot_map)
        self.moving_x = 0
        self.moving_y = 0

    def move(self, dx, dy):
        """Additive pixel delta to move object X and Y.
        Can be called multiple times in one frame"""
        self.moving_x += dx
        self.moving_y += dy

    def update(self):
        if self.moving_x or self.moving_y: # If we're moving (at least one axis)
            self.x += self.moving_x
            self.y += self.moving_y
            # Reset the moving deltas to 0
            self.moving_x = 0
            self.moving_y = 0
        else: # Not moving
            # Do nothing for now
            pass