import pygame
from pygame.locals import *
import math, os, csv
import numpy as np

from classes.scenes import Scene

##############################################################################################
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

        self.last_coords = None
        self.curr_coords = None
        self.paint_value = False

        self.level = TileMap(16, 2000, 70, center_x=self.game.center_x, center_y=-3*self.game.center_y)
        print(self.level.num_layers, self.level.num_sides)

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
        self.last_coords = self.curr_coords
        self.curr_coords = self.level.getGrid(self.mouse_x, self.mouse_y)

        if self.curr_coords and self.clicked and self.first_selected:
            self.paint_value = self.level.grid[self.curr_coords[1]][self.curr_coords[0]]
            self.first_selected = False

        if self.curr_coords and self.clicked and (not self.changed):
            self.level.setGrid(*self.curr_coords, not self.paint_value)
            self.changed = True

        if (self.curr_coords != self.last_coords):
            self.changed = False

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("Black"))
        self.level.drawCorners(self.game.screen)
        self.level.drawMap(self.game.screen)

##############################################################################################
class TileMap():
    '''
    Tile map functionality.
    '''
    def __init__(self, tile_size, level_radius, level_height, center_x=0.0, center_y=0.0):
        self.center_x, self.center_y = center_x, center_y
        self.setLevel(tile_size, level_radius, level_height)

    def setLevel(self, tile_size, level_radius, num_layers):
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
        self.level_radius = level_radius # level height, in pixels
        self.num_layers = num_layers     # number of layers

        self.height_offset = self.level_radius - self.num_layers*self.tile_size
        self.num_sides = round(math.pi/math.atan2(self.tile_size, 2*self.height_offset))
        if self.num_sides < 3:
            self.num_sides = 3
        self.height_offset = self.tile_size/(2*math.tan(math.pi/self.num_sides))
        self.level_radius = self.height_offset + self.num_layers*self.tile_size
        self.angle = 2*math.pi/self.num_sides

        self.grid = [[False for i in range(self.num_layers)] for j in range(self.num_sides)] # grid initialization

        self.level_distortion = 2*self.num_layers*math.tan(math.pi/self.num_sides)

        self.computeCorners()

    def computeCorners(self):
        '''
        Computes the corner points of the polygonal grid.
        '''
        self.tiles_x, self.tiles_y = [], []
        self.num_points = self.num_sides*(self.num_layers+1)
        for angle_index in range(self.num_sides):
            for level_index in range(0, self.num_layers+1):
                self.tiles_x.append( self.center_x + ( self.height_offset + self.tile_size*level_index )*math.cos( self.angle*angle_index - self.angle/2 ) )
                self.tiles_y.append( self.center_y + ( self.height_offset + self.tile_size*level_index )*math.sin( self.angle*angle_index - self.angle/2 ) )

    def moveCenter(self, x, y):
        '''
        Moves the entire grid by moving the center coordinates.
        '''
        self.center_x += x
        self.center_y += y
        self.tiles_x = (np.array(self.tiles_x)+x).tolist()
        self.tiles_y = (np.array(self.tiles_y)+y).tolist()

    def getRadial(self, x, y):
        '''
        Converts cartesian coords (x,y) to polar coords (radius, angle).
        '''
        radius = math.sqrt( (x - self.center_x)**2 + (y - self.center_y)**2 )
        angle = math.atan2( y - self.center_y, x - self.center_x )
        if angle < 0:
            angle += 2*math.pi
        return radius, angle

    def getIndex(self, radius, angle):
        '''
        Returns the grid indexes at position (radius,angle), in polar coordinates. If the position is outside of the grid, returns None.
        '''
        i_index, j_index = None, None
        for k in range(self.num_sides):
            if angle > self.angle*k - self.angle/2 and angle < self.angle*(k+1) - self.angle/2:
                j_index = k
                break
        for k in range(self.num_layers):
            if radius > self.height_offset + self.tile_size*k  and radius < self.height_offset + self.tile_size*(k+1):
                i_index = k
                break
        if i_index:
            return i_index, j_index
        else:
            return None

    def getGrid(self, x, y):
        '''
        Returns the grid value at position (x,y). If the position is outside of the grid, returns None.
        '''
        radius, angle = self.getRadial(x, y)
        if radius > self.height_offset and radius < self.level_radius:
            return self.getIndex(radius, angle)
        else:
            return None

    def setGrid(self, i, j, *values):
        '''
        Sets the grid value at (i,j) to value [True/False]
        If no argument is passed, negates the current value.
        '''
        if len(values) > 0:
            for value in values:
                self.grid[j][i] = value
        else:
            self.grid[j][i] = not self.grid[j][i]
        return self.grid[j][i]

    def drawMap(self, screen):
        '''
        Draws polygons using the corner coordinates.
        This method can be greatly optimized by drawing the minimum amount of polygons required to represent the map, instead of simply drawing one polygon per tile.
        '''
        for j in range(self.num_sides):
            for i in range(self.num_layers):
                if self.grid[j][i]:
                    x1 = self.center_x + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*j - self.angle/2 )
                    y1 = self.center_y + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*j - self.angle/2 )
                    p1 = (x1,y1)

                    x2 = self.center_x + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*j - self.angle/2 )
                    y2 = self.center_y + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*j - self.angle/2 )
                    p2 = (x2,y2)

                    x3 = self.center_x + ( self.height_offset + self.tile_size*(i+1) )*math.cos( self.angle*(j+1) - self.angle/2 )
                    y3 = self.center_y + ( self.height_offset + self.tile_size*(i+1) )*math.sin( self.angle*(j+1) - self.angle/2 )
                    p3 = (x3,y3)

                    x4 = self.center_x + ( self.height_offset + self.tile_size*i )*math.cos( self.angle*(j+1) - self.angle/2 )
                    y4 = self.center_y + ( self.height_offset + self.tile_size*i )*math.sin( self.angle*(j+1) - self.angle/2 )
                    p4 = (x4,y4)

                    pygame.draw.polygon( screen, (255,0,0), (p1,p2,p3,p4) )

    def drawCorners(self, screen):
        '''
        Draws the corner points at the screen.
        '''
        pygame.draw.circle(screen, (255, 0, 0), ( self.center_x, self.center_y ), 1 )
        for i in range(self.num_points):
            pygame.draw.circle(screen, (255, 0, 0), ( self.tiles_x[i], self.tiles_y[i] ), 1 )

    def load_csv(self, filename):
        self.grid = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                self.grid.append(list(row))

    def create_csv(self, filename):
        with open(filename+str('.csv'), mode='w') as file:
            file_writer = csv.writer(file, delimiter=',')
            print("Number of sides = " + str(self.num_sides))
            for j in range(self.num_sides):
                print(len(self.grid[j]))
                file_writer.writerow(self.grid[j])