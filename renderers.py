import logging

import pygame
import pygame.draw
import pygame.display

from abc import ABC, abstractmethod
# from objects import Renderable

class ObjectRenderer(ABC):
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def draw_game_object(self, surface: pygame.Surface, rect: pygame.Rect):
        """Called each time Driver calls to Renderer to draw the game object"""
        pass # Abstract

class ShapeRenderer(ObjectRenderer):
    def __init__(self, color, shape):
        super().__init__(color)
        self.shape = shape

    def draw_game_object(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draws actor/game object based on shape definition.
        Draws actor w/ body and hand, facing a direction.
        Hand is defined as mini-version of body"""
        # TODO: Make Renderer a classed object, to precalculate render values
        # TODO: Setup pre-drawn surface for the object and simply blit over?
        body_center = (rect.x + (rect.w / 3), rect.centery)
        if self.shape == "circle":
            body_radius = (rect.w / 3)
            pygame.draw.circle(surface,
                self.color,
                body_center,
                body_radius,
                2 # line thickness
                )
        elif self.shape == "dot":
            pygame.draw.circle(surface,
                self.color,
                body_center,
                5, # radius
                0 # 0 means fill the circle (dot)
                )
        elif self.shape == "square":
            pygame.draw.rect(surface,
                self.color,
                pygame.Rect(rect.x, rect.y, rect.w, rect.h),
                0 # Fill the square
                )