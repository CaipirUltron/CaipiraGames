import pygame
from scene import Scene
from spiral import Spiral

default_text_color = pygame.Color("WHITE")
default_font_name = pygame.font.get_default_font()

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

class MainMenu(Scene):
    def __init__(self, game, name):
        super().__init__(game, name)

        self.center_x = 150
        self.center_y = self.game.center_y/2

        self.title = Button(text='Caipira Game', font_size=24, x=self.center_x, y=self.center_y - 20)

        self.buttons = {
            "Start Game": Button(text="Start Game", x=self.center_x, y=self.center_y + 30),
            "Options":    Button(text="Options", x=self.center_x, y=self.center_y + 50),
            "Credits":    Button(text="Credits", x=self.center_x, y=self.center_y + 70)
        }

        self.cursor = Button(text='o', font_size=20)

        self.cursor_offset = -50
        self.cursor_state = "Start Game"
        self.cursor.x = self.buttons[self.cursor_state].x + self.cursor_offset
        self.cursor.y = self.buttons[self.cursor_state].y

        self.spiral = Spiral(color=pygame.Color("WHITE"), size=self.game.height/2)

        self.reset_keys()

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.CLICKING = False, False, False, False, False

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.CLICKING = True

    def updateLogic(self):
        '''
        This method encapsulates the Scene logic, and is responsible for updating the Scene state.
        '''
        # if self.DOWN_KEY:
        #     if self.cursor_state == "Start Game":
        #         self.cursor.y = self.buttons["Options"].y
        #         self.cursor_state = "Options"
        #     elif self.cursor_state == "Options":
        #         self.cursor.y = self.buttons["Credits"].y
        #         self.cursor_state = "Credits"
        #     elif self.cursor_state == "Credits":
        #         self.cursor.y = self.buttons["Start Game"].y
        #         self.cursor_state = "Start Game"
        # elif self.UP_KEY:
        #     if self.cursor_state == "Start":
        #         self.cursor.y = self.buttons["Credits"].y
        #         self.cursor_state = "Credits"
        #     elif self.cursor_state == "Options":
        #         self.cursor.y = self.buttons["Start Game"].y
        #         self.cursor_state = "Start Game"
        #     elif self.cursor_state == "Credits":
        #         self.cursor.y = self.buttons["Options"].y
        #         self.cursor_state = "Options"

        self.cursor.x = self.mouse_x
        self.cursor.y = self.mouse_y

        for key in self.buttons:
            if self.buttons[key].rect.collidepoint(self.mouse_x, self.mouse_y):
                self.buttons[key].setFontSize(20)
                if self.CLICKING:
                    if key == "Start Game":
                        self.changeScene("MainGame")
                    elif key == "Options":
                        self.changeScene("MainGame")
                    elif key == "Credits":
                        self.changeScene("MainGame")
            else:
                self.buttons[key].setFontSize(12)

        # if self.START_KEY:
        #     if self.cursor_state == "Start Game":
        #         '''
        #         Transition to "MainGame" scene.
        #         '''
        #         self.changeScene("MainGame")
        #     elif self.cursor_state == "Options":
        #         self.changeScene("MainGame")
        #     elif self.cursor_state == "Credits":
        #         self.changeScene("MainGame")

        self.reset_keys()

    def updateDisplay(self):
        '''
        This method updates the display.
        '''
        self.game.screen.fill(pygame.Color("BLACK"))

        self.title.draw(self.game.screen)

        # Draws texts
        for key in self.buttons:
            self.buttons[key].draw(self.game.screen)

        # Draws cursor
        self.cursor.draw(self.game.screen)

        # Draws spirals
        self.spiral.drawDots(self.game.screen, self.game.center_x, self.game.center_y)