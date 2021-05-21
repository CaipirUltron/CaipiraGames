import pygame, sys, math
from pygame.locals import *
from pygame.math import *
from classes.basics.tilemap2 import Background, Tile, TileMap
from classes.basics import BasicSprite, BasicGroup
from classes.cameras import Camera

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

pygame.init()
screen = pygame.display.set_mode(WINXP_RESOLUTION)
pygame.display.set_caption("Test Sprite Tiles")
timer = pygame.time.Clock()

print(screen.get_rect())

radius = 640
height = 32

player_image = pygame.image.load('player.png')
player_size = player_image.get_size()
player_offset = (player_size[0]/2, player_size[1]/2)

player_speed = 5
player_pos = Vector2(0,1000)
player_angle = 0
player = BasicSprite(player_image, player_offset, position=player_pos, orientation=player_angle, pivot_flag=True)

camera = Camera(player, WINXP_RESOLUTION)

all_sprites = TileMap( camera, radius, height, 'map1' )

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
            player_angle += event.y

    if left:
        player_pos += pygame.math.Vector2(-player_speed,0)
    if right:
        player_pos += pygame.math.Vector2(player_speed,0)
    if up:
        player_pos += pygame.math.Vector2(0,-player_speed)
    if down:
        player_pos += pygame.math.Vector2(0,player_speed)

    player.set_pose(position=player_pos, orientation=player_angle)

    x, y = camera.screen2world( (mouse_x,mouse_y) )
    value, indexes = all_sprites.get_value( x, y )

    print("Material = " + str(value))
    print("Indexes = " + str(indexes))

    tile_angle += -1
    all_sprites.update()

    screen.fill((0, 0, 0))
    dirty_rects = all_sprites.draw(screen)

    pygame.display.update(dirty_rects)
    timer.tick(60)