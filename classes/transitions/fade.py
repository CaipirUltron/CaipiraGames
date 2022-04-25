import pygame

from pygame.locals import *
from classes.transitions import Transition


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

        self.wait_time = 0

    def set_type(self, type):
        self.type = type.lower()

    def onEnter(self):
        super().onEnter()

        if self.type == 'out' or self.type == 'smooth':
            self.opacity = 0
            self.fading_out = True
            self.waiting = False
            self.fading_in = False

        elif self.type == 'in':
            self.opacity = 255

        elif self.type == 'empty':
            self.opacity = 0

    def onExit(self):
        super().onExit()
        self.opacity = 0

    def updateDisplay(self):
        '''
        Main update code.
        '''
        if self.type == 'out':
            self.fadeout()
        elif self.type == 'in':
            self.fadein()
        elif self.type == 'smooth':
            self.smooth(1000)
        elif self.type == 'empty':
            self.empty()

        self.transparency_mask.set_alpha(self.opacity)
        self.game.screen.blit(self.transparency_mask, (0, 0))

    def wait(self, ms):
        '''
        Waiting function. Waits for ms milliseconds.
        '''
        if self.wait_time >= ms:
            self.wait_time = 0
            return True
        else:
            self.wait_time += self.game.deltaTime
            return False

    def fadeout(self):
        '''
        Fade out method.
        '''
        self.opacity += round(255*self.game.deltaTime/(1000*self.fade_period))
        if self.opacity >= 255:
            self.opacity = 255
            self.game.setActiveScene(self.game.next_scene)
            self.running = False

    def fadein(self):
        '''
        Fade in method.
        '''
        self.opacity -= round(255*self.game.deltaTime/(1000*self.fade_period))
        if self.opacity <= 0:
            self.opacity = 0
            self.game.setActiveScene(self.game.next_scene)
            self.running = False

    def smooth(self, waiting_time):
        '''
        Smooth transition between scenes by: (i) fading out, (ii) waiting some time and (iii) fading in to the next scene.
        '''
        if self.fading_out:
            self.opacity += round(255*self.game.deltaTime/(1000*self.fade_period))
            if self.opacity >= 255:
                self.opacity = 255
                self.fading_out = False
                self.waiting = True

        if self.waiting:
            if self.wait(waiting_time):
                self.game.setActiveScene(self.game.next_scene)
                self.waiting = False
                self.fading_in = True

        if self.fading_in:
            self.opacity -= round(255*self.game.deltaTime/(1000*self.fade_period))
            if self.opacity <= 0:
                self.opacity = 0
                self.fading_in = False
                self.running = False

    def empty(self):
        '''
        Method for empty transition.
        '''
        self.game.setActiveScene(self.game.next_scene)
        self.running = False