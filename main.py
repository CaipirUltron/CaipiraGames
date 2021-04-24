import pygame as pg

# Initialize pygame
pg.init()

# Create the screen
screen_resolution = (800,600) # has to be tuple
screen = pg.display.set_mode(screen_resolution)

# Title and Icon
pg.display.set_caption("CaipiraGames")
icon = pg.image.load("caipiragames.png") # doesn't work on Ubuntu (probably)
pg.display.set_icon(icon)

# Game loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # RGB - Red, Green, Blue
    RGB_tuple = (255, 0, 0)
    screen.fill(RGB_tuple)

    # Updates game window
    pg.display.update()