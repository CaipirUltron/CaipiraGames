import pygame, pymunk
from pygame.locals import *
from pygame.math import *

from classes.common import BasicSprite

class Ball(BasicSprite):
    def __init__(self, *groups):

        radius = 20
        image = pygame.Surface((2*radius,2*radius), pygame.SRCALPHA, 32)
        offset = (radius,radius)
        pygame.draw.circle( image, Color("RED"), offset, radius )
        super().__init__( image, offset, *groups )

        self.position = Vector2(0,800)

        self.body = pymunk.Body()
        self.body.position = ( self.position[0], self.position[1] )
        self.shape = pymunk.Circle(self.body, radius, (0,0))
        self.shape.mass = 10

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        self.position = Vector2(self.body.position)