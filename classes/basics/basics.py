import math, pygame
from pygame.locals import *
from classes.cameras import Camera

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