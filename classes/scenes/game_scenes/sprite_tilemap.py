import numpy as np
import os, csv, math, pygame
from pygame.locals import *


class BasicSprite(pygame.sprite.Sprite):
    def __init__(self, image, pos, angle, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.angle = angle


class Tile(BasicSprite):
    '''
    Basic curved tile.
    '''
    def __init__(self, radius, height, phi, pos, angle, color=pygame.Color("WHITE"), *groups):
            
        self.radius = radius
        self.height = height

        self.phi = phi
        self.color = color

        self.img_width = 2*( self.radius+self.height )*math.sin(self.phi/2)
        self.img_height = self.radius*( 1 - math.cos(self.phi/2) ) + self.height

        self.resolution = 20 # even int

        image=pygame.Surface( (self.img_width, self.img_height), pygame.SRCALPHA)
        super().__init__(image, pos, angle, *groups)
        self.draw_base_tile()

    def draw_base_tile(self):
        points = []
        centerx = self.img_width/2
        centery = -(self.radius*math.cos(self.phi/2))
        for i in range(self.resolution+1):
            x = centerx + self.radius*math.sin( (i-self.resolution/2)*(self.phi/self.resolution) )
            y = centery + self.radius*math.cos( (i-self.resolution/2)*(self.phi/self.resolution) )
            points.append( (x,y) )
        for i in range(self.resolution+1):
            x = centerx + ( self.radius + self.height )*math.sin( -(i-self.resolution/2)*(self.phi/self.resolution) )
            y = centery + ( self.radius + self.height )*math.cos( -(i-self.resolution/2)*(self.phi/self.resolution) )
            points.append( (x,y) )
        pygame.draw.polygon( self.image, self.color, points )
        

class Background(BasicSprite):
    '''
    Tile map background sprite.
    '''
    def __init__(self, internal_radius, tile_height, num_floors, num_sides, color=pygame.Color("WHITE"), *groups):
        self.internal_radius = internal_radius
        self.tile_height = tile_height
        self.num_floors = num_floors
        self.num_sides = num_sides
        self.external_radius = self.internal_radius + self.num_floors*self.tile_height
        self.phi = 2*math.pi/self.num_sides
        self.color = color

        self.pos = (0,0)
        self.angle = 0

        image = pygame.Surface( (2*self.external_radius, 2*self.external_radius), pygame.SRCALPHA )
        super().__init__(image, self.pos, self.angle, *groups)

        self.drawBackground()

    def drawBackground(self):
        '''
        Draws the tile map dots to the specified surface. Returns a list with modified rects.
        '''
        # Central point
        pygame.draw.circle(self.image, self.color, (self.external_radius, self.external_radius), 1 )

        # Corner points
        for j in range(self.num_sides):
            for floor in range(self.num_floors+1):
                x = self.external_radius + ( self.internal_radius + self.tile_height*floor )*math.sin( self.phi*j - self.phi/2 )
                y = self.external_radius + ( self.internal_radius + self.tile_height*floor )*math.cos( self.phi*j - self.phi/2 )
                pygame.draw.circle(self.image, self.color, (x,y), 1 )

    def update(self, *args, **kwargs):
        pass


class TileMap(pygame.sprite.Group):
    '''
    Tile map functionality.
    '''
    default_shape = (10,100)

    def __init__(self, internal_radius, tile_height, filename, color=pygame.Color("WHITE"), **kwargs):
        super().__init__()
        self.color = color
        self.filename = filename
        self.level_shape = TileMap.default_shape

        if type(tile_height) != int:
            raise Exception("Tile size must be an integer.")

        for key, value in kwargs.items():
            if key == 'level_shape':
                self.level_shape = value

        self.load_level(self.filename)

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
        self.add( Background( internal_radius, tile_height, self.num_floors, self.num_sides ) )

    def load_level(self, filename):
        try:
            grid = []
            with open(os.path.join(filename+str('.csv'))) as data:
                data = csv.reader(data, delimiter=',')
                for row in data:
                    grid.append(list(row))
            self.tilegrid = np.array(grid)
            self.num_floors = self.tilegrid.shape[0]
            self.num_sides = self.tilegrid.shape[1]
        except IOError:
            print("Couldn't locate "+filename+str('.csv'))
            print("Initializing grid and creating new file "+filename+str('.csv'))
            self.tilegrid = np.zeros(self.level_shape,dtype=int)
            self.save_level(filename)

    def save_level(self, filename):
        with open(filename+str('.csv'), mode='w', newline='') as file:
            file_writer = csv.writer(file, delimiter=',')
            for row in range(self.num_floors):
                file_writer.writerow(self.tilegrid[row].tolist())
        print("Tile map saved.")