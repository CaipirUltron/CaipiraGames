import pygame
from scene import Scene
from spiral import Spiral

class Button():
    def __init__(self, x, y, width, height):
        self.clickable = False
        self.text = ""
        self.rect = pygame.Rect(0,0,width,height)
        self.rect.center = (x,y)
        self.isPressed = False

class MainMenu(Scene):
    def __init__(self, game, name):
        super().__init__(game, name)

        self.reset_keys()
        self.cursor_state = "Start"
        self.cursorRect = pygame.Rect(0,0,20,20)
        self.offset = -100
        self.background = pygame.image.load("caipirultron.png")
        self.spiral = Spiral(color=pygame.Color("WHITE"))

        self.start_x, self.start_y = self.game.center_x, self.game.center_y + 30
        self.options_x, self.options_y = self.game.center_x, self.game.center_y + 50
        self.credits_x, self.credits_y = self.game.center_x, self.game.center_y + 70
        self.cursorRect.midtop = (self.start_x + self.offset, self.start_y)

    def draw_text(self, text, size, x, y, font_name=None):
        if font_name:
            font = pygame.font.Font(font_name, size)
        else:
            font = pygame.font.Font(self.default_font_name, size)
        
        text_surface = font.render(text, True, pygame.Color("WHITE"))
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.game.screen.blit(text_surface, text_rect)

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def eventHandler(self, event):
        '''
        This method handles an event in the queue.
        '''
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

    def updateLogic(self):
        '''
        This method encapsulates the Scene logic, and is responsible for updating the Scene state.
        '''
        if self.DOWN_KEY:
            if self.cursor_state == "Start":
                self.cursorRect.midtop = (self.options_x + self.offset, self.options_y)
                self.cursor_state = "Options"
            elif self.cursor_state == "Options":
                self.cursorRect.midtop = (self.credits_x + self.offset, self.credits_y)
                self.cursor_state = "Credits"
            elif self.cursor_state == "Credits":
                self.cursorRect.midtop = (self.start_x + self.offset, self.start_y)
                self.cursor_state = "Start"
        elif self.UP_KEY:
            if self.cursor_state == "Start":
                self.cursorRect.midtop = (self.credits_x + self.offset, self.credits_y)
                self.cursor_state = "Credits"
            elif self.cursor_state == "Options":
                self.cursorRect.midtop = (self.start_x + self.offset, self.start_y)
                self.cursor_state = "Start"
            elif self.cursor_state == "Credits":
                self.cursorRect.midtop = (self.options_x + self.offset, self.options_y)
                self.cursor_state = "Options"

        if self.START_KEY:
            if self.cursor_state == "Start":
                '''
                Transition to "MainGame" scene.
                '''
                self.changeScene("MainGame")
            elif self.cursor_state == "Options":
                pass
            elif self.cursor_state == "Credits":
                pass

        self.reset_keys()

    def updateDisplay(self):
        '''
        This method updates the display.
        '''
        self.game.screen.fill(pygame.Color("BLACK"))
        self.draw_text("Main Menu", 20, self.game.center_x, self.game.center_y - 20)

        # Draws texts
        self.draw_text("Start Game",20, self.start_x, self.start_y)
        self.draw_text("Options",20, self.options_x, self.options_y)
        self.draw_text("Credits",20, self.credits_x, self.credits_y)

        # Draws cursor
        self.draw_text(">", 15, self.cursorRect.x, self.cursorRect.y)

        # Draws spirals
        self.spiral.drawDots(self.game.screen, self.game.center_x, self.game.center_y)