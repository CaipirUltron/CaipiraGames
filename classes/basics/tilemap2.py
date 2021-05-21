import numpy as np
import os, csv, math, pygame
from pygame.locals import *
from classes.basics import BasicSprite, BasicGroup


class Background(BasicSprite):
    '''
    Tile map background sprite.
    '''
    def __init__(self, internal_radius, tile_height, num_floors, num_sides, color=pygame.Color("WHITE"), *groups):
        self._layer = 0

        self.internal_radius = internal_radius
        self.tile_height = tile_height
        self.num_floors = num_floors
        self.num_sides = num_sides
        self.external_radius = self.internal_radius + self.num_floors*self.tile_height
        self.phi = 2*math.pi/self.num_sides
        self.color = color

        image = pygame.Surface( (2*self.external_radius, 2*self.external_radius), pygame.SRCALPHA )
        self.drawBackground(image)
        super().__init__(image, (self.external_radius,self.external_radius), *groups)

    def drawBackground(self, image):
        '''
        Draws the tile map dots to the specified surface. Returns a list with modified rects.
        '''
        # Central point
        pygame.draw.circle(image, self.color, (self.external_radius, self.external_radius), 1 )

        # Corner points
        for j in range(self.num_sides):
            for floor in range(self.num_floors+1):
                x = self.external_radius + ( self.internal_radius + self.tile_height*floor )*math.sin( self.phi*j - self.phi/2 )
                y = self.external_radius + ( self.internal_radius + self.tile_height*floor )*math.cos( self.phi*j - self.phi/2 )
                pygame.draw.circle(image, self.color, (x,y), 1 )


class Tile(BasicSprite):
    '''
    Basic curved tile.
    '''
    def __init__(self, radius, height, phi, angle=0, color=pygame.Color("RED"), *groups):
        self._layer = -1

        # Tile parameters
        self.radius = radius            # tile radius
        self.height = height            # tile height
        self.phi = math.radians(phi)    # tile angle
        self.color = color              # tile color

        # Compute necessary dimensions for the tile surface
        self.distortion = self.radius*( 1 -math.cos(self.phi/2) )
        self.img_width = 2*( self.radius + self.height )*math.sin(self.phi/2)
        self.img_height = self.distortion + self.height

        # Initialize BasicSprite surface
        image = pygame.Surface( ( self.img_width, self.img_height ), pygame.SRCALPHA)
        offset = ( self.img_width/2, self.distortion - self.radius )
        self.draw_base_tile(image, 10)
        super().__init__(image, offset, orientation=angle, *groups)

    def draw_base_tile(self, surface, resolution):
        points = []
        centerx = self.img_width/2
        centery = -(self.radius*math.cos(self.phi/2))
        for i in range(resolution+1):
            x = centerx + self.radius*math.sin( (i-resolution/2)*(self.phi/resolution) )
            y = centery + self.radius*math.cos( (i-resolution/2)*(self.phi/resolution) )
            points.append( (x,y) )
        for i in range(resolution+1):
            x = centerx + ( self.radius + self.height )*math.sin( -(i-resolution/2)*(self.phi/resolution) )
            y = centery + ( self.radius + self.height )*math.cos( -(i-resolution/2)*(self.phi/resolution) )
            points.append( (x,y) )
        pygame.draw.polygon( surface, self.color, points )


class TileMap(BasicGroup):
    '''
    Tile map functionality.
    '''
    default_shape = (10,100)

    def __init__(self, camera, internal_radius, tile_height, filename, color=pygame.Color("WHITE"), **kwargs):
        super().__init__(camera)

        self.internal_radius = internal_radius
        self.tile_height = tile_height
        self.filename = filename
        self.level_shape = TileMap.default_shape

        if type(tile_height) != int:
            raise Exception("Tile size must be an integer.")

        for key, value in kwargs.items():
            if key == 'level_shape':
                self.level_shape = value
        self.load_level(self.filename)

        self.num_floors, self.num_sides = self.level_shape[0], self.level_shape[1]
        self.phi = 360/self.num_sides
        self.external_radius = self.internal_radius + self.num_floors*self.tile_height

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
        # self.add( Background( self.internal_radius, self.tile_height, self.num_floors, self.num_sides, color ) )

    def load_sprites(self):
        '''
        This method creates the sprites in the screen.
        '''
        for i in range(self.num_floors):
            for j in range(self.num_sides):
                radius = self.internal_radius + self.tile_height*i
                angle = self.phi*j
                if self.tilegrid[i,j] > 1:
                    color = self.materials[self.tilegrid[i,j]]
                    tile = Tile( radius, self.tile_height, self.phi, angle, color )
                    self.add( tile )

    def get_value(self, x, y):
        '''
        Returns the tuple (value, index), containing the grid value and index at position x,y (world coordinates). 
        If the position is outside of the grid, returns None.
        '''
        radius, angle = self.to_polar(x, y)
        if radius >= self.internal_radius and radius <= self.external_radius:
            radii = np.array([ self.tile_height*(i+1) for i in range(self.num_floors) ]) + self.internal_radius
            angles = np.array([ self.phi*i + self.phi/2 for i in range(self.num_sides) ])

            i_index = np.nonzero(radii>=radius)[0][0]
            if angle < 360-self.phi/2:
                j_index = np.nonzero(angles>=angle)[0][0]
            else:
                j_index = 0
            value = self.tilegrid[ i_index, j_index ]

            return value, (i_index, j_index)
        else:
            return None, None

    def load_level(self, filename):
        try:
            grid = []
            with open(os.path.join(filename+str('.csv'))) as data:
                data = csv.reader(data, delimiter=',')
                for row in data:
                    grid.append(list(row))
            self.tilegrid = np.array(grid,dtype=int)
            self.level_shape = self.tilegrid.shape
        except IOError:
            print("Couldn't locate "+filename+str('.csv'))
            print("Initializing grid and creating new file "+filename+str('.csv'))
            self.tilegrid = np.zeros(self.level_shape,dtype=int)
            self.save_level(filename)

    def save_level(self, filename):
        with open(filename+str('.csv'), mode='w', newline='') as file:
            file_writer = csv.writer(file, delimiter=',')
            for row in range(self.level_shape[0]):
                file_writer.writerow(self.tilegrid[row].tolist())
        print("Tile map saved.")

    @staticmethod
    def to_polar(x, y):
        '''
        Converts cartesian coords (x,y) to polar coords (radius, angle).
        '''
        radius = math.sqrt( x**2 + y**2 )
        angle = math.degrees(math.atan2( x,y ))
        if angle < 0:
            angle += 360

        return radius, angle