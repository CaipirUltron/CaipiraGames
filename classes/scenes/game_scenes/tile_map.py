import numpy as np
import os, csv, math, pygame

class TileMap():
    '''
    Tile map functionality.
    '''
    def __init__(self, tile_size, level_radius, num_layers, base_color=pygame.Color("WHITE"), filename=None):

        self.base_color = base_color

        self.materials = {
            '1': pygame.Color("WHITE"),
            '2': pygame.Color("RED"),
            '3': pygame.Color("GREEN"),
            '4': pygame.Color("BLUE"),
            '5': pygame.Color("MAGENTA"),
            '6': pygame.Color("ORANGE")
        }
        self.num_materials = len(self.materials)

        if type(tile_size) != int:
            raise Exception("Tile size must be an integer.")
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
        if filename != None:
            self.load_level(filename)
        else:
            self.tilegrid = np.zeros([self.num_layers, self.num_sides],dtype=int) # grid initialization

        # Initialize background graphics.
        self.background = pygame.Surface( (math.ceil(2*self.level_radius), math.ceil(2*self.level_radius)) )
        self.background_rect = self.background.get_rect()
        self.drawBackground()

    def drawBackground(self):
        '''
        Draws the tile map dots to the specified surface. Returns a list with modified rects.
        '''
        dirty_rects = []

        # Central point
        dirty_rects.append( pygame.draw.circle(self.background, self.base_color, self.background.get_rect().center, 1 ) )

        # Corner points
        for angle_index in range(self.num_sides):
            for layer_index in range(0, self.num_layers+1):
                x = self.background_rect.centerx + ( self.height_offset + self.tile_size*layer_index )*math.cos( self.angle*angle_index )
                y = self.background_rect.centery + ( self.height_offset + self.tile_size*layer_index )*math.sin( self.angle*angle_index )
                dirty_rects.append( pygame.draw.circle(self.background, self.base_color, (x,y), 1 ) )

                if layer_index < self.num_layers:
                    material = int(self.getAtIndexes([layer_index], [angle_index])[0])
                    if material != 0:
                        dirty_rects.append( self.drawTile(layer_index, angle_index, self.materials[str(material)]) )

        return dirty_rects

    def toPolar(self, x, y):
        '''
        Converts cartesian coords (x,y) to polar coords (radius, angle).
        '''
        radius = math.sqrt( (x - self.background_rect.centerx)**2 + (y - self.background_rect.centery)**2 )
        angle = math.atan2( y - self.background_rect.centery, x - self.background_rect.centerx )
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
        Fills tile at index (i,j) with color. Returns modified rects.
        '''
        dirty_rects = []

        centerx, centery = self.background_rect.centerx, self.background_rect.centery

        x1 = centerx + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*j )
        y1 = centery + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*j )

        x2 = centerx + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*j )
        y2 = centery + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*j )

        x3 = centerx + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*(j+1) )
        y3 = centery + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*(j+1) )

        x4 = centerx + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*(j+1) )
        y4 = centery + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*(j+1) )

        p1, p2, p3, p4 = (x1,y1), (x2,y2), (x3,y3), (x4,y4)

        dirty_rects.append( pygame.draw.circle(self.background, self.base_color, (x1,y1), 1 ) )
        dirty_rects.append( pygame.draw.circle(self.background, self.base_color, (x2,y2), 1 ) )
        dirty_rects.append( pygame.draw.circle(self.background, self.base_color, (x3,y3), 1 ) )
        dirty_rects.append( pygame.draw.circle(self.background, self.base_color, (x4,y4), 1 ) )
        dirty_rects.append( pygame.draw.polygon(self.background, color, (p1,p2,p3,p4)) )

        return dirty_rects

    def load_level(self, filename):
        grid = []
        with open(os.path.join(filename+str('.csv'))) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                grid.append(list(row))
        tilegrid = np.array(grid)
        if tilegrid.shape == ( self.num_layers, self.num_sides ):
            self.tilegrid = tilegrid
            print("Tile map loaded.")
        else:
            raise Exception("Shape of loaded level is incompatible.")

    def save_level(self, filename):
        with open(filename+str('.csv'), mode='w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for row in range(self.num_layers):
                file_writer.writerow(self.tilegrid[row].tolist())
        print("Tile map saved.")