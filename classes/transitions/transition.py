from pygame.locals import *

class Transition():
    '''
    Class for defining scene transitions. Defines an empty transition and can be inherited for more complex transitions.
    A condition setting self.running = False must be defined somewhere; otherwise the transition will never finish.
    '''
    def __init__(self, game, name):

        self.game = game
        self.id = name
        self.game.addTransition(self)

        self.running = False

    def onEnter(self):
        '''
        Executed only once, upon entering the transition.
        '''
        print("Starting transition " + str(self.id))

    def onExit(self):
        '''
        Executed only once, upon exiting the transition.
        '''
        print("Finishing transition " + str(self.id))

    def updateDisplay(self):
        '''
        The empty transition simply changes the scene imediately.
        '''
        self.game.setActiveScene(self.game.next_scene)
        self.running = False