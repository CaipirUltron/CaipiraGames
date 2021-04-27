import os, os.path
import pygame as pg

DEFAULT_CHAR_SPEED = 100

def get_sprites(sprite_folder):
    """ 
    Method for getting sprites from a given folder.
    """
    sprites = []
    for file_name in os.listdir(sprite_folder):
        file_path = sprite_folder+"/"+file_name
        sprites.append( pg.image.load(file_path) )
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

        self.x = x
        self.y = y

        self.speed_x = 0.0
        self.speed_y = 0.0

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

    def move(self, vel_x, vel_y):
        self.speed_x = vel_x
        self.speed_y = vel_y
        print(self.x, self.y)
        self.update_position()

    def update_position(self):
        # keys = pg.key.get_pressed()

        # speed_x = 0.0
        # speed_y = 0.0
        # if keys[pg.K_LEFT]:
        #     speed_x = -1.0
        # if keys[pg.K_RIGHT]:
        #     speed_x = +1.0
        # if keys[pg.K_UP]:
        #     speed_y = -1.0
        # if keys[pg.K_DOWN]:
        #     speed_y = +1.0

        normalization_factor = ( self.speed_x**2 + self.speed_y**2 )**0.5
        if normalization_factor != 0.0:
            self.x += self.deltaTime*DEFAULT_CHAR_SPEED*self.speed_x/normalization_factor
            self.y += self.deltaTime*DEFAULT_CHAR_SPEED*self.speed_y/normalization_factor

        self.check_wall_collision()

    def draw(self, screen):
        self.update_position()
        screen.blit(self.current_sprite, (self.x, self.y) )

class Player(Character):
    """ 
    Class for the player character.
    The implementation of player controls can be found here.
    """

class Enemy(Character):
    """ 
    Class for an enemy character.
    The implementation of enemy controls and AI can be found here.
    """
    # def __init__(self, x, y, width, height):
    #     self.sprite = pg.image.load("sprites/enemy/idle/player-idle-1.png")