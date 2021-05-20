import math, pygame
from pygame.locals import *

class BasicSprite(pygame.sprite.Sprite):
    '''
    Basic sprite class. The sprite contains a Surface image, a Vector2 position /float orientation (in world coordinates), and a Vector2 pivot point (in local coordinates).
    This class expands upon pygamne.sprite.Sprite, allowing sprite rotation around the pivot point.
    '''
    def __init__(self, image, offset, pos=pygame.math.Vector2(0,0), angle=0, pivot_flag=False, *groups):
        super().__init__(*groups)
        self.original_image = image
        self.offset = pygame.math.Vector2(offset)
        self.pivot_flag = pivot_flag
        self.set_pose(position=pos, orientation=angle)

    def set_pose(self, **kwargs):
        '''
        Sets the sprite current world position/orientation.
        '''
        for key in kwargs:
            if key.lower() == 'position':
                self.position = kwargs[key]
            if key.lower() == 'orientation':
                self.orientation = kwargs[key]

        # Set the rotated image for blitting.
        self.image = pygame.transform.rotate(self.original_image, self.orientation)

        # Calculate the coordinates of the original topleft point in the rotated image.
        width, height = self.original_image.get_size()
        s, c = math.sin(math.radians(self.orientation)), math.cos(math.radians(self.orientation)) 
        original_topleft = pygame.math.Vector2( max([0, -s*height, -c*width, - s*height - c*width]), max([0, s*width, -c*height, s*width - c*height]) )

        # Calculate the translation of the pivot 
        pivot_offset = self.offset.rotate(-self.orientation) + original_topleft

        # Calculate the upper left origin of the rotated image
        # origin = (self.position[0] - self.offset[0] + min_x - pivot_move[0], self.position[1] - self.offset[1] - min_y + pivot_move[1])
        rect_origin = self.position - pivot_offset
        self.rect = self.image.get_rect(topleft=rect_origin)

        if self.pivot_flag:
            pygame.draw.line(self.image, Color("GREEN"), (pivot_offset[0]-20, pivot_offset[1]), (pivot_offset[0]+20, pivot_offset[1]), 3)
            pygame.draw.line(self.image, Color("GREEN"), (pivot_offset[0], pivot_offset[1]-20), (pivot_offset[0], pivot_offset[1]+20), 3)
        

    def update(self):
        pass


class BasicGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        pass
