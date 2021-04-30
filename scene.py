from abc import ABC, abstractmethod
import pygame

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    def __init__(self, running=False, fps=30):
        self.running = running
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.events = []

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
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    break
                self.eventHandler(event)
            self.updateLogic()
            self.updateDisplay()

        self.clock.tick(self.fps)