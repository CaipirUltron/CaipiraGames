from pygame.constants import FULLSCREEN
from profilehooks import profile

import pygame, sys
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

@profile
def main():
    screen = pygame.display.set_mode(HD720_RESOLUTION)
    screen_rect = screen.get_rect()

    fps = 60.0
    clock = pygame.time.Clock()

    background = pygame.Surface( (500,500) )
    background.fill(pygame.Color("WHITE"))
    bg_center = np.array([ HD720_RESOLUTION[0]/2, HD720_RESOLUTION[1]/2 ])
    background_rect = background.get_rect(center=(bg_center[0],bg_center[1]))

    square = pygame.Surface( (50,50) )
    square.fill(pygame.Color("RED"))
    square_rect = square.get_rect(center=(250,250))
    background.blit(square, square_rect)

    curr_mouse_pos = np.array(pygame.mouse.get_pos())
    scroll_holding = False

    running = True
    while running:

        dirty_rects = []

        # Compute intersection btw the screen and background
        intersect = background_rect.clip(screen_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if background_rect.collidepoint(event.pos):
                    scroll_holding = True
            if event.type == pygame.MOUSEBUTTONUP:
                scroll_holding = False
            if event.type == pygame.MOUSEMOTION and scroll_holding:
                background_rect.move_ip(event.rel)

        '''
        Scrolling logic.
        '''
        last_mouse_pos = curr_mouse_pos
        curr_mouse_pos = np.array([mouse_x, mouse_y])
        if scroll_holding:
            error = curr_mouse_pos - last_mouse_pos
            bg_center += error

        # Update background center
        background_rect.center = bg_center.tolist()

        # portion_to_blit = pygame.Rect( ( background_rect.x, background_rect.y, intersect.width, intersect.height ) )
        portion_to_blit = background_rect.copy()
        portion_to_blit.width = intersect.width
        portion_to_blit.height = intersect.height

        dirty_rects.append( screen.fill(pygame.Color("BLACK"), rect=intersect) )
        # dirty_rects.append( screen.blit(background, background_rect, area=intersect) )
        # dirty_rects.append( screen.blit(background, background_rect) )
        dirty_rects.append( screen.blit(background, background_rect) )

        print("Background = " + str(background_rect)  + ", Intersection = " + str(intersect) + ", Area to blit = " + str(portion_to_blit))

        pygame.display.update(dirty_rects)
        clock.tick(fps)

if __name__ == '__main__':
    main()