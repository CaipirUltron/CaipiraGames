import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    '''
    Basic class for a game scene. Always contains at least an eventHandler and a runningLoop method.
    Used as a parent class for game menus, screens and for the game itself.
    '''
    def __init__(self, screen, running=False, fps=30, default_font_name=pygame.font.get_default_font()):
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.running = running
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.default_font_name = default_font_name
        self.events = []

    @abstractmethod
    def eventHandler(self, event):
        '''
        This method handles an event in the queue.
        '''
        pass

    @abstractmethod
    def updateLogic(self):
        '''
        This method encapsulates the Scene logic, and is responsible for updating the Scene state.
        '''
        pass

    @abstractmethod
    def updateDisplay(self):
        '''
        This method updates the display.
        '''
        pass

    def runningLoop(self):
        '''
        Main loop for the scene.
        '''
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    break
                self.eventHandler(event)
            self.updateLogic()

            self.updateDisplay()
            pygame.display.update()
            self.clock.tick(self.fps)

    def draw_text(self, text, size, x, y, font_name=None):

        if font_name:
            font = pygame.font.Font(font_name, size)
        else:
            font = pygame.font.Font(self.default_font_name, size)
        
        text_surface = font.render(text, True, pygame.Color("WHITE"))
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.screen.blit(text_surface, text_rect)