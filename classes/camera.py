import pygame, math
import numpy as np
from pygame.locals import *

HD720_RESOLUTION = (1280,720)

class Camera():
    '''
    Base class for a simple camera.
    '''
    def __init__(self):
        self.position = np.array([0,0])
        self.angle = 0.0
        
    def transform(self, sprite):
        transformed_angle = sprite.angle - self.angle
        transformed_img = pygame.transform.rotate(sprite.image, transformed_angle)
        camera_pos = self.rot(math.radians(self.angle)).T.dot( np.array(sprite.rect.center) - self.position ) + np.array(HD720_RESOLUTION)/2
        transformed_rect = transformed_img.get_rect(center=camera_pos.tolist())
        return transformed_img, transformed_rect
        
    def update(self, target):
        self.position = np.array(target.rect.center)
        self.angle = 0.0

    def rot(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[c,-s],[s,c]])


class CameraAwareGroup(pygame.sprite.Group):
    def __init__(self, target):
        super().__init__()
        self.camera = Camera()
        self.target = target
        if self.target:
            self.add( self.target )

    def update(self, *args):
        super().update(*args)
        self.camera.update(self.target)

    def draw(self, surface):
        for sprite in self.sprites():
            transf_img, transf_rect = self.camera.transform(sprite)
            surface.blit( transf_img, transf_rect )