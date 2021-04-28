import sys
import pygame

from game import *

pygame.init()
pygame.display.set_caption("Caipira Games")
pygame.display.set_icon(pygame.image.load("caipiragames.png"))

game = Game()

while game.running:
    """ 
    Main game loop.
    """
    game.curr_menu.display_menu()
    game.runGameLoop()