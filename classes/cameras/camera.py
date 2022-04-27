import pygame, math
from pygame.math import *


def follow(camera):
    '''
    Simply follows the target with some vertical and horizontal offset. 
    '''
    hor_offset = 0
    ver_offset = -250
    camera.position = camera.target.position + Vector2(hor_offset, ver_offset).rotate(-camera.target.orientation)
    camera.orientation = camera.target.orientation

def fixed(camera):
    '''
    A fixed camera with some vertical and horizontal offset. 
    '''
    hor_offset = 0
    ver_offset = 0
    camera.position = Vector2(hor_offset, ver_offset)

class Camera():
    '''
    Base class for a simple camera. 
    Members:
    (i)   Target sprite to be followed
    (ii)  Screen size
    (iii) Camera position at the screen center (world frame)
    (iv)  Camera orientation                   (world frame)
    '''
    def __init__(self, target, camera_method, screen_size, pos=Vector2(0,0), angle=0):
        self.target = target
        self.camera_method = camera_method
        self.screen_size = screen_size

        self.position = pos
        self.orientation = angle

    def screen2world(self, screen_pos):
        '''
        Converts position in the screen coordinates to world coordinates.
        Useful for clickable objects.
        '''
        world_pos = ( Vector2(screen_pos) - Vector2(self.screen_size)/2 ).rotate( -self.orientation ) + self.position
        return world_pos

    def world2screen(self, world_pos):
        '''
        Converts position in the world coordinates to screen coordinates.
        '''
        screen_pos = ( Vector2(world_pos) - self.position ).rotate( self.orientation ) + Vector2(self.screen_size)/2
        return screen_pos

    def transform(self, sprite):
        '''
        Converts sprite with world coordinates to image and rect in screen coordinates.
        Used to implement the camera scroll.
        '''
        # Computes the position and orientation of the sprite in camera coordinates.
        # position_wrt_cam = ( Vector2(sprite.position) - self.position ).rotate( self.orientation ) + Vector2(self.screen_size)/2
        position_wrt_cam = self.world2screen(sprite.position)
        orientation_wrt_cam = sprite.orientation - self.orientation

        # Calculate the coordinates of the original topleft point in the rotated image.
        width, height = sprite.image.get_size()
        s, c = math.sin(math.radians(orientation_wrt_cam)), math.cos(math.radians(orientation_wrt_cam)) 
        original_topleft = Vector2( max([0, -s*height, -c*width, - s*height - c*width]), max([0, s*width, -c*height, s*width - c*height]) )

        # Convert the offset point to coordinates on the new rotated image
        pivot_offset = sprite.offset.rotate(-orientation_wrt_cam) + original_topleft

        # Apply the corrected pivot offset to the Sprite rect, to correctly represent the Sprite position in the world wrt to the pivot point
        rect_origin = position_wrt_cam - pivot_offset

        # Transformed image and rect
        transformed_image = pygame.transform.rotate(sprite.image, orientation_wrt_cam)
        transformed_rect = sprite.image.get_rect(topleft=rect_origin)

        return transformed_image, transformed_rect

    def update(self):
        '''
        Updates the state of the camera. For now, it just follows the target position/orientation
        TO DO: expand this method to more complex camera behaviours.
        '''
        self.state = self.camera_method(self)