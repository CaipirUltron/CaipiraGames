import pygame, sys
from pygame.locals import *
import numpy as np

from classes.scenes import Scene
from classes.scenes.game_scenes.tilemap import TileMap

class LevelEditor(Scene):
    """ 
    Class for polygonal tile level editor.
    """
    def __init__(self, game, name):
        super().__init__(game, name)

        self.filename = 'map1'

        self.background_color = pygame.Color("BLACK")
        self.button_separation = 40
        self.button_radius = 15
        self.ponter_size = 8

        self.curr_material = 1

        self.left_holding = False
        self.right_holding = False
        self.scroll_holding = False
        self.scroll_speed = 1.0

        self.mouse_x, self.mouse_y = 0.0, 0.0
        self.mouse_displacement = (0,0)
        self.angle = 0.0

        self.level = TileMap(16, 400, 15, filename=self.filename)
        # self.level = TileMap(16, 800, 25, filename=self.filename)

        self.level_center = np.array([self.game.center_x, self.game.center_y])
        self.level_rect = self.level.background.get_rect(center=self.level_center.tolist())

        # Initially blits the level into the screnn
        self.dirty_rects.append( self.game.screen.blit( self.level.background, self.level_rect ) )

    def panLevel(self, displacement):
        self.level_center += self.scroll_speed*displacement

    def getInput(self):

        self.mouse_displacement = np.zeros(2)
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.level.save_level(self.filename)
                pygame.quit()
                sys.exit()
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
                    self.left_holding = True
                if event.button == 2:
                    self.scroll_holding = True
                if event.button == 3:
                    self.right_holding = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.left_holding = False
                if event.button == 2:
                    self.scroll_holding = False
                if event.button == 3:
                    self.right_holding = False
            if event.type == pygame.MOUSEMOTION and self.scroll_holding:
                self.mouse_displacement += np.array(event.rel)
            if event.type == MOUSEWHEEL:
                if event.y < 0:
                    self.curr_material += 1
                if event.y > 0:
                    self.curr_material -= 1
  
    def updateLogic(self):
        
        # Loop on the number of materials
        if self.curr_material > self.level.num_materials:
            self.curr_material = 1
        elif self.curr_material < 1:
            self.curr_material = self.level.num_materials

        # Scrolling
        self.panLevel( self.mouse_displacement )

        # Updating the map.
        value, indexes = self.level.getValue( *self.toBackground(self.mouse_x, self.mouse_y) )

        if indexes:
            if self.left_holding:
                self.level.setValue( *self.toBackground(self.mouse_x, self.mouse_y), self.curr_material )
                tile_rect = self.level.drawTile( *indexes, self.level.materials[self.curr_material] )
            if self.right_holding:
                self.level.setValue( *self.toBackground(self.mouse_x, self.mouse_y), 0 )
                tile_rect = self.level.drawTile( *indexes, self.background_color )

    def updateDisplay(self):

        # Fills the game screen with the background color, but only at the intersection with the background
        intersect = self.level_rect.clip(self.game.screen_rect)
        self.dirty_rects.append( self.game.screen.fill(self.background_color) )

        # Blits the background level at the screen

        self.level_rect.center = self.level_center.tolist()
        self.dirty_rects.append( self.game.screen.blit( self.level.background, self.level_rect ) )

        self.dirty_rects.append( pygame.draw.circle(self.game.screen, self.level.materials[self.curr_material], (self.mouse_x,self.mouse_y), self.ponter_size ) )

        for material in self.level.materials:
            pygame.draw.circle(self.game.screen, self.level.materials[material], ( 2*self.button_radius , int(material)*self.button_separation ), self.button_radius )

    def rot_center(self, angle):
        """rotate an image while keeping its center"""
        self.level.background = pygame.transform.rotate(self.level.background, angle)
        self.level_rect = self.level.background.get_rect(center=self.level_rect.center)

    def toScreen(self, rect):
        '''
        Converts a rect defined in background coordinates to screen coordinates.
        '''
        new_rect = rect.copy()
        new_rect.x = self.level_rect.x + rect.x
        new_rect.y = self.level_rect.y + rect.y

        return new_rect

    def toBackground(self, x, y):
        '''
        Converts from screen coordinates to background coordinates.
        '''
        return x - self.level_rect.x, y - self.level_rect.y