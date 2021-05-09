import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    BLACK = pygame.Color("BLACK")
    RED = pygame.Color("RED")
    
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.running = False

        # Updates the hole screen.
        self.dirty_rects = self.game.screen.get_rect()

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
        This method updates the display.
        '''
        pass

    def runningLoop(self):
        '''
        Main loop for the scene.
        '''
        self.running = True
        while self.running:
            self.getInput()
            self.updateLogic()
            self.updateDisplay()
            pygame.display.update(self.dirty_rects)
            self.game.clock.tick(self.game.fps)