import pygame, pymunk
from pygame.locals import *
from abc import ABC, abstractmethod

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    def __init__(self, game, name):

        # Add reference to the GM
        self.game = game
        self.id = name
        self.game.addScene(self)

        # Scene parameters
        self.running = False
        self.update_all = True
        self.dirty_rects = []

        self.use_physics = True
        if self.use_physics:
            self.space = pymunk.Space()
        
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

    def onEnter(self):
        '''
        Executed only once, upon entering the scene.
        '''
        pass

    def onExit(self):
        '''
        Executed only once, upon exiting the scene.
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

            # Main execution occurs here -> gets player inputs, updates physics (if used) and game internal logic and draws current frame
            self.getInput()
            if self.use_physics:
                if not hasattr(self,'space'):
                    self.space = pymunk.Space()
                self.space.step(1/self.game.fps)
            self.updateLogic()
            self.updateDisplay()

            # Handles transitions from one scene to another
            if self.game.active_transition:
                self.game.active_transition.updateDisplay()
                if not self.game.active_transition.running:         # when transition is finished
                    self.game.next_scene = None
                    self.game.active_transition.onExit()
                    self.game.active_transition = None

            # Updates pygame display
            if self.update_all:
                pygame.display.update()
            else:
                pygame.display.update(self.dirty_rects)

            self.game.deltaTime = self.game.clock.tick(self.game.fps)       # computes time between frames