import pygame, sys
from pygame.locals import *

clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_COLOR = WHITE
FHD_RESOLUTION = (1920,1080)
HD_RESOLUTION = (1280,720)
GARBAGE_RESOLUTION = (800, 600)
GAME_FPS = 60.0

pygame.init()
pygame.display.set_caption("Circular Tile Level Editor")

screen = pygame.display.set_mode(HD_RESOLUTION,0,32)

background_color = BLACK
tile = pygame.Rect(0, 0, 50, 50)

if __name__ == "__main__":
    while True:
        screen.fill(background_color)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        pygame.draw.rect(screen, (255, 0, 0), tile)

        pygame.display.update()
        clock.tick(60)