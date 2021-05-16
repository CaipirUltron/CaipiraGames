import pygame, sys
from pygame.locals import *
import numpy as np

from classes.scenes import Scene
from classes.scenes.game_scenes.tile_map import TileMap

class LevelEditor(Scene):
    """ 
    Class for polygonal tile level editor.
    """
    def __init__(self, game, name):
        super().__init__(game, name)

        self.background_color = pygame.Color("BLACK")
        self.scroll_speed = 1.0

        self.left_holding = False
        self.right_holding = False
        self.scroll_holding = False

        self.mouse_x, self.mouse_y = 0.0, 0.0
        self.mouse_displacement = (0,0)

        self.level = TileMap(16, 500, 15, pygame.Color("RED"), filename='mymap')
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
                self.level.save_level('mymap')
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

    def updateLogic(self):
        
        # Scrolling
        self.panLevel( self.mouse_displacement )
        
        # Updating the map.
        value, indexes = self.level.getValue( *self.toBackground(self.mouse_x, self.mouse_y) )

        if indexes:
            if self.left_holding:
                self.level.setValue( *self.toBackground(self.mouse_x, self.mouse_y), 1 )
                tile_rect = self.level.drawTile( *indexes, self.level.tile_color )
            if self.right_holding:
                self.level.setValue( *self.toBackground(self.mouse_x, self.mouse_y), 0 )
                tile_rect = self.level.drawTile( *indexes, self.background_color )

    def updateDisplay(self):

        # Fills the game screen with the background color, but only at the intersection with the background
        intersect = self.level_rect.clip(self.game.screen_rect)
        self.dirty_rects.append( self.game.screen.fill(self.background_color, rect=intersect) )

        # Blits the background level at the screen
        self.level_rect.center = self.level_center.tolist()
        self.dirty_rects.append( self.game.screen.blit( self.level.background, self.level_rect ) )

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