import pygame, time, sys
import numpy as np

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

pygame.init()
pygame.display.set_caption("Caipira Games")
pygame.display.set_icon(pygame.image.load("./images/caipiragames.png"))

screen = pygame.display.set_mode(HD720_RESOLUTION)
screen_rect = screen.get_rect()

fps = 60.0
clock = pygame.time.Clock()

background = pygame.Surface( (500,500) ).convert_alpha()
background.fill(pygame.Color("WHITE"))
bg_center = np.array([ 250, 250 ])
background_rect = background.get_rect(center=(bg_center[0],bg_center[1]))

print(background_rect)

square = pygame.Surface( (50,50) )
square.fill(pygame.Color("RED"))
square_rect = square.get_rect(topleft=(20,20))

last_mouse_pos = np.zeros(2)
curr_mouse_pos = np.array(pygame.mouse.get_pos())
scroll_holding = False

running = True
while running:

    screen.fill(pygame.Color("BLACK"))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                pass
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                pass
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                scroll_holding = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                scroll_holding = False
    '''
    Scrolling logic.
    '''
    last_mouse_pos = curr_mouse_pos
    curr_mouse_pos = np.array([mouse_x, mouse_y])
    if scroll_holding:
        error = curr_mouse_pos - last_mouse_pos
        bg_center += error

    # Update background
    background_rect.center = bg_center.tolist()
    intersect = background_rect.clip(screen_rect)

    screen.fill(pygame.Color("BLACK"), rect=intersect)
    screen.blit(background, background_rect, area=intersect)
    
    print(intersect)

    pygame.display.update()
    clock.tick(fps)