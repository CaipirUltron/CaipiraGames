import math, pygame
from pygame.locals import *
from pygame.math import *

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
            # print(start_points)
            pygame.draw.lines( surface, color, True, points )

    def __str__(self):
        return "<x: %s, y: %s, radius:%s height:%s arc width:%s>" % (self.radius, self.height, self.angular_width)


class BasicSprite(pygame.sprite.Sprite):
    '''
    This class expands upon pygamne.sprite.Sprite, allowing sprite rotation around a pivot point.
    Mmebers:
    (i)   Surface image
    (ii)  Vector2 position    (world coordinates)
    (iii) float orientation   (world coordinates)
    (iv)  Vector2 pivot point (local coordinates)
    '''
    def __init__(self, image, offset, position=pygame.math.Vector2(0,0), orientation=0, pivot_flag=False, *groups):
        super().__init__(*groups)
        self.image = image
        self.offset = pygame.math.Vector2(offset)
        self.pivot_flag = pivot_flag
        self.set_pose(position=position, orientation=orientation)

    def set_pose(self, **kwargs):
        '''
        Sets the sprite current world position/orientation.
        '''
        for key in kwargs:
            if key.lower() == 'position':
                self.position = kwargs[key]
            if key.lower() == 'orientation':
                self.orientation = kwargs[key]


class BasicGroup(pygame.sprite.LayeredUpdates):
    '''
    Adds camera functionality to pygame.sprite.Group. 
    '''
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        if self.camera.target:
            self.add( self.camera.target )

    def update(self, *args, **kwargs):
        '''
        Updates the sprites and the camera. 
        '''
        super().update(*args, **kwargs)
        self.camera.update()

    def draw(self, surface):
        '''
        Overrides the draw method of LayeredUpdates to take the camera state into account.
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
        return dirty