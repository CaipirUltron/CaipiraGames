import numpy as np
import json, pygame
import math

from itertools import product
from pygame.locals import *
from pygame.sprite import Sprite

import pymunk

from classes.common import GameObject, GameObjectGroup

class TileMap(GameObjectGroup):
    '''
    Tile map. Creates a rectangular tile map from .json file with "tilegrid" array.
    '''
    def __init__(self, map_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Loads map config
        if map_config == None:
            self.map_config = ...
            {
                "tile_width": 16,           # tile width in pixels
                "tile_height": 16,          # tile height in pixels
                "height": 10,               # map width in number of tiles
                "width": 100                # map height in number of tiles
            }
            self.map_config["tilegrid"] = np.zeros([10,100]).tolist()
        else:
            self.map_config = map_config

        self.tile_w = self.map_config["tile_width"]
        self.tile_h = self.map_config["tile_height"]
        self.grid = np.array(self.map_config["tilegrid"])
        self.h = self.grid.shape[0]
        self.w = self.grid.shape[1]

        print(self.grid.shape)

        self.see_grid = False

        self.materials = {
            1: pygame.Color("WHITE"),
            2: pygame.Color("RED"),
            3: pygame.Color("GREEN"),
            4: pygame.Color("BLUE"),
            5: pygame.Color("MAGENTA"),
            6: pygame.Color("ORANGE"),
            7: pygame.Color("BROWN")
        }
        self.num_materials = len(self.materials)
        self.load_sprites()

    # def update(self, *args, **kwargs):
    #     super().update(*args, **kwargs)

    #     def ship_gravity(body, gravity, damping, dt):
    #         gravity = (- self.angular_accel * self.hat_1 + (self.angular_vel**2)*np.eye(2) ) @ np.array([pos[0],pos[1]])
    #         pymunk.Body.update_velocity(body, [ gravity[0], gravity[1] ], damping, dt)

    #     for sprite in self.sprites():
    #         pos = sprite.position
    #         if hasattr(sprite, 'body'):
    #             sprite.body.velocity_func = ship_gravity

    def get_grid(self, color=pygame.Color("BLACK")):
        '''
        Returns the grid lines for debugging.
        '''
        grid_surf = pygame.Surface([640,480], pygame.SRCALPHA, 32).convert_alpha()

        # Draws vertical lines
        for i in range(self.w):
            pygame.draw.line(grid_surf, color, (i*self.tile_w, 0), (i*self.tile_w, self.h*self.tile_h))

        # Draws horizontal lines
        for i in range(self.h):
            pygame.draw.line(grid_surf, color, (0, i*self.tile_h), (self.w*self.tile_w, i*self.tile_h))

        return grid_surf

    def load_sprites(self):
        '''
        Loads the sprites in the screen.
        '''
        for i,j in product(range(self.h),range(self.w)):
            if self.grid[i,j] >= 1:
                tile_color = self.materials[self.grid[i,j]]
                tile_surf = pygame.Surface((self.tile_h,self.tile_w))
                tile_surf.fill(tile_color)
                tile = GameObject( tile_surf, position=(j*self.tile_w, i*self.tile_h) )
                self.add(tile)

    def get_tiles_at(self, mouse_x, mouse_y):
        '''
        Returns a list with all tiles at a given mouse position.
        '''
        # Sprite class method get_sprites_at() uses a simple collision detection to check if there is a sprite at the specified SCREEN_COORDINATES
        sprite_list = self.get_sprites_at( (mouse_x, mouse_y) )
        # world_x, world_y = self.camera.screen2world( (mouse_x, mouse_y) )

        # colliding_tiles = []
        # for sprite in sprite_list:
        #     if isinstance(sprite, Tile):
        #         if sprite.collidepoint( world_x, world_y ):
        #             colliding_tiles.append(sprite)

        return sprite_list

    def set_value_at(self, value, indexes):
        self.grid[ indexes[0], indexes[1] ] = value

    def get_value_at(self, x, y):
        '''
        Returns the tuple (value, index), containing the grid value and index at position x,y (world coordinates). 
        If the position is outside of the grid, returns None.
        '''
        i = math.floor(y/self.tile_h)+1
        j = math.floor(x/self.tile_w)
        if i >= 0 and j >= 0 and i < self.h and j < self.w:
            value = self.grid[ i, j ]
            return value, (i,j)
        else:
            return None, None

    def save_level(self, filename):
        '''
        Save the current map configuration into a file.
        '''
        self.map_config["tilegrid"] = self.grid.tolist()
        with open(filename+str(".json"), "w") as file:
            json.dump(self.map_config, file, indent=4)
        print("Tile map saved.")

    @classmethod
    def from_file(cls, filename: str, *args, **kwargs):
        '''
        Creates obj from specified filename.
        '''
        try:
            with open(filename+str('.json')) as file:
                map_config = json.load(file)

                must_have = ["tile_width", "tile_height", "width", "height", "tilegrid"]
                dkeys = map_config.keys()

                if "tilegrid" in dkeys and isinstance( map_config["tilegrid"], list ):
                    map_config["tilegrid"] = np.array(map_config["tilegrid"])
                    map_config["height"] = map_config["tilegrid"].shape[0]
                    map_config["width"] = map_config["tilegrid"].shape[1]

                for key in must_have:
                    if key not in dkeys:
                        raise TypeError(f"A valid map configuration must have the \"{key}\" attribute.")
                    
                return cls(map_config, *args, **kwargs)
            
        except IOError:
            print("Couldn't locate " + filename + str(".json"))
            return None