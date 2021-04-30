import sys
import pygame

from game import *

pygame.init()
pygame.display.set_caption("Caipira Games")
pygame.display.set_icon(pygame.image.load("caipiragames.png"))

game = Game()
game.playing = True

while game.running:
    """ 
    Main game loop.
    """
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         pygame.quit()
    #         sys.exit()
    
    # game.curr_menu.display_menu()
    game.runGameLoop()