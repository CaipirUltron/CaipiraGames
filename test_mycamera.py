import pygame, sys, math
from pygame.locals import *
from pygame.math import Vector2
from classes.basics.sprite_tilemap import Background, Tile, TileMap
from classes.cameras import Camera, CameraAwareGroup

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

x, y, angle = 0, 300, 0
radius = 160
height = 16
num_floors = 10
num_sides = 3
phi = 2*math.pi/num_sides

tileBG = Background( radius, height, num_floors, num_sides )
player = Tile(radius,height,phi, (x, y), angle, Color("BLUE"))
# tile2 = Tile(radius+height,height,phi, x, y, angle, Color("BLUE"))

# tileMap = CameraAwareGroup( player, HD720_RESOLUTION )
# tileMap.add( player )
# tileMap.add( tileBG )

tileMap = TileMap( player, HD720_RESOLUTION, radius, height, 'map1' )

left, right, up, down = False, False, False, False

while True:

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

    if left:
        dir = Vector2()
        player.rect.centerx -= 5
    if right:
        player.rect.centerx += 5
    if up:
        player.rect.centery -= 5
    if down:
        player.rect.centery += 5

    player.angle += 1

    print("Player pos = " + str(player.rect.center))
    print("Player angle = " + str(player.angle))

    tileMap.update(mouse_x, mouse_y)

    screen.fill((0, 0, 0))
    tileMap.draw(screen)

    pygame.display.update()
    timer.tick(60)