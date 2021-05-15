import numpy as np
import sys, os, csv, math, pygame
from classes.scenes import Scene

class TileMap():
    '''
    Tile map functionality.
    '''
    def __init__(self, tile_size, level_radius, num_layers, center_x=0.0, center_y=0.0):
        self.center_x, self.center_y = center_x, center_y
        self.tile_color = Scene.RED
        self.background_color = Scene.BLACK

        if type(tile_size) != int:
            raise Exception("Tile size must be and integer.")
        if type(num_layers) != int:
            raise Exception("Number of layers must an integer.")
        if num_layers*tile_size >= level_radius:
            raise Exception("Level height must be smaller than the level radius.")

        self.tile_size = tile_size       # tile size, in pixels
        self.level_radius = level_radius # map height, in pixels
        self.num_layers = num_layers     # number of layers in the map

        # Compute the map parameters 
        self.height_offset = self.level_radius - self.num_layers*self.tile_size
        self.num_sides = round(math.pi/math.atan2(self.tile_size, 2*self.height_offset))
        if self.num_sides < 3:
            self.num_sides = 3
        self.height_offset = self.tile_size/(2*math.tan(math.pi/self.num_sides))
        self.level_radius = self.height_offset + self.num_layers*self.tile_size
        self.angle = 2*math.pi/self.num_sides
        self.level_distortion = 2*self.num_layers*math.tan(math.pi/self.num_sides)

        # Initialize logical grid
        self.tilegrid = np.zeros([self.num_layers, self.num_sides]) # grid initialization

    def drawBackground(self, screen):
        '''
        Creates the tile map background, with dotted points representing the corners.
        '''
        self.background = pygame.Surface( (math.ceil(2*self.level_radius), math.ceil(2*self.level_radius)) )
        self.background_rect = self.background.get_rect(center=(self.center_x, self.center_y))

        pygame.draw.circle(self.background, self.tile_color, self.background.get_rect().center, 1 )
        self.num_points = self.num_sides*(self.num_layers+1)
        for angle_index in range(self.num_sides):
            for layer_index in range(0, self.num_layers+1):
                x = self.background_rect.centerx + ( self.height_offset + self.tile_size*layer_index )*math.cos( self.angle*angle_index )
                y = self.background_rect.centery + ( self.height_offset + self.tile_size*layer_index )*math.sin( self.angle*angle_index )
                pygame.draw.circle(self.background, self.tile_color, (x,y), 1 )
        
        self.updateBackground(screen)

    def diffMap(self):
        indexes = np.nonzero(self.last_grid-self.tilegrid)
        changed_values = self.getAtIndexes( indexes[0], indexes[1] )
        return changed_values, indexes[0], indexes[1]

    def updateBackground(self, screen):
        # background_rect = self.background.get_rect()
        self.background_rect.center = (self.center_x, self.center_y)
        screen.blit(self.background, self.background_rect)

    def moveMap(self, x, y):
        '''
        Moves the entire grid by moving the center coordinates.
        '''
        self.center_x += x
        self.center_y += y

    def toPolar(self, x, y):
        '''
        Converts cartesian coords (x,y) to polar coords (radius, angle).
        '''
        radius = math.sqrt( (x - self.center_x)**2 + (y - self.center_y)**2 )
        angle = math.atan2( y - self.center_y, x - self.center_x )
        if angle < 0:
            angle += 2*math.pi
        return radius, angle

    def setValue(self, x, y, value):
        '''
        Sets the grid values at (x,y). If the position is outside of the grid, returns None.
        '''
        self.last_grid = self.tilegrid
        val, indexes = self.getValue(x, y)
        if indexes:
            self.tilegrid[indexes] = value
        else:
            return None

    def getAtIndexes(self, i_index, j_index):
        if len(i_index) != len(j_index):
            raise Exception("Number of indexes is not the same.")
        num_indexes = len(i_index)
        values = []
        for k in range(num_indexes):
            print(i_index[k], j_index[k])
            values.append( self.tilegrid[ i_index[k], j_index[k]] )
        return values

    def getValue(self, x, y):
        '''
        Returns the tuple (value, indexes), containing the grid value and indexes at position (x,y). 
        If the position is outside of the grid, returns None.
        '''
        radius, angle = self.toPolar(x, y)
        if radius >= self.height_offset and radius <= self.level_radius:
            radii = np.array([ self.tile_size*(i+1) for i in range(self.num_layers) ]) + self.height_offset
            angles = np.array([ self.angle*(i+1) for i in range(self.num_sides) ])

            i_index = np.nonzero(radii>=radius)[0][0]
            j_index = np.nonzero(angles>=angle)[0][0]
            value = self.getAtIndexes([i_index], [j_index])

            return value, (i_index, j_index)
        else:
            return None, None

    def drawTile(self, i, j, color):
        '''
        Fills tile at index (i,j) with color.
        '''
        centerx, centery = self.background.get_rect().centerx, self.background.get_rect().centery

        x1 = centerx + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*j )
        y1 = centery + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*j )

        x2 = centerx + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*j )
        y2 = centery + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*j )

        x3 = centerx + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*(j+1) )
        y3 = centery + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*(j+1) )

        x4 = centerx + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*(j+1) )
        y4 = centery + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*(j+1) )

        return pygame.draw.polygon( self.background, color, ((x1,y1),(x2,y2),(x3,y3),(x4,y4)) ).get_rect()

    # def drawMap(self):
    #     '''
    #     Draws the map. This method can be greatly optimized by drawing the minimum amount of polygons required to represent the map, instead of simply drawing one polygon per tile.
    #     '''
    #     rows, columns = np.nonzero(self.tilegrid)
    #     num_zonzero = len(rows)
    #     dirty_rects = []
    #     for i in range(num_zonzero):
    #         dirty_rects.append(self.drawTile(rows[i], columns[i], self.tile_color))

    #     return dirty_rects

    # def drawLines(self):
    #     '''
    #     Draws the lines at the screen.
    #     '''
    #     pygame.draw.circle(self.background, self.tile_color, ( self.center_x, self.center_y ), 1 )
    #     # pygame.draw.circle(self.background, self.tile_color, ( self.center_x, self.center_y ), self.height_offset, width=1 )
    #     pygame.draw.circle(self.background, self.tile_color, ( self.center_x, self.center_y ), self.level_radius, width=1 )

    #     for j in range(self.num_sides):
    #         x1 = self.center_x + self.height_offset*math.cos( self.angle*j )
    #         y1 = self.center_y + self.height_offset*math.sin( self.angle*j )

    #         x2 = self.center_x + self.level_radius*math.cos( self.angle*j )
    #         y2 = self.center_y + self.level_radius*math.sin( self.angle*j )

    #         pygame.draw.line(self.background, self.tile_color, (x1,y1), (x2,y2))

    #     for i in range(self.num_layers):
    #         pygame.draw.circle(self.background, self.tile_color, ( self.center_x, self.center_y ), self.height_offset + self.tile_size*i, width=1 )

    def load_csv(self, filename):
        grid = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                grid.append(list(row))
        self.tilegrid = np.array(grid)

    def create_csv(self, filename):
        with open(filename+str('.csv'), mode='w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for row in range(self.num_layers):
                file_writer.writerow(self.tilegrid[row])