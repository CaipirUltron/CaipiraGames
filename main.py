import sys
import pygame as pg

from character import *

WHITE = (255, 255, 255)

SCREEN_COLOR = WHITE
FHD_RESOLUTION = (1920,1080)
HD_RESOLUTION = (1280,720)
GAME_FPS = 40.0

deltaTime = 1/GAME_FPS

# Initialize pygame
pg.init()
gameClock = pg.time.Clock()
screen = pg.display.set_mode(HD_RESOLUTION)

pg.display.set_caption("CaipiraGames")
icon = pg.image.load("caipiragames.png") # doesn't show the icon at the top-left corner of the game screen on Ubuntu
pg.display.set_icon(icon)

# Player and enemy
player = Player("sprites/player", HD_RESOLUTION, deltaTime, x=0.0, y=0.0)
enemy = Enemy("sprites/enemy", HD_RESOLUTION, deltaTime)

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

    print(player.speed_x,player.speed_y)

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
    pg.time.delay(50)
    screen.fill(SCREEN_COLOR)

    # # Quit if player exists game window
    # for event in pg.event.get():
    #     if event.type == pg.QUIT:
    #         running = False

        # # Checks if some key was pressed
        # if event.type == pg.KEYDOWN:
        #     if event.key == pg.K_LEFT:
        #         playerSpeedX += -1.0
        #     if event.key == pg.K_RIGHT:
        #         playerSpeedX += +1.0
        #     if event.key == pg.K_UP:
        #         playerSpeedY += -1.0
        #     if event.key == pg.K_DOWN:
        #         playerSpeedY += +1.0
        # if event.type == pg.KEYUP:
        #     if event.key == pg.K_LEFT:
        #         playerSpeedX -= -1.0
        #     if event.key == pg.K_RIGHT:
        #         playerSpeedX -= +1.0
        #     if event.key == pg.K_UP:
        #         playerSpeedY -= -1.0
        #     if event.key == pg.K_DOWN:
        #         playerSpeedY -= +1.0

    # normalization_factor = ( playerSpeedX**2 + playerSpeedY**2 )**0.5
    # if normalization_factor != 0.0:
    #     playerX += playerSpeed*playerSpeedX/normalization_factor
    #     playerY += playerSpeed*playerSpeedY/normalization_factor

    # if playerX <= 0:
    #     playerX = 0.0
    # elif playerX >= HD_RESOLUTION[0]-playerImg.get_rect().size[0]:
    #     playerX = HD_RESOLUTION[0]-playerImg.get_rect().size[0]

    # if playerY <= 0:
    #     playerY = 0.0
    # elif playerY >= HD_RESOLUTION[1]-playerImg.get_rect().size[1]:
    #     playerY = HD_RESOLUTION[1]-playerImg.get_rect().size[1]

    # # Updates game window
    # move_player(playerX, playerY)
    # move_enemy(enemyX, enemyY)

    eventHandling()
    redrawGameWindow()

    # Limit game to 40 fps
    gameClock.tick(GAME_FPS)