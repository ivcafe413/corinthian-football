from abc import ABC, abstractmethod

class BaseObject(ABC):
    def __init__(self, dot_map):
        # Game Board-relative coordinates
        self.x = dot_map.x
        self.y = dot_map.y

        self.name = dot_map.name or self.__class__.__name__
        self.hp = dot_map.hp or 1
        
        self.info_list = ["name", "hp"] # List of parameters to display in informational panels

        self.render_mode = "texture" # 'texture', 'shape', 'sprite'
        self.text_texture = """0""" #

        self.selectable = True # Able to be left-click selected
        self.solid = True # Not able to path through if solid (right-click)

    @abstractmethod
    def update(self):
        """ Called each frame for Game Object to update itself """
        pass # Abstract

class Moveable(BaseObject):
    """ Game Object that is able to be moved (passed a vector for the next update)"""
    def __init__(self, dot_map):
        super().__init__(dot_map)
        self.moving_x = 0
        self.moving_y = 0

        self.speed = 10

    def move(self, dx: int, dy: int):
        """Additive pixel delta to move object X and Y.
        Can be called multiple times in one frame"""
        self.moving_x += dx
        self.moving_y += dy

    def move_to(self, x, y):
        """Target pixel move, uses delta move under the hood.
        Should only be called once per frame/update"""
        # Calculate the delta and move
        dx = x - self.x
        dy = y - self.y

        self.move(dx, dy)

    def partial_move(self, x: int, y: int):
        """Targeted partial pixel move. Attempts to move towards target.
        Limted by object speed (max pixels/move).
        Should only be called once per frame/update,
        and not in same update/frame if 'move_to' was called"""
        # Distance from target
        dist_x = abs(x - self.x)
        dist_y = abs(y - self.y)
        
        # Only step speed length if target is further away
        min_x = min(dist_x, self.speed)
        min_y = min(dist_y, self.speed)
        if x < self.x: min_x = -min_x
        if y < self.y: min_y = -min_y

        # move_x = self.x + min_x
        # move_y = self.y + min_y

        self.move(min_x, min_y)

    def update(self):
        if self.moving_x or self.moving_y: # If we're moving (at least one axis)
            self.x += self.moving_x
            self.y += self.moving_y
            # Reset the moving deltas to 0
            self.moving_x = 0
            self.moving_y = 0
        else: # Not moving
            # Do nothing for now
            super().update()

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

class DotBall(Moveable):
    def __init__(self, dot_map):
        super().__init__(dot_map)
        self.render_mode = "shape"

        self.selectable = False
        self.solid = False

    @property
    def shape(self):
        return "dot"

class SquareBlocker(Moveable):
    def __init__(self, dot_map):
        super().__init__(dot_map)
        self.render_mode = "shape"

    @property
    def shape(self):
        return "square"