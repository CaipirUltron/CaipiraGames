import pygame, math
from pygame.locals import *
from classes.scenes import Scene
from itertools import cycle

default_text_color = pygame.Color("WHITE")
default_font_name = pygame.font.get_default_font()

class MainMenu(Scene):
    def __init__(self, game, name):
        super().__init__(game, name)

        self.center_x = 150
        self.center_y = self.game.center_y/2

        self.title = Button(text='Free Squid', font_size=24, x=self.center_x, y=self.center_y - 20)

        self.buttons = {
            "Start Game": Button(text="Start Game", x=self.center_x, y=self.center_y + 30),
            "Options":    Button(text="Options", x=self.center_x, y=self.center_y + 50),
            "Credits":    Button(text="Credits", x=self.center_x, y=self.center_y + 70),
            "Exit":    Button(text="Exit", x=self.center_x, y=self.center_y + 90),
        }
        self.mouse_x, self.mouse_y = 0.0, 0.0

        self.cursor = Button(text='o', font_size=20)

        self.cursor_offset = -50
        self.cursor_state = "Start Game"
        self.cursor.x = self.buttons[self.cursor_state].x + self.cursor_offset
        self.cursor.y = self.buttons[self.cursor_state].y

        self.spiral = Spiral(color=pygame.Color("WHITE"), size=self.game.height/2)

        self.reset_keys()
        self.init_state()

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.CLICKING = False, False, False, False, False

    def init_state(self):
        self.ON_EXIT = False

    def getInput(self):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
            if event.type == pygame.KEYUP:
                pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.CLICKING = True

    def updateLogic(self):
        self.cursor.x = self.mouse_x
        self.cursor.y = self.mouse_y

        for key in self.buttons:
            self.buttons[key].pressed = False
            if self.buttons[key].rect.collidepoint(self.mouse_x, self.mouse_y):
                self.buttons[key].setFontSize(20)
                if self.CLICKING:
                    self.buttons[key].pressed = True
                    self.ON_EXIT = True
                    if key == "Start Game":
                        self.game.transformScene('GameScene', 'SmoothFade')
                        pass
                    elif key == "Exit":
                        pygame.quit()
                        exit()
            else:
                self.buttons[key].setFontSize(12)

        self.reset_keys()

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("BLACK"))

        self.title.draw(self.game.screen)

        # Draws texts
        for key in self.buttons:
            self.buttons[key].draw(self.game.screen)

        self.cursor.draw(self.game.screen)                                                     # draw cursor
        self.spiral.drawDots(self.game.screen, self.game.center_x, self.game.center_y)         # draw spirals

class Cursor():
    def __init__(self, cursor_text):
        self.text = cursor_text

class Button():
    def __init__(self, text='', text_color=default_text_color, x=0.0, y=0.0, font_name=None, font_size=12):
        self.pressed = False
        self.x, self.y = x, y
        
        if font_name:
            self.font_name = font_name
        else:
            self.font_name = default_font_name
        self.setFontSize(font_size)
        self.setText(text, text_color)

    def setFontSize(self, font_size):
        self.font_size = font_size
        self.font = pygame.font.Font(self.font_name, self.font_size)

    def setText(self, text, text_color=default_text_color):
        self.text = text
        self.text_color = text_color
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surf.get_rect()
  
    def draw(self, screen):
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surf.get_rect()      
        self.rect.center = (self.x,self.y)
        screen.blit(self.text_surf, self.rect)

class Dot():
    def __init__(self, x, y, addAngle=5, increase=0):
        self.x, self.y = x, y
        self.dist = y-450
        self.angle = 0
        self.addAngle = addAngle
        self.increase = increase

    def move(self, center_x, center_y):
        self.angle+=self.dist/self.addAngle
        self.x=center_x+math.cos(math.radians(self.angle))*self.dist
        self.y=center_y+math.sin(math.radians(self.angle))*self.dist
        self.dist+=self.increase

class Spiral():
    def __init__(self, numberDots=500, thickness=1, size=300, color=pygame.Color("BLACK")):
        self.numberDots = numberDots
        self.thickness = thickness
        self.size = size
        self.color = color

        self.dots = [] 
        for i in range(self.numberDots):
            self.dots.append(Dot(450,450+i*self.size/self.numberDots))

    def draw(self,number, screen):
        if number != 0:
            pygame.draw.line(screen,self.color,(self.dots[number].x,self.dots[number].y),(self.dots[number-1].x,self.dots[number-1].y),self.thickness)

    def drawDots(self, screen, center_x, center_y):
        number = 0
        for dot in self.dots:
            self.draw(number, screen)
            dot.move(center_x, center_y)
            number += 1