import pygame
from scene import Scene
from spiral import Spiral

default_color = pygame.Color("BLACK")
default_font_name = pygame.font.get_default_font()

class Cursor():
    def __init__(self, cursor_text):
        self.text = cursor_text

class Button():
    def __init__(self, text='', text_color=default_color, x=0.0, y=0.0, font_name=None, font_size=12):
        self.pressed = False

        if font_name:
            self.font = pygame.font.Font(font_name, font_size)
        else:
            self.font = pygame.font.Font(default_font_name, font_size)

        self.setText(text, text_color)
        self.draw(x, y)

    def setText(self, text, text_color=default_color):
        self.text = text
        self.text_color = text_color
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surf.get_rect()

    def draw(self, x, y):
        self.rect.center = (x,y)
        self.game.screen.blit(self.text_surf, self.rect)

class MainMenu(Scene):
    def __init__(self, game, name):
        super().__init__(game, name)

        self.buttons = []
        self.buttons.append( Button(text='Start Game', x=self.game.center_x, y=self.game.center_y + 30) )
        self.buttons.append( Button(text='Options', x=self.game.center_x, y=self.game.center_y + 50) )
        self.buttons.append( Button(text='Credits', x=self.game.center_x, y=self.game.center_y + 70) )

        self.cursor = Button(text='>', x=self.game.center_x, y=self.game.center_y + 30)

        self.reset_keys()
        self.cursor_state = "Start"
        self.cursorRect = pygame.Rect(0,0,20,20)
        self.cursor_offset = -100
        self.spiral = Spiral(color=pygame.Color("WHITE"))
        self.cursorRect.midtop = (self.start_x + self.cursor_offset, self.start_y)

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