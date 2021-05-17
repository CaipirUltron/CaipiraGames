import pygame

PHONE_RESOLUTION = (1440,2960)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

class Game():
    '''
    Main game class, encapsulating every game scene (menus, transitions, loading screens, the game itself, etc).
    Also contains main game parameters.
    '''
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caipira Games")
        pygame.display.set_icon(pygame.image.load("./images/caipiragames.png"))

        self.screen = pygame.display.set_mode(HD1080_RESOLUTION)
        self.screen_rect = self.screen.get_rect()
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        self.center_x = self.width/2
        self.center_y = self.height/2

        self.fps = 60.0
        self.clock = pygame.time.Clock()

        self.scenes = [] # a list with the game scenes
        self.active_scene = None # current active scene

    def addScene(self, scene):
        '''
        Adds a new scene object to the game.
        '''
        self.scenes.append(scene)

    def removeScene(self, scene_name):
        '''
        Removes the scene with name "scene_name" from the game.
        '''
        for scene in self.scenes:
            if scene.name == scene_name:
                self.scenes.remove(scene)
                break

    def setActiveScene(self, scene_name):
        '''
        Sets a scene from self.scenes with name "scene name" as the active scene.
        '''
        for scene in self.scenes:
            if scene.name == scene_name:
                self.active_scene = scene
                break