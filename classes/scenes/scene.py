import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.running = False

        self.update_all = True
        self.dirty_rects = []

    def changeScene(self, scene_name):
        self.game.setActiveScene(scene_name)
        self.running = False
        
    @abstractmethod
    def getInput(self):
        '''
        This method handles user inputs.
        '''
        pass

    @abstractmethod
    def updateLogic(self):
        '''
        This method encapsulates the Scene logic, and is responsible for updating the Scene state.
        '''
        pass

    @abstractmethod
    def updateDisplay(self):
        '''
        This method updates the display screen with created surfaces.
        It is recommended to append the Rect returned by every blit to the list self.dirty_rects, for optimal performance on display update.
        '''
        pass

    def runningLoop(self):
        '''
        Main loop for the scene.
        '''
        self.running = True
        while self.running:
            if not self.update_all:
                self.dirty_rects = []
            self.getInput()
            self.updateLogic()
            self.updateDisplay()
            if self.update_all:
                pygame.display.update()
            else:
                pygame.display.update(self.dirty_rects)
            self.game.clock.tick(self.game.fps)