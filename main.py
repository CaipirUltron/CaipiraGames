import pygame as pg

# Initialize pygame
pg.init()

# Create the screen
screen_resolution = (800,600)
screen = pg.display.set_mode(screen_resolution)

# Game loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False