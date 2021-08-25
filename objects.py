import logging

from abc import ABC, abstractmethod
from pygame import Rect
from renderers import ObjectRenderer

class BaseObject(ABC, Rect):
    def __init__(self, x, y, w, h, **kwargs):
        # logging.info(kwargs)
        # Game Board-relative coordinates
        Rect.__init__(self, x, y, w, h)
        # self.x = dot_map.x
        # self.y = dot_map.y

        self.name = kwargs.get("name", self.__class__.__name__)
        
        self.info_list = ["name"] # List of parameters to display in informational panels

        self.render_mode = "texture" # 'texture', 'shape', 'sprite'
        self.text_texture = """0""" #

        self.selectable = True # Able to be left-click selected
        self.solid = True # Not able to path through if solid (right-click)

        self.can_carry = False
        self.carrying = None

    def __hash__(self):
        return id(self)

    @abstractmethod
    def update(self):
        """Called each frame for Game Object to update itself"""
        pass # Abstract

class Moveable(BaseObject):
    """ Game Object that is able to be moved (passed a vector for the next update)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.moving_x = 0
        self.moving_y = 0

        self.speed = 10
        self.movement_range = 5

    def move(self, dx: int, dy: int):
        """Additive pixel delta to move object X and Y.
        Can be called multiple times in one frame"""
        self.moving_x += dx
        self.moving_y += dy
        # If we're carrying something, move it as well
        if(self.carrying is not None):
            self.carrying.move(dx, dy)

    def move_to(self, x: int, y: int):
        """Target pixel move, uses delta move under the hood.
        Should only be called once per frame/update.
        Tuple would need to be unpacked for usage"""
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

class Renderable(BaseObject):
    def __init__(self, render_mode: str, shape="circle", **kwargs):
        super().__init__(**kwargs) # Handled by MRO
        self.render_mode = render_mode
        self.shape = shape

        self.renderer = None # type: ObjectRenderer

    def draw(self, surface):
        self.renderer.draw_game_object(surface, self)

class Carrier(Moveable, Renderable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.can_carry = True

class Ball(Moveable, Renderable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selectable = False
        self.solid = False

class Blocker(Moveable, Renderable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
