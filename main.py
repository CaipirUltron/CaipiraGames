import pygame as pg
import random

# Initialize pygame
pg.init()

# Create the screen
screen_resolution = (800,600) # has to be tuple
screen = pg.display.set_mode(screen_resolution)

# Title and Icon
pg.display.set_caption("CaipiraGames")
icon = pg.image.load("caipiragames.png") # doesn't show the icon at the top-left corner of the game screen on Ubuntu
pg.display.set_icon(icon)

# Player
playerImg = pg.image.load("caipiragames.png")
playerX = screen_resolution[0]/2
playerY = screen_resolution[1]/2
playerSpeed = 0.2
playerSpeedX = 0.0
playerSpeedY = 0.0

# Player
enemyImg = pg.image.load("caipiragames.png")
enemyX = random.randint(0,screen_resolution[0]-enemyImg.get_rect().size[0])
enemyY = random.randint(0,screen_resolution[1]-enemyImg.get_rect().size[1])
enemySpeed = 0.2
enemySpeedX = 0.0
enemySpeedY = 0.0

# Method for player positioning
def move_player(x, y):

    player_pos = (x, y)
    screen.blit(playerImg, player_pos)

# Method for enemy positioning
def move_enemy(x, y):

    enemy_pos = (x, y)
    screen.blit(enemyImg, enemy_pos)

print(playerImg.get_rect().size)

# Game loop
screen_base_color_white = (255, 255, 255)
running = True
while running:

    screen.fill(screen_base_color_white)

    for event in pg.event.get():

        # Quit if player exists game window
        if event.type == pg.QUIT:
            running = False

        # Checks if some key was pressed
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                playerSpeedX += -1.0
            if event.key == pg.K_RIGHT:
                playerSpeedX += +1.0
            if event.key == pg.K_UP:
                playerSpeedY += -1.0
            if event.key == pg.K_DOWN:
                playerSpeedY += +1.0
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                playerSpeedX -= -1.0
            if event.key == pg.K_RIGHT:
                playerSpeedX -= +1.0
            if event.key == pg.K_UP:
                playerSpeedY -= -1.0
            if event.key == pg.K_DOWN:
                playerSpeedY -= +1.0

    normalization_factor = ( playerSpeedX**2 + playerSpeedY**2 )**0.5
    if normalization_factor != 0.0:
        playerX += playerSpeed*playerSpeedX/normalization_factor
        playerY += playerSpeed*playerSpeedY/normalization_factor

    if playerX <= 0:
        playerX = 0.0
    elif playerX >= screen_resolution[0]-playerImg.get_rect().size[0]:
        playerX = screen_resolution[0]-playerImg.get_rect().size[0]

    if playerY <= 0:
        playerY = 0.0
    elif playerY >= screen_resolution[1]-playerImg.get_rect().size[1]:
        playerY = screen_resolution[1]-playerImg.get_rect().size[1]

    # Updates game window
    move_player(playerX, playerY)
    move_enemy(enemyX, enemyY)

    pg.display.update()