import pygame

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)


class GameManager():
    '''
    Main game class, encapsulating every game scene (menus, transitions, loading screens, the game itself, etc).
    Contains game parameters and configurations.
    '''
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caipira Games")
        pygame.display.set_icon(pygame.image.load("./images/caipiragames.png"))

        self.screen = pygame.display.set_mode(HD720_RESOLUTION)
        self.screen_rect = self.screen.get_rect()
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.center_x = self.width/2
        self.center_y = self.height/2

        self.fps = 60.0
        self.fixed_deltaTime = 1/self.fps
        self.clock = pygame.time.Clock()
        self.deltaTime = 0

        self.scenes = {}                # Dictionary with the game scenes
        self.active_scene = None        # Current active scene. Only one of the scenes is active at any given time.
        self.next_scene = None          # Next scene to be loaded, after transition finishes.

        self.transitions = {}           # Dictionary with the game transitions
        self.active_transition = None   # Current active transition. Transitions are active just for a brief period of time; when no transition is occurring, this variable is set to None.

    # Scene management -------------------------------------------------------------------------------

    def addScene(self, scene):
        if not scene.id in self.scenes.keys():
            self.scenes[scene.id] = scene
        else:
            raise Exception("The scene you are trying to add is already defined.")

    def removeScene(self, scene_id):
        if scene_id in self.scenes.keys():
            del self.scenes[scene_id]
        else: 
            raise Exception("Scene not found.")

    def setActiveScene(self, scene_id):
        '''
        Imediately changes the current active scene.
        '''
        try:
            if self.active_scene:
                self.active_scene.onExit()
                self.active_scene.running = False
            self.active_scene = self.scenes[scene_id]
            self.active_scene.onEnter()
        except KeyError:
            print("An error occurred when setting a new active scene.\nScene not found.")

    # Transition management ---------------------------------------------------------------------------

    def addTransition(self, transition):
        if not transition.id in self.transitions.keys():
            self.transitions[transition.id] = transition
        else:
            raise Exception("The transition you are trying to add is already defined.")

    def removeTransition(self, transition_id):
        if transition_id in self.transitions.keys():
            del self.transitions[transition_id]
        else:
            raise Exception("Transition not found.")

    def transformScene(self, scene_id, transition_id):
        '''
        Changes the current active scene using a transition.
        '''
        if transition_id in self.transitions.keys():
            self.active_transition = self.transitions[transition_id]
            if not self.active_transition.running:
                self.active_transition.running = True
                self.active_transition.onEnter()
        else:
            raise Exception("An error occurred when starting the transition.\nTransition not found.")

        # Marks next scene to be loaded, after transition is finished.
        self.next_scene = scene_id