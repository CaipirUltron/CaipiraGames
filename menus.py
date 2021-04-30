import pygame
from scene import Scene
from spiral import Spiral

class Menu(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.reset_keys()
        self.cursor_state = "Start"
        self.MID_RES = (self.width/2, self.height/2)
        self.cursorRect = pygame.Rect(0,0,20,20)
        self.offset = -100
        self.background = pygame.image.load("caipirultron.png")
        self.spiral = Spiral(self.screen, color=pygame.Color("WHITE"))

        self.start_x, self.start_y = self.MID_RES[0], self.MID_RES[1] + 30
        self.options_x, self.options_y = self.MID_RES[0], self.MID_RES[1] + 50
        self.credits_x, self.credits_y = self.MID_RES[0], self.MID_RES[1] + 70
        self.cursorRect.midtop = (self.start_x + self.offset, self.start_y)

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
                self.running = True
            elif self.cursor_state == "Options":
                pass
            elif self.cursor_state == "Credits":
                pass
            self.running = False

        self.reset_keys()

    def updateDisplay(self):
        '''
        This method updates the display.
        '''
        self.screen.fill(pygame.Color("BLACK"))
        self.draw_text("Main Menu", 20, self.MID_RES[0], self.MID_RES[1] - 20)

        # Draws texts
        self.draw_text("Start Game",20, self.start_x, self.start_y)
        self.draw_text("Options",20, self.options_x, self.options_y)
        self.draw_text("Credits",20, self.credits_x, self.credits_y)

        # Draws cursor
        self.draw_text(">", 15, self.cursorRect.x, self.cursorRect.y)

        # Draws spirals
        self.spiral.drawDots()

        # Blits screen
        self.screen.blit(self.background, self.MID_RES)