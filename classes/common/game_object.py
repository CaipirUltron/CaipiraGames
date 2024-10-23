import math, pygame, pymunk
from pygame.locals import *
from pygame.math import *

class GameObject(pygame.sprite.Sprite):
    '''
    This class expands upon pygame.sprite.Sprite, allowing sprite rotation around a pivot point.
    Members:
    (i)   Surface image
    (ii)  offset to position  (local coordinates)
    (iii) Vector2 position    (world coordinates)
    (iv)  float orientation   (world coordinates)
    '''
    def __init__(self, image, offset=(0,0), position=(0,0), orientation=0, layer=-1, *groups):
        super().__init__(*groups)

        self.image = image
        self.rect = self.image.get_rect()

        self.offset = Vector2(offset)
        self.position = Vector2(position)
        self.orientation = orientation
        self._layer = layer

    def topleft(self):
        '''
        Compute top left position of the sprite
        '''

    def topright(self):
        '''
        Compute top right position of the sprite
        '''

    def bottomleft(self):
        '''
        Compute bottom left position of the sprite
        '''

    def bottomright(self):
        '''
        Compute bottom right position of the sprite
        '''

    def center(self):
        '''
        Compute center position of the sprite
        '''

class GameObjectGroup(pygame.sprite.LayeredUpdates):
    '''
    Adds camera functionality to pygame.sprite.Group
    Adds physics support to the sprites.
    '''
    def __init__(self, camera, space):
        self.space = space                       # reference to the space that will be used to compute physics
        super().__init__()
        self.camera = camera

    def add(self, *sprites):
        '''
        Add sprite body and shape to space.
        '''
        super().add(*sprites)
        if self.space:
            for sprite in sprites:
                if hasattr(sprite, 'body') and hasattr(sprite, 'shape'):
                    self.space.add(sprite.body, sprite.shape)

    def remove(self, *sprites):
        '''
        Remove sprite body and shape to space.
        '''
        super().remove(*sprites)
        for sprite in sprites:
            if hasattr(sprite, 'body') and hasattr(sprite, 'shape'):
                self.space.remove(sprite.body, sprite.shape)

    def update(self, *args, **kwargs):
        '''
        Updates the sprites and the camera. 
        '''
        super().update(*args, **kwargs)
        self.camera.update()

    def draw(self, surface):
        '''
        Overrides the draw method of LayeredUpdates() to take the camera state into account.
        The change here from LayeredUpdates() is the "transf_img, transf_rect = self.camera.transform(sprite)" line,
        which transforms the image and its rect according to the camera state before blitting.
        '''
        dirty = self.lostsprites
        self.lostsprites = []
        for sprite in self.sprites():
            rect = self.spritedict[sprite]
            transf_img, transf_rect = self.camera.transform(sprite)
            new_rect = surface.blit( transf_img, transf_rect )
            if rect is self._init_rect:
                dirty.append(new_rect)
            else:
                if new_rect.colliderect(rect):
                    dirty.append(new_rect.union(rect))
                else:
                    dirty.append(new_rect)
                    dirty.append(rect)
            self.spritedict[sprite] = new_rect
            sprite.rect = new_rect
        return dirty
    
# ------------------------------------------------- Code before MAJOR REFACTOR ---------------------------------------------------

def to_polar(x, y):
    '''
    Converts cartesian coords (x,y) to polar coords (radius, angle).
    '''
    radius = math.sqrt( x**2 + y**2 )
    angle = math.degrees(math.atan2( x,y ))
    if angle < 0:
        angle += 360
    return radius, angle

class Arc():
    '''
    Class for solid arcs. position is the topleft position of the smallest Rect containing the Arc.
    A solid arc can be identified by three parameters: arc radius, arc height and arc angular width, or angle.
    '''
    def __init__(self, center, radius, height, angular_width):

        # Arc parameters
        self.center = center                   # center coordinates
        self.radius = radius                   # radius
        self.height = height                   # height
        self.angular_width = angular_width     # angular width (arc angle)

        # Compute necessary dimensions for the rect
        self.distortion = self.radius*( 1 -math.cos( ( math.radians(self.angular_width)/2 ) ) )
        rect_width = 2*( self.radius + self.height )*math.sin(math.radians(self.angular_width)/2)
        rect_height = self.distortion + self.height

        topleft = Vector2( center.x - rect_width/2, center.y + self.radius - self.distortion )
        self.rect = pygame.Rect( topleft, (rect_width, rect_height) )

    def draw_arc(self, surface, color, resolution=20, fill=False):

        points = []
        centerx = self.rect.width/2
        centery = self.distortion - self.radius
        for i in range(resolution+1):
            x = centerx + self.radius*math.sin( (i-resolution/2)*(math.radians(self.angular_width)/resolution) )
            y = centery + self.radius*math.cos( (i-resolution/2)*(math.radians(self.angular_width)/resolution) )
            points.append( (x,y) )
        for i in range(resolution+1):
            x = centerx + ( self.radius + self.height )*math.sin( -(i-resolution/2)*(math.radians(self.angular_width)/resolution) )
            y = centery + ( self.radius + self.height )*math.cos( -(i-resolution/2)*(math.radians(self.angular_width)/resolution) )
            points.append( (x,y) )
        if fill:
            pygame.draw.polygon( surface, color, points )
        else:
            pygame.draw.lines( surface, color, True, points )

    def __str__(self):
        return "<x: %s, y: %s, radius:%s height:%s arc width:%s>" % (self.radius, self.height, self.angular_width)