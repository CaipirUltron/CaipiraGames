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
        self.clock = pygame.time.Clock()

        self.scenes = {} # a list with the game scenes
        self.active_scene = None # current active scene

    def addScene(self, scene):
        if not scene.id in self.scenes.keys():
            self.scenes[scene.id] = scene
        else:
            raise Exception("The scene you are trying to add already exists in the game.")

    def removeScene(self, scene_id):
        try:
            del self.scenes[scene_id]
        except KeyError:
            print("An error occurred when trying to remove the scene from game.\n Scene not found.")

    def setActiveScene(self, scene_id):
        try:
            if self.active_scene:
                self.active_scene.running = False
            self.active_scene = self.scenes[scene_id]
        except KeyError:
            print("An error occurred when setting a new active scene.\n Scene not found.")