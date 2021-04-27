import sys
import pygame as pg

from character import *

WHITE = (255, 255, 255)

SCREEN_COLOR = WHITE
FHD_RESOLUTION = (1920,1080)
HD_RESOLUTION = (1280,720)
GARBAGE_RESOLUTION = (800, 600)
GAME_FPS = 60.0

deltaTime = 1/GAME_FPS
gameResolution = GARBAGE_RESOLUTION

# Initialize pygame
pg.init()
gameClock = pg.time.Clock()
screen = pg.display.set_mode(gameResolution)

pg.display.set_caption("CaipiraGames")
icon = pg.image.load("caipiragames.png") # doesn't show the icon at the top-left corner of the game screen on Ubuntu
pg.display.set_icon(icon)

# Player and enemy
player = Player("sprites/player", gameResolution, deltaTime, x=0.0, y=0.0)
enemy = Enemy("sprites/enemy", gameResolution, deltaTime)

def startMovement(pressed_key):
    player_speed_x = player.speed_x
    player_speed_y = player.speed_y
    if pressed_key == pg.K_LEFT:
        player_speed_x += -1
    if pressed_key == pg.K_RIGHT:
        player_speed_x += +1
    if pressed_key == pg.K_UP:
        player_speed_y += -1
    if pressed_key == pg.K_DOWN:
        player_speed_y += +1
    player.move(player_speed_x, player_speed_y)

def endMovement(released_key):
    player_speed_x = player.speed_x
    player_speed_y = player.speed_y
    if released_key == pg.K_LEFT:
        player_speed_x -= -1
    if released_key == pg.K_RIGHT:
        player_speed_x -= +1
    if released_key == pg.K_UP:
        player_speed_y -= -1
    if released_key == pg.K_DOWN:
        player_speed_y -= +1
    player.move(player_speed_x, player_speed_y)

def eventHandling():
    """
    Method for handling all pygame events.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT or event.key == pg.K_RIGHT or event.key == pg.K_UP or event.key == pg.K_DOWN:
                startMovement(event.key)
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT or event.key == pg.K_RIGHT or event.key == pg.K_UP or event.key == pg.K_DOWN:
                endMovement(event.key)

def redrawGameWindow():
    """
    Method for redrawing the game window.
    """
    player.draw(screen)
    pg.display.update()

while True:
    """
    Main game loop
    """
    screen.fill(SCREEN_COLOR)

    eventHandling()
    redrawGameWindow()

    gameClock.tick(GAME_FPS)