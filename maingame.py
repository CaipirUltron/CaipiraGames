import pygame

from scene import Scene
from characters import Player

class MainGame(Scene):
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.deltaTime = 1/self.game.fps
        self.player = Player("sprites/player", (self.game.width, self.game.height), self.deltaTime)

    def eventHandler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.startMovement(event.key)
            if event.key == pygame.K_ESCAPE:
                '''
                Transition to "MainMenu" scene.
                '''
                self.changeScene("MainMenu")
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.endMovement(event.key)

    def updateLogic(self):
        self.player.update()

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("Black"))
        self.player.draw(self.game.screen)