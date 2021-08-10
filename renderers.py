import logging

import pygame
import pygame.draw
import pygame.display

from abc import ABC, abstractmethod
from objects import Renderable

COLOR_WHITE = (255, 255, 255)

class ObjectRenderer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def draw_game_object(self, surface: pygame.Surface, go: Renderable):
        """Called each time Driver calls to Renderer to draw the game object"""
        pass # Abstract

class ShapeRenderer(ObjectRenderer):
    def __init__(self):
        super().__init__()

    def draw_game_object(self, surface: pygame.Surface, go: Renderable):
        """Draws actor/game object based on shape definition.
        Draws actor w/ body and hand, facing a direction.
        Hand is defined as mini-version of body"""
        # TODO: Make Renderer a classed object, to precalculate render values
        # TODO: Setup pre-drawn surface for the object and simply blit over?
        body_center = (go.x + (go.w / 3), go.centery)
        if go.shape == "circle":
            body_radius = (go.w / 3)
            pygame.draw.circle(surface,
                COLOR_WHITE,
                body_center,
                body_radius,
                2 # line thickness
                )
        elif go.shape == "dot":
            pygame.draw.circle(surface,
                COLOR_WHITE,
                body_center,
                5, # radius
                0 # 0 means fill the circle (dot)
                )
        elif go.shape == "square":
            pygame.draw.rect(surface,
                COLOR_WHITE,
                pygame.Rect(go.x, go.y, go.w, go.h),
                0 # Fill the square
                )