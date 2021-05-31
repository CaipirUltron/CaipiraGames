import pygame, pymunk, sys
from pygame.locals import *
from pygame.math import *

from classes.basics import Ball
from classes.basics.tilemap2 import TileMap, Background
from classes.cameras import Camera, follow
from classes.characters.player2 import Player

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
space = pymunk.Space()
space.gravity = 0, 200

print(screen.get_rect())

radius = 640
height = 32

bg = Background()
player_image = pygame.image.load('player.png')
player_size = player_image.get_size()
player_offset = (player_size[0]/2, player_size[1]/2)

player = Player()
ball = Ball(space, 30)

camera = Camera(player, follow, HD720_RESOLUTION)

all_sprites = TileMap( camera, 'map1' )
# all_sprites.add(bg)
all_sprites.add(ball)

left, right, up, down = False, False, False, False

tile_angle = 0

while True:

    dirty_rects = []
    mouse_x, mouse_y = pygame.mouse.get_pos()

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
        if event.type == MOUSEWHEEL:
            player.orientation += event.y

    x, y = camera.screen2world( (mouse_x,mouse_y) )
    value, indexes = all_sprites.get_value( x, y )

    # print("Material = " + str(value))
    # print("Indexes = " + str(indexes))

    tile_angle += -1
    all_sprites.update()

    screen.fill((0, 0, 0))
    all_sprites.draw(screen)

    print("Ball position = " + str(ball.position))

    pygame.display.update()
    space.step(1/60)
    timer.tick(60)