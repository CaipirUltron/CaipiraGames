import pygame, math
from pygame.locals import *
from pygame.math import *
from classes.basics import BasicSprite


class Player(BasicSprite):

    def __init__(self):
        image = pygame.image.load('./images/sprites/player/player.png')
        size = image.get_size()
        offset = (size[0]/2, size[1]/2)
        super().__init__(image, offset)

        self.speed = 600*(1/60)
        self.position = Vector2(0,800)
        self.orientation = 0
        self.range = self.position.length()

    def update(self):
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