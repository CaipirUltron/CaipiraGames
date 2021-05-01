import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    def __init__(self, game, name, default_font_name=pygame.font.get_default_font()):
        self.game = game
        self.name = name
        self.running = False
        self.default_font_name = default_font_name

    def changeScene(self, scene_name):
        self.game.setActiveScene(scene_name)
        print(self.game.active_scene.name + " is active.")
        self.running = False
        
    @abstractmethod
    def eventHandler(self, event):
        '''
        This method handles an event in the queue.
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    break
                self.eventHandler(event)
            self.updateLogic()
            self.updateDisplay()
            pygame.display.update()
            self.game.clock.tick(self.game.fps)