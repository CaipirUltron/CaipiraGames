import pygame
import sys, os, os.path

def get_sprites(sprite_folder):
    """ 
    Method for getting sprites from a given folder. Returns a list of 
    """
    sprites = []
    for file_name in os.listdir(sprite_folder):
        file_path = sprite_folder+"/"+file_name
        sprites.append( pygame.image.load(file_path) )
    return sprites

class Character():
    """ 
    Abstract class for general game character.
    General attributes are (x,y) positions, width and height, animation sprites, etc.
    """
    def __init__(self, sprite_folder, screen_res, deltaTime, x=0.0, y=0.0):
        self.sprite_folder = sprite_folder
        self.screen_resolution = screen_res
        self.deltaTime = deltaTime

        self.x, self.y = x, y
        self.speed_x, self.speed_y = 0.0, 0.0
        self.default_speed = 50.0

        self.idle_sprites = get_sprites(self.sprite_folder+"/idle")
        self.walk_sprites = get_sprites(self.sprite_folder+"/walk")

        self.current_sprite = self.idle_sprites[0]

        self.width = self.current_sprite.get_rect().size[0]
        self.height = self.current_sprite.get_rect().size[1]

    def get_position(self):
        return self.x, self.y

    def check_wall_collision(self):
        if self.x <= 0:
            self.x = 0.0
        elif self.x >= self.screen_resolution[0]-self.width:
            self.x = self.screen_resolution[0]-self.width
        if self.y <= 0:
            self.y = 0.0
        elif self.y >= self.screen_resolution[1]-self.height:
            self.y = self.screen_resolution[1]-self.height

    def set_speed(self, vel_x, vel_y):
        self.speed_x, self.speed_y = vel_x, vel_y

    def update(self):
        normalization_factor = ( self.speed_x**2 + self.speed_y**2 )**0.5
        if normalization_factor != 0.0:
            self.x += self.deltaTime*self.default_speed*self.speed_x/normalization_factor
            self.y += self.deltaTime*self.default_speed*self.speed_y/normalization_factor

        self.check_wall_collision()

    def draw(self, screen):
        screen.blit(self.current_sprite, (self.x, self.y) )


class Player(Character):
    """ 
    Class for the player character. The implementation of player controls can be found here.
    """
    def startMovement(self, pressed_key):
        if pressed_key == pygame.K_LEFT:
            self.speed_x += -1
        if pressed_key == pygame.K_RIGHT:
            self.speed_x += +1
        if pressed_key == pygame.K_UP:
            self.speed_y += -1
        if pressed_key == pygame.K_DOWN:
            self.speed_y += +1

    def endMovement(self, released_key):
        if released_key == pygame.K_LEFT:
            self.speed_x -= -1
        if released_key == pygame.K_RIGHT:
            self.speed_x -= +1
        if released_key == pygame.K_UP:
            self.speed_y -= -1
        if released_key == pygame.K_DOWN:
            self.speed_y -= +1

class Enemy(Character):
    """ 
    Class for an enemy character.
    The implementation of enemy controls and AI can be found here.
    """