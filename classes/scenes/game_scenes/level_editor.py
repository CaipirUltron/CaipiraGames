import pygame
from pygame.locals import *
import math, os, csv
import numpy as np

from classes.scenes import Scene


class LevelEditor(Scene):
    """ 
    Class for polygonal tile level editor.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.deltaTime = 1/self.game.fps
        self.scroll_speed = 100.0

        self.clicked = False
        self.changed = False
        self.scroll_holding = False
        self.first_selected = True

        self.last_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        self.curr_mouse_pos = np.array([self.mouse_x, self.mouse_y])

        self.last_indexes = None
        self.curr_indexes = None
        self.value = False

        self.level = TileMap(16, 2000, 70, center_x=self.game.center_x, center_y=-3*self.game.center_y)

    def eventHandler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                pass
            if event.key == pygame.K_ESCAPE:
                self.changeScene("MainMenu")
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                pass
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.clicked = True
            if event.button == 2:
                self.scroll_holding = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicked = False
                self.changed = False
                self.first_selected = True
            if event.button == 2:
                self.scroll_holding = False
        if event.type == pygame.QUIT:
            self.level.create_csv('mymap')

    def updateLogic(self):
        '''
        Scrolling logic
        '''
        self.last_mouse_pos = self.curr_mouse_pos
        self.curr_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        if self.scroll_holding:
            self.error = self.curr_mouse_pos - self.last_mouse_pos
            self.level.moveCenter(self.error[0], self.error[1])

        '''
        Painting polygons.
        '''
        self.last_indexes = self.curr_indexes
        self.curr_indexes = self.level.getIndex(self.mouse_x, self.mouse_y)

        if self.curr_indexes and self.clicked and self.first_selected:
            self.value = self.level.getValue(self.mouse_x, self.mouse_y)
            self.first_selected = False

        if self.curr_indexes and self.clicked and (not self.changed):
            if self.value == 0:
                self.level.setValue(self.mouse_x, self.mouse_y, 1)
            elif self.value == 1:
                self.level.setValue(self.mouse_x, self.mouse_y, 0)
            self.changed = True

        if (self.curr_indexes != self.last_indexes):
            self.changed = False

    def updateDisplay(self):
        self.level.background.fill(pygame.Color("BLACK"))
        self.level.drawPoints()
        self.level.drawMap()
        self.game.screen.blit(self.level.background, (0,0))


class TileMap():
    '''
    Tile map functionality.
    '''
    def __init__(self, tile_size, level_radius, level_height, center_x=0.0, center_y=0.0):
        self.center_x, self.center_y = center_x, center_y
        self.tile_color = pygame.Color("RED")
        self.setMap(tile_size, level_radius, level_height)
        self.computeCorners()

    def setMap(self, tile_size, level_radius, num_layers):
        '''
        Initially configures the map according to tile size, level radius and chosen number of layers.
        '''
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
        self.last_grid = np.zeros([self.num_layers, self.num_sides]) # grid initialization
        self.curr_grid = np.zeros([self.num_layers, self.num_sides]) # grid initialization

        # Create background surface
        self.background = pygame.Surface( (math.ceil(2*self.level_radius), math.ceil(2*self.level_radius)) ).convert()

    def computeCorners(self):
        '''
        Computes the corner points of the polygonal grid.
        '''
        self.tiles_x, self.tiles_y = [], []
        self.num_points = self.num_sides*(self.num_layers+1)
        for angle_index in range(self.num_sides):
            for level_index in range(0, self.num_layers+1):
                self.tiles_x.append( self.center_x + ( self.height_offset + self.tile_size*level_index )*math.cos( self.angle*angle_index ) )
                self.tiles_y.append( self.center_y + ( self.height_offset + self.tile_size*level_index )*math.sin( self.angle*angle_index ) )

    def moveCenter(self, x, y):
        '''
        Moves the entire grid by moving the center coordinates.
        '''
        self.center_x += x
        self.center_y += y
        self.tiles_x = (np.array(self.tiles_x)+x).tolist()
        self.tiles_y = (np.array(self.tiles_y)+y).tolist()

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
        self.last_grid = self.curr_grid
        indexes = self.getIndex(x, y)
        if indexes:
            self.curr_grid[indexes] = value
        else:
            return None

    def getValue(self, x, y):
        '''
        Returns the grid value at (x,y). If the position is outside of the grid, returns None.
        '''
        indexes = self.getIndex(x, y)
        if indexes:
            return self.curr_grid[indexes]
        else:
            return None

    def getIndex(self, x, y):
        '''
        Returns the grid index at position (x,y). If the position is outside of the grid, returns None.
        '''
        radius, angle = self.toPolar(x, y)
        if radius > self.height_offset and radius < self.level_radius:
            # return self.getIndex(radius, angle)
            for k in range(self.num_sides):
                if angle >= self.angle*k and angle < self.angle*(k+1):
                    j_index = k
                    break
            for k in range(self.num_layers):
                if radius >= self.height_offset + self.tile_size*k  and radius < self.height_offset + self.tile_size*(k+1):
                    i_index = k
                    break
            return i_index, j_index
        else:
            return None

    def drawTile(self, i, j, color):
        '''
        Draws tile at index (i,j).
        '''
        x1 = self.center_x + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*j )
        y1 = self.center_y + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*j )

        x2 = self.center_x + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*j )
        y2 = self.center_y + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*j )

        x3 = self.center_x + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*(j+1) )
        y3 = self.center_y + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*(j+1) )

        x4 = self.center_x + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*(j+1) )
        y4 = self.center_y + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*(j+1) )

        pygame.draw.polygon( self.background, color, ((x1,y1),(x2,y2),(x3,y3),(x4,y4)) )

    def drawMap(self):
        '''
        Draws the map. This method can be greatly optimized by drawing the minimum amount of polygons required to represent the map, instead of simply drawing one polygon per tile.
        '''
        rows, columns = np.nonzero(self.curr_grid)
        num_zonzero = len(rows)
        for i in range(num_zonzero):
            self.drawTile(rows[i], columns[i], self.tile_color)
        print(range(num_zonzero))

    def drawPoints(self):
        '''
        Draws the corner points at the screen.
        '''
        pygame.draw.circle(self.background, self.tile_color, ( self.center_x, self.center_y ), 1 )
        for i in range(self.num_points):
            pygame.draw.circle(self.background, self.tile_color, ( self.tiles_x[i], self.tiles_y[i] ), 1 )

    def load_csv(self, filename):
        grid = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                grid.append(list(row))
        self.curr_grid = np.array(grid)

    def create_csv(self, filename):
        with open(filename+str('.csv'), mode='w') as file:
            file_writer = csv.writer(file, delimiter=',')
            for row in range(self.num_layers):
                file_writer.writerow(self.curr_grid[row])