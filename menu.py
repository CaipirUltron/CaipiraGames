import pygame

BLACK, WHITE = (0,0,0), (255,255,255)

class Menu():
    def __init__(self, game):
        self.game = game
        self.MID_RES = (self.game.RESOLUTION[0]/2, self.game.RESOLUTION[1]/2)
        self.isRunning = True
        self.cursor_rect = pygame.Rect(0,0,20,20)
        self.offset = -100
        self.background = pygame.image.load("caipirultron.png")


    def draw_cursor(self):
        self.game.draw_text(">", 15, self.cursor_rect.x, self.cursor_rect.y)
    
    def blit_screen(self):
        self.game.display.blit(self.background, self.MID_RES)
        self.game.window.blit(self.game.display, (0,0))
        pygame.display.update()
        self.game.reset_keys()

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start"
        self.start_x, self.start_y = self.MID_RES[0], self.MID_RES[1] + 30
        self.options_x, self.options_y = self.MID_RES[0], self.MID_RES[1] + 50
        self.credits_x, self.credits_y = self.MID_RES[0], self.MID_RES[1] + 70
        self.cursor_rect.midtop = (self.start_x + self.offset, self.start_y)

    def display_menu(self):
        self.isRunning = True
        while self.isRunning:

            self.game.handleGameEvents()
            self.check_input()
            self.game.display.fill(BLACK)
            self.game.draw_text("Main Menu", 20, self.MID_RES[0], self.MID_RES[1] - 20)
            self.game.draw_text("Start Game",20, self.start_x, self.start_y)
            self.game.draw_text("Options",20, self.options_x, self.options_y)
            self.game.draw_text("Credits",20, self.credits_x, self.credits_y)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Start":
                self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
                self.state = "Options"
            elif self.state == "Options":
                self.cursor_rect.midtop = (self.credits_x + self.offset, self.credits_y)
                self.state = "Credits"
            elif self.state == "Credits":
                self.cursor_rect.midtop = (self.start_x + self.offset, self.start_y)
                self.state = "Start"
        elif self.game.UP_KEY:
            if self.state == "Start":
                self.cursor_rect.midtop = (self.credits_x + self.offset, self.credits_y)
                self.state = "Credits"
            elif self.state == "Options":
                self.cursor_rect.midtop = (self.start_x + self.offset, self.start_y)
                self.state = "Start"
            elif self.state == "Credits":
                self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
                self.state = "Options"

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == "Start":
                self.game.playing = True
            elif self.state == "Options":
                pass
            elif self.state == "Credits":
                pass
            self.isRunning = False