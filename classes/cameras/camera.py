import pygame, math
import numpy as np
from pygame.locals import *

class Camera():
    '''
    Base class for a simple camera. 
    Holds the camera position and orientation wrt to the world frame, and performs the required coordinates transformations.
    '''
    def __init__(self, screen_size):
        self.position = np.array([0,0])
        self.angle = 0.0
        self.screen_size = screen_size

    def from_camera(self, pos):
        '''
        Converts position in the screen coordinates to world coordinates. Useful for clickable objects.
        '''
        world_pos = self.rot(math.radians(self.angle)).dot( np.array(pos) - np.array(self.screen_size)/2 ) + self.position
        return world_pos.tolist()

    def transform(self, sprite):
        '''
        Converts a sprite with world coordinates to image and rect in screen coordinates.
        Used to convert the sprites coordinates to the screen, effectivelly implementing the camera scroll.
        '''
        transformed_angle = sprite.angle - self.angle
        transformed_img = pygame.transform.rotate(sprite.image, transformed_angle)
        camera_pos = self.rot(math.radians(self.angle)).T.dot( np.array(sprite.rect.center) - self.position ) + np.array(self.screen_size)/2
        transformed_rect = transformed_img.get_rect(center=camera_pos.tolist())
        return transformed_img, transformed_rect
        
    def update(self, target):
        '''
        Sets a target for the camera to follow, and specifies its behavior.
        '''
        self.position = np.array(target.rect.center)
        # self.angle = target.angle
        self.angle = 0.0

        if self.angle < 0:
            self.angle += 2*math.pi

    def rot(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        return np.array([[c,-s],[s,c]])


class CameraAwareGroup(pygame.sprite.Group):
    def __init__(self, target, screen_size):
        super().__init__()
        self.camera = Camera(screen_size)
        self.target = target
        if self.target:
            self.add( self.target )

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.camera.update(self.target)

        # for key, value in kwargs.items():
        #     if key == "":

    def draw(self, surface):
        for sprite in self.sprites():
            transf_img, transf_rect = self.camera.transform(sprite)
            surface.blit( transf_img, transf_rect )