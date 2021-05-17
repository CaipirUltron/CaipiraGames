import pygame, sys, math
from pygame.locals import *
from classes.scenes.game_scenes.tile_map import Tile

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

pygame.init()
screen = pygame.display.set_mode(HD720_RESOLUTION)
pygame.display.set_caption("Test Sprite Tiles")
timer = pygame.time.Clock()

tile = Tile(500,40,math.pi/100, Color("BLUE"))

x, y = 500, 500
tileMap = pygame.sprite.Group()
tileMap.add(tile)

left, right, up, down = False, False, False, False

while True:
    for event in pygame.event.get():
        if event.type == QUIT: 
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False

    tileMap.update()

    screen.fill((0, 0, 0))
    tileMap.draw(screen)

    pygame.display.update()
    timer.tick(60)