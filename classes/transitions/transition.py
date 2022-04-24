import pygame
from pygame.locals import *

class Transition():
    '''
    Class for defining scene transitions. Defines an empty transition and can be inherited for more complex transitions.
    A condition setting self.running = False must be defined; otherwise the transition will finish but the next scene will not be loaded.
    '''
    def __init__(self, game, name):

        self.game = game
        self.id = name
        self.game.addTransition(self)

        self.running = False

    def onEnter(self):
        '''
        Executed only once, upon entering the transition.
        '''
        pass

    def onExit(self):
        '''
        Executed only once, upon exiting the transition.
        '''
        pass

    def updateDisplay(self):
        '''
        The empty transition simply changes the scene imediately.
        '''
        self.game.setActiveScene(self.game.next_scene)
        self.running = False


class Fade(Transition):
    '''
    Class for fading out/in transition.
    '''
    def __init__(self, game, name, type = 'smooth', period = 1):
        super().__init__(game, name)

        self.set_type(type)
        self.fade_period = period
        self.transparency_mask = pygame.Surface(self.game.screen_rect.size)
        self.transparency_mask.fill(Color("BLACK"))
        self.fading_out = False
        self.fading_in = False

    def set_type(self, type):
        self.type = type

    def onEnter(self):
        '''
        Starting flags and opacity appropriately.
        '''
        if self.type == 'out' or self.type == 'smooth':
            self.opacity = 0
            self.fading_out = True
            self.fading_in = False

        elif self.type == 'in':
            self.opacity = 255
            self.fading_out = False
            self.fading_in = True

    def onExit(self):
        self.opacity = 0

    def updateDisplay(self):
        
        self.fade()
        self.transparency_mask.set_alpha(self.opacity)
        self.game.screen.blit(self.transparency_mask, (0, 0))

    def fade(self):
        '''
        Fading method. Note the conditions self.running = False, signaling the end of the transition.
        '''
        if self.fading_out:
            self.opacity += round(255*self.game.deltaTime/(1000*self.fade_period))
            if self.opacity >= 255:
                self.opacity = 255
                self.fading_out = False
                self.game.setActiveScene(self.game.next_scene)
                if self.type == 'smooth':
                    self.fading_in = True
                elif self.type == 'out':
                    self.running = False

        if self.fading_in:
            self.opacity -= round(255*self.game.deltaTime/(1000*self.fade_period))
            if self.opacity <= 0:
                self.opacity = 0
                self.fading_in = False
                if self.type == 'in' or self.type == 'smooth':
                    self.running = False