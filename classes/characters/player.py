import pygame, math
from pygame.locals import *
from pygame.math import *

import pymunk
import pymunk.pygame_util

from classes.common import GameObject


class Player(GameObject):

    def __init__(self):
        image = pygame.image.load('./images/sprites/player/player.png')
        size = image.get_size()
        offset = (size[0]/2, size[1]/2)
        super().__init__(image, (offset))

        self.position = Vector2(0,1000)
        self.orientation = 0

        self.speed = 600*(1/60)
        self.range = self.position.length()

        self.body = pymunk.Body( body_type=pymunk.Body.KINEMATIC )
        self.body.position = (self.position.x, self.position.y)

        self.shape = pymunk.Poly.create_box(self.body, (30,40))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        left = pygame.key.get_pressed()[pygame.K_LEFT]
        right = pygame.key.get_pressed()[pygame.K_RIGHT]
        up = pygame.key.get_pressed()[pygame.K_UP]
        down = pygame.key.get_pressed()[pygame.K_DOWN]

        unit_radial = self.position.normalize()
        unit_left = unit_radial.rotate(90).normalize()

        if left or right:
            if left:
                self.position += unit_left*self.speed
            if right:
                self.position -= unit_left*self.speed
            self.orientation = math.degrees(math.atan2( self.position.x,self.position.y ))
            self.position.x = self.range*math.sin( math.radians(self.orientation) )
            self.position.y = self.range*math.cos( math.radians(self.orientation) )
        if up:
            self.position -= unit_radial*self.speed
        if down:
            self.position += unit_radial*self.speed
        self.range = self.position.length()

        self.body.position = (self.position.x, self.position.y)
        self.body.angle = -math.radians(self.orientation)