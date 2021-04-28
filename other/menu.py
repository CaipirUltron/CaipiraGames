import pygame, sys
from pygame.locals import *

mainClock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption("Game Menu")

screen = pygame.display.set_mode((500,500),0,32)
font = pygame.font.SysFont(None, 20)

background_color = (0,0,0)
text_color = (255,255,255)

def draw_text(text, font, color, surface, x, y):
    textObj = font.render(text, 1, color)
    textRect = textObj.get_rect()
    textRect.topleft = (x,y)
    surface.blit(textObj, textRect)

click = False

def main_menu():
    while True:

        screen.fill(background_color)
        draw_text("Main Menu", font, text_color, screen, 20, 20)

        mx, my = pygame.mouse.get_pos()

        button1_pos = (50, 100)
        button2_pos = (50, 200)

        button1 = pygame.Rect(button1_pos[0], button1_pos[1], 200, 50)
        button2 = pygame.Rect(button2_pos[0], button2_pos[1], 200, 50)

        if button1.collidepoint((mx, my)):
            if click:
                game()
        if button2.collidepoint((mx, my)):
            if click:
                options()

        pygame.draw.rect(screen, (255, 0, 0), button1)
        pygame.draw.rect(screen, (255, 0, 0), button2)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.type == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)

def game():
    running = True
    while running:
        screen.fill(background_color)
        draw_text("Game", font, text_color, screen, 20, 20)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Escape")
                    running = False
        pygame.display.update()
        mainClock.tick(60)

def options():
    running = True
    while running:
        screen.fill(background_color)
        draw_text("Options", font, text_color, screen, 20, 20)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Escape")
                    running = False
        pygame.display.update()
        mainClock.tick(60)

main_menu()