import pygame

from scene import Scene
from characters import Player

class Game(Scene):
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, screen):
        super().__init__(screen)
        
        self.deltaTime = 1/self.fps
        self.player = Player("sprites/player", (self.width, self.height), self.deltaTime)

    def eventHandler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.startMovement(event.key)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.endMovement(event.key)

    def updateLogic(self):
        self.player.update()

    def updateDisplay(self):
        self.screen.fill(pygame.Color("Black"))
        self.player.draw(self.screen)