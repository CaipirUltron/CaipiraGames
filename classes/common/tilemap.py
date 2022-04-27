import numpy as np
import json, math, pygame

from pygame.locals import *
from pygame.math import *

import pymunk

from classes.common import GameObjectGroup, Arc, to_polar
from classes.objects import Tile


class TileMap(GameObjectGroup):
    '''
    Tile map functionality.
    '''
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # super().attach_space(space)

        # Default map config
        self.map_config = ...
        {
            "internal_radius": 300,
            "tile_height": 16,
            "angular_width": 360,
            "tilegrid": np.zeros([10,100]).tolist()
        }

        self.load_level(filename)
        self.internal_radius = self.map_config["internal_radius"]
        self.tile_height = self.map_config["tile_height"]
        self.angular_width = self.map_config["angular_width"]
        self.tilegrid = np.array(self.map_config["tilegrid"])

        self.num_floors, self.num_sides = self.tilegrid.shape
        self.phi = self.angular_width/self.num_sides
        self.external_radius = self.internal_radius + self.num_floors*self.tile_height

        self.solid_arc = Arc( Vector2(0,0), self.internal_radius, self.num_floors*self.tile_height, self.angular_width )

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

        self.hat_1 = np.array([[0, -1],[1, 0]])
        self.angular_accel = 0
        self.angular_vel = 1

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        def ship_gravity(body, gravity, damping, dt):
            gravity = (- (self.angular_accel + 0.2*self.angular_vel) * self.hat_1 + (self.angular_vel**2)*np.eye(2) ) @ np.array([pos[0],pos[1]])
            # gravity = (- self.angular_accel * self.hat_1 + (self.angular_vel**2)*np.eye(2) ) @ np.array([pos[0],pos[1]])
            pymunk.Body.update_velocity(body, [ gravity[0], gravity[1] ], damping, dt)

        for sprite in self.sprites():
            pos = sprite.position
            if hasattr(sprite, 'body'):
                sprite.body.velocity_func = ship_gravity

    def load_sprites(self):
        '''
        Loads the sprites in the screen.
        '''
        for i in range(self.num_floors):
            for j in range(self.num_sides):
                if self.tilegrid[i,j] >= 1:
                    color = self.materials[self.tilegrid[i,j]]
                    self.add_tile((i,j), color)

    def add_tile( self, indexes, color ):
        '''
        Adds a tile of specific color to location specified by indexes.
        '''
        radius = self.internal_radius + self.tile_height*indexes[0]
        angle = self.phi*indexes[1]+self.phi/2
        tile = Tile( radius, self.tile_height, self.phi, angle, color )
        self.add(tile)

    def get_tiles_at(self, mouse_x, mouse_y):
        '''
        Returns a list with all tiles at a given mouse position.
        '''
        sprite_list = self.get_sprites_at( (mouse_x, mouse_y) )
        world_x, world_y = self.camera.screen2world( (mouse_x, mouse_y) )

        colliding_tiles = []
        for sprite in sprite_list:
            if isinstance(sprite, Tile):
                if sprite.collidepoint( world_x, world_y ):
                    colliding_tiles.append(sprite)
        return colliding_tiles

    def set_value_at(self, value, indexes):
        self.tilegrid[ indexes[0], indexes[1] ] = value
        self.map_config["tilegrid"] = self.tilegrid.tolist()

    def get_value_at(self, x, y):
        '''
        Returns the tuple (value, index), containing the grid value and index at position x,y (world coordinates). 
        If the position is outside of the grid, returns None.
        '''
        radius, angle = to_polar(x, y)
        
        if ( radius >= self.internal_radius and radius <= self.external_radius ) and ( angle <= self.angular_width ):
            radii = np.array([ self.tile_height*(i+1) for i in range(self.num_floors) ]) + self.internal_radius
            angles = np.array([ self.phi*(i+1) for i in range(self.num_sides) ])

            i_index = np.nonzero(radii>=radius)[0][0]
            if len(np.nonzero(angles>=angle)[0]) != 0:
                j_index = np.nonzero(angles>=angle)[0][0]
            else:
                return None, None

            value = self.tilegrid[ i_index, j_index ]
            return value, (i_index, j_index)
        else:
            return None, None

    def load_level(self, filename):
        try:
            with open(filename+str('.json')) as file:
                self.map_config = json.load(file)
        except IOError:
            print("Couldn't locate "+filename+str(".json"))
            print("Initializing grid and creating new configuration file "+filename+str(".json"))
            self.save_level(filename)

    def save_level(self, filename):
        with open(filename+str(".json"), "w") as file:
            json.dump(self.map_config, file, indent=4)
        print("Tile map saved.")
