import os
import pygame

class Character():
    """ 
    Abstract class for general game character.
    General attributes are (x,y) positions, width and height, animation sprites, etc.
    """
    def __init__(self, sprite_folder, deltaTime, x=0.0, y=0.0):
        self.sprite_folder = sprite_folder
        self.deltaTime = deltaTime

        self.x, self.y = x, y
        self.speed_x, self.speed_y = 0.0, 0.0

        self.idle_sprites = get_sprites(self.sprite_folder+"/idle")
        self.walk_sprites = get_sprites(self.sprite_folder+"/walk")

        self.current_sprite = self.idle_sprites[0]

        self.rect = self.current_sprite.get_rect()
        self.rect.center = (self.x, self.y)

        self.width = self.rect.size[0]
        self.height = self.rect.size[1]

        self.k = 1.0

    def get_position(self):
        return self.x, self.y

    # def check_wall_collision(self):
    #     if self.x <= 0:
    #         self.x = 0.0
    #     elif self.x >= self.screen_resolution[0]-self.width:
    #         self.x = self.screen_resolution[0]-self.width
    #     if self.y <= 0:
    #         self.y = 0.0
    #     elif self.y >= self.screen_resolution[1]-self.height:
    #         self.y = self.screen_resolution[1]-self.height

    def set_speed(self, vel_x, vel_y):
        self.speed_x, self.speed_y = vel_x, vel_y

    def update(self):
        self.x += self.deltaTime*self.speed_x
        self.y += self.deltaTime*self.speed_y

        # normalization_factor = ( self.speed_x**2 + self.speed_y**2 )**0.5
        # if normalization_factor != 0.0:            
            # self.x += self.deltaTime*self.default_speed*self.speed_x/normalization_factor
            # self.y += self.deltaTime*self.default_speed*self.speed_y/normalization_factor
        self.rect.center = (self.x, self.y)
        # self.check_wall_collision()

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)

def get_sprites(sprite_folder):
    """ 
    Method for getting sprites from a given folder. Returns a list of 
    """
    sprites = []
    for file_name in os.listdir(sprite_folder):
        file_path = sprite_folder+"/"+file_name
        sprites.append( pygame.image.load(file_path) )
    return sprites
