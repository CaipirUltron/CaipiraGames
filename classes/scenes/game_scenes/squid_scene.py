import pygame
from pygame.locals import *
import math

from classes.scenes.scene import Scene
from classes.characters.player import Player

class SquidGame(Scene):
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.deltaTime = 1/self.game.fps
        self.player = Player("images/sprites/player", self.deltaTime)

    def eventHandler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.startMovement(event.key)
            if event.key == pygame.K_ESCAPE:
                self.changeScene("MainMenu")
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.endMovement(event.key)

    def updateLogic(self):
        self.player.followMouse(float(self.mouse_x), float(self.mouse_y))
        self.player.update()

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("Black"))
        self.player.draw(self.game.screen)