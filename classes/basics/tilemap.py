import numpy as np
import json, math, pygame
from pygame.locals import *
from pygame.math import *
from classes.basics import BasicSprite, BasicGroup, Arc


def to_polar(x, y):
    '''
    Converts cartesian coords (x,y) to polar coords (radius, angle).
    '''
    radius = math.sqrt( x**2 + y**2 )
    angle = math.degrees(math.atan2( x,y ))
    if angle < 0:
        angle += 360
    return radius, angle


class Background(BasicSprite):
    '''
    Tile map background sprite.
    '''
    def __init__(self, *groups):
        self._layer = -1
        image = pygame.transform.scale(pygame.image.load("images/sprites/bg/axis.png"), (1200,1200) ).convert_alpha()
        img_size = image.get_size()
        super().__init__(image, offset=(img_size[0]/2, img_size[1]/2), *groups)


class Tile(BasicSprite):
    '''
    Basic curved tile.
    '''
    def __init__(self, radius, height, angular_width, angle=0, color=pygame.Color("RED"), *groups):
        self._layer = -1

        # Tile parameters
        self.arc = Arc( Vector2(0,0), radius, height, angular_width ) # tile arc
        self.color = color                                            # tile color

        # Initialize BasicSprite surface
        image = pygame.Surface( ( self.arc.rect.width, self.arc.rect.height ), pygame.SRCALPHA)
        offset = ( self.arc.rect.width/2, self.arc.distortion - self.arc.radius )
        super().__init__(image, offset, orientation=angle, *groups)

        # Draws sprite
        self.arc.draw_arc(image, self.color, fill=True)

    def collidepoint(self, world_x, world_y):
        '''
        Checks if given world position is inside the tile.
        '''
        radius, angle = to_polar(world_x, world_y)
        is_in_radius = ( radius >= self.arc.radius ) and ( radius < self.arc.radius + self.arc.height )
        is_in_angle = ( angle >= self.orientation - self.arc.angular_width/2 ) and ( angle < self.orientation + self.arc.angular_width/2 )
        if is_in_radius and is_in_angle:
            return True
        else:
            return False


class TileMap(BasicGroup):
    '''
    Tile map functionality.
    '''
    def __init__(self, camera, filename):
        super().__init__(camera)

        default_num_floors = 10
        default_num_sides = 100
        default_map = np.zeros([default_num_floors,default_num_sides])
        self.map_config = ...
        {
            "internal_radius": 300,
            "tile_height": 16,
            "angular_width": 360,
            "tilegrid": default_map.tolist()
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

    def load_sprites(self):
        '''
        Loads the sprites in the screen.
        '''
        for i in range(self.num_floors):
            for j in range(self.num_sides):
                radius = self.internal_radius + self.tile_height*i
                angle = self.phi*j+self.phi/2
                if self.tilegrid[i,j] > 1:
                    color = self.materials[self.tilegrid[i,j]]
                    tile = Tile( radius, self.tile_height, self.phi, angle, color )
                    self.add( tile )

    def get_tiles_at(self, mouse_x, mouse_y):
        '''
        Returns a list with all tiles at a given mouse position.
        '''
        sprite_list = self.get_sprites_at((mouse_x, mouse_y))
        world_x, world_y = self.camera.screen2world( (mouse_x, mouse_y) )

        colliding_tiles = []
        for sprite in sprite_list:
            if type(sprite) == Tile:
                if sprite.collidepoint( world_x, world_y ):
                    colliding_tiles.append(sprite)

        return colliding_tiles

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
            json.dump(self.map_config, file)
        print("Tile map saved.")