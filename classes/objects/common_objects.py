import pygame, pymunk, math
from pygame.locals import *
from pygame.math import *

from classes.common import GameObject, Arc, to_polar

class Background(GameObject):
    '''
    Tile map background sprite.
    '''
    def __init__(self, *groups):
        self._layer = -1
        image = pygame.transform.scale(pygame.image.load("images/sprites/bg/axis.png"), (1200,1200) ).convert_alpha()
        img_size = image.get_size()
        super().__init__(image, offset=(img_size[0]/2, img_size[1]/2), *groups)

class Ball(GameObject):
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
        self.orientation = self.body.angle

# ------------------------------------------------- Code before MAJOR REFACTOR ---------------------------------------------------

class CurvedTile(GameObject):
    '''
    Basic curved tile.
    '''
    def __init__(self, radius, height, angular_width, angle=0, color=pygame.Color("RED"), *groups):
        self._layer = -1

        # Tile parameters
        self.arc = Arc( Vector2(0,0), radius, height, angular_width ) # tile arc
        self.color = color                                            # tile color

        # Initialize BasicSprite surface
        image = pygame.Surface( ( self.arc.rect.width, self.arc.rect.height ), pygame.SRCALPHA)
        offset = ( self.arc.rect.width/2, self.arc.distortion - self.arc.radius )
        super().__init__(image, offset, orientation=angle, *groups)

        # Draws sprite
        self.arc.draw_arc(image, self.color, fill=True)
        
        # Physics
        self.body = pymunk.Body( body_type=pymunk.Body.STATIC )

        topleft_x = self.arc.radius*math.sin( math.radians(self.orientation-self.arc.angular_width/2) )
        topleft_y = self.arc.radius*math.cos( math.radians(self.orientation-self.arc.angular_width/2) )

        topright_x = self.arc.radius*math.sin( math.radians(self.orientation+self.arc.angular_width/2) )
        topright_y = self.arc.radius*math.cos( math.radians(self.orientation+self.arc.angular_width/2) )

        bottonleft_x = (self.arc.radius+self.arc.height)*math.sin( math.radians(self.orientation-self.arc.angular_width/2) )
        bottonleft_y = (self.arc.radius+self.arc.height)*math.cos( math.radians(self.orientation-self.arc.angular_width/2) )

        bottonright_x = (self.arc.radius+self.arc.height)*math.sin( math.radians(self.orientation+self.arc.angular_width/2) )
        bottonright_y = (self.arc.radius+self.arc.height)*math.cos( math.radians(self.orientation+self.arc.angular_width/2) )

        self.topleft = ( topleft_x, topleft_y )
        self.topright = ( topright_x, topright_y )
        self.bottonleft = ( bottonleft_x, bottonleft_y )
        self.bottonright = ( bottonright_x, bottonright_y )

        self.shape = pymunk.Poly(self.body, [ self.topleft, self.topright, self.bottonright, self.bottonleft ])
        self.shape.color = Color("RED")

    def collidepoint(self, world_x, world_y):
        '''
        Checks if given world position is inside the tile.
        '''
        radius, angle = to_polar(world_x, world_y)
        is_in_radius = ( radius >= self.arc.radius ) and ( radius < self.arc.radius + self.arc.height )
        is_in_angle = ( angle >= self.orientation - self.arc.angular_width/2 ) and ( angle < self.orientation + self.arc.angular_width/2 )
        if is_in_radius and is_in_angle:
            return True
        else:
            return False