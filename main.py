import sys
import pygame
import math

from game import *
from menus import *

HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

pygame.init()
pygame.display.set_caption("Caipira Games")
pygame.display.set_icon(pygame.image.load("caipiragames.png"))
screen = pygame.display.set_mode(WINXP_RESOLUTION)

# All scenes are instanciated here (in practice, they must be created and instantiated at runtime).
menu_scene = Menu(screen)
game_scene = Game(screen)

menu_scene.running = True
menu_scene.runningLoop()