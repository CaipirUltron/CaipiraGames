import pygame
from scene import Scene

class Menu(Scene):
    def __init__(self):
        super().__init__()
    
    def eventHandler(self, event):
        '''
        This method handles an event in the queue.
        '''
        pass

    def updateLogic(self):
        '''
        This method encapsulates the Scene logic, and is responsible for updating the Scene state.
        '''
        pass

    def updateDisplay(self):
        '''
        This method updates the display.
        '''
        print("Updating the display")

# This works
menu = Menu()
window = pygame.display.set_mode((300,200))

menu.running = True
menu.runningLoop()