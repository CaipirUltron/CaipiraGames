import pygame
import math

from pygame.math import Vector2
from classes.basics.basic_sprite import BasicSprite

pygame.init()
size = (400,400)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

image = pygame.image.load('boomerang.png')
image_size = image.get_size()
pivot = ( image_size[0]/2, image_size[1]/2 )

pos, angle = Vector2(200,200), 0

sprite = BasicSprite(image, pivot, pos, angle, pivot_flag=True)

sprites = pygame.sprite.Group()
sprites.add( sprite )

running = False
while not running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = True
    screen.fill('white')

    pos += Vector2(0,0)
    angle += 1
    sprite.set_pose(position=pos, orientation=angle)

    sprites.draw(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()