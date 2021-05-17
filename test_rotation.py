#Imports
import random
import pygame
from pygame.locals import *

# Pygame initialization
pygame.init()

fps = 120
sample_time = 1/fps

# Class for creating test object
class Object(pygame.sprite.Sprite):

    # Init
    def __init__(self):
        super(Object, self).__init__()
        self.og_surf = pygame.transform.smoothscale(pygame.image.load("new_bullet.jpg").convert(), (300, 300))
        # self.og_surf = pygame.Surface((32,32))
        # self.og_surf.fill(Color("RED"))
        self.surf = self.og_surf
        self.rect = self.surf.get_rect(center=(400, 400))
        self.angle = 0
        self.change_angle = 0

    # THE MAIN ROTATE FUNCTION
    def rot(self):
        self.surf = pygame.transform.rotate(self.og_surf, self.angle)
        self.angle += self.change_angle*sample_time
        # self.angle = self.angle % 360
        self.rect = self.surf.get_rect(center=self.rect.center)

    # Move for keypresses
    def move(self, li):
        self.change_angle = 0
        if li[K_LEFT]:
            self.change_angle = 60
        elif li[K_RIGHT]:
            self.change_angle = -60
        obj.rot()


# Assigning required vars
run = True
screen = pygame.display.set_mode((800, 800))
obj = Object()
obj.angle = random.randint(50, 100)
obj.rect.x = 300
obj.rect.y = 299
all_sprites = pygame.sprite.Group()
all_sprites.add(obj)

timer = pygame.time.Clock()
# Main run loop
while run:
    # Screen fill
    screen.fill((50, 50, 50))

    # Getting presses for move
    presses = pygame.key.get_pressed()

    # Closing the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    # Rendering and rotating
    for x in all_sprites:
        x.move(presses)
        screen.blit(x.surf, x.rect)

    # Flipping and setting framerate
    pygame.display.update()
    timer.tick(fps)

# Quit
pygame.quit()