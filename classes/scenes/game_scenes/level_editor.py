import pygame
from pygame.locals import *
import math
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
        self.tile_changed = False
        self.scroll_holding = False

        self.last_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        self.current_mouse_pos = np.array([self.mouse_x, self.mouse_y])

        self.polygonalLevel = PolygonalLevel(32, 2000, 50, center_x=self.game.center_x, center_y=-4*self.game.center_y)

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
            if event.button == 2:
                self.scroll_holding = False

    def updateLogic(self):
        # Scroll level
        self.last_mouse_pos = self.current_mouse_pos
        self.current_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        if self.scroll_holding:
            self.error = self.current_mouse_pos - self.last_mouse_pos
            self.polygonalLevel.moveCenter(self.error[0], self.error[1])

        # Paint current polygon
        if self.clicked:
            self.polygonalLevel.setGrid(self.mouse_x, self.mouse_y)
            self.clicked = False

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("Black"))
        self.polygonalLevel.drawPoints(self.game.screen)
        self.polygonalLevel.drawLevel(self.game.screen)

class PolygonalLevel():
    def __init__(self, tile_size, level_radius, level_height, center_x=0.0, center_y=0.0):
        self.center_x, self.center_y = center_x, center_y
        self.setLevel(tile_size, level_radius, level_height)

    def setLevel(self, tile_size, level_radius, num_layers):
        if type(tile_size) != int:
            raise Exception("Tile size must be and integer.")
        if type(num_layers) != int:
            raise Exception("Number of layers must an integer.")
        if num_layers*tile_size >= level_radius:
            raise Exception("Level height must be smaller than the level radius.")

        self.tile_size = tile_size       # tile size, in pixels
        self.level_radius = level_radius # level height, in pixels
        self.num_layers = num_layers     # number of layers

        # Computes the required number of polygon sides
        self.height_offset = self.level_radius - self.num_layers*self.tile_size
        self.num_sides = round(math.pi/math.atan2(self.tile_size, 2*self.height_offset))
        if self.num_sides < 3:
            self.num_sides = 3
        self.height_offset = self.tile_size/(2*math.tan(math.pi/self.num_sides))
        self.level_radius = self.height_offset + self.num_layers*self.tile_size
        self.angle = 2*math.pi/self.num_sides
        self.grid = [[False for i in range(self.num_layers)] for j in range(self.num_sides)]

        # Computes the level distortion
        self.level_distortion = 2*self.num_layers*math.tan(math.pi/self.num_sides)

        # Computes grid points and move center
        self.computePoints()

    def computePoints(self):
        self.tiles_x, self.tiles_y = [], []
        self.num_points = self.num_sides*(self.num_layers+1)
        for angle_index in range(self.num_sides):
            for level_index in range(0, self.num_layers+1):
                self.tiles_x.append( self.center_x + ( self.height_offset + self.tile_size*level_index )*math.cos( self.angle*angle_index - self.angle/2 ) )
                self.tiles_y.append( self.center_y + ( self.height_offset + self.tile_size*level_index )*math.sin( self.angle*angle_index - self.angle/2 ) )

    def moveCenter(self, x, y):
        self.center_x += x
        self.center_y += y
        self.tiles_x = (np.array(self.tiles_x)+x).tolist()
        self.tiles_y = (np.array(self.tiles_y)+y).tolist()

    def getRadial(self, x, y):
        radius = math.sqrt( (x - self.center_x)**2 + (y - self.center_y)**2 )
        angle = math.atan2( y - self.center_y, x - self.center_x )
        if angle < 0:
            angle += 2*math.pi
        return radius, angle

    def getIndex(self, radius, angle):
        i_index, j_index = 0, 0
        for k in range(self.num_sides):
            if angle > self.angle*k - self.angle/2 and angle < self.angle*(k+1) - self.angle/2:
                j_index = k
                break
        for k in range(self.num_layers):
            if radius > self.height_offset + self.tile_size*k  and radius < self.height_offset + self.tile_size*(k+1):
                i_index = k
                break
        return i_index, j_index

    def getGrid(self, x, y):
        radius, angle = self.getRadial(x, y)
        if radius > self.height_offset and radius < self.level_radius:
            return self.getIndex(radius, angle)
        else:
            return None

    def setGrid(self, x, y):
        radius, angle = self.getRadial(x, y)
        if radius > self.height_offset and radius < self.level_radius:
            i, j = self.getIndex(radius, angle)
            self.grid[j][i] = not self.grid[j][i]

    def drawLevel(self, screen):
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

    def drawPoints(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), ( self.center_x, self.center_y ), 1 )
        for i in range(self.num_points):
            pygame.draw.circle(screen, (255, 0, 0), ( self.tiles_x[i], self.tiles_y[i] ), 1 )