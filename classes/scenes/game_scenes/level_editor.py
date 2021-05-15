import pygame
from pygame.locals import *
import numpy as np

from classes.scenes import Scene
from tilemap import TileMap

class LevelEditor(Scene):
    """ 
    Class for polygonal tile level editor.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.scroll_speed = 100.0

        self.left_holding = False
        self.right_holding = False
        self.scroll_holding = False
        self.first_selected = False

        self.changed = False
        self.mouse_x, self.mouse_y = 0.0, 0.0

        self.last_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        self.curr_mouse_pos = np.array([self.mouse_x, self.mouse_y])

        self.last_indexes = None
        self.curr_indexes = None
        self.value = False

        self.level = TileMap(16, 2000, 70, center_x=self.game.center_x, center_y=-3*self.game.center_y)
        self.level.drawBackground(self.game.screen)

    def getInput(self):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                break
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
                    self.changed = False
                    self.first_selected = True
                if event.button == 2:
                    self.scroll_holding = False
                if event.button == 3:
                    self.right_holding = False
            if event.type == pygame.QUIT:
                self.level.create_csv('mymap')

    def updateLogic(self):
        '''
        Scrolling.
        '''
        self.last_mouse_pos = self.curr_mouse_pos
        self.curr_mouse_pos = np.array([self.mouse_x, self.mouse_y])
        if self.scroll_holding:
            self.error = self.curr_mouse_pos - self.last_mouse_pos
            self.level.moveMap(self.error[0], self.error[1])

        '''
        Updating the map.
        '''
        self.last_indexes = self.curr_indexes
        self.value, self.curr_indexes = self.level.getValue(self.mouse_x, self.mouse_y)
        print(self.curr_indexes)

        if self.curr_indexes:
            if self.left_holding:
                self.level.setValue(self.mouse_x, self.mouse_y, 1)
            if self.right_holding:
                self.level.setValue(self.mouse_x, self.mouse_y, 0)

        '''
        Registering changes.
        These changes must reflect in updateDisplay(), below
        '''


    def updateDisplay(self):

        self.game.screen.fill(Scene.BLACK)
        # Updates the screen if something has changed
        changed_values, i_indexes, j_indexes = self.level.diffMap()
        num_changes = len(changed_values)
        if num_changes > 0:
            for k in range(num_changes):
                if changed_values[k] == 0:
                    self.level.drawTile( i_indexes[k], j_indexes[k], Scene.BLACK )
                if changed_values[k] == 1:
                    self.level.drawTile( i_indexes[k], j_indexes[k], Scene.RED )

        # self.level.updateBackground(self.game.screen)

        self.game.screen.blit(self.level.background, self.level.background_rect)