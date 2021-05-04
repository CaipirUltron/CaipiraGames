import pygame
import math

from classes.scene import Scene
from classes.player import Player

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

        self.screen = pygame.display.set_mode(HD720_RESOLUTION)
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

class MainGame(Scene):
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.deltaTime = 1/self.game.fps
        self.player = Player("images/sprites/player", self.deltaTime)
        self.polygonalLevel = PolygonalLevel(32, 2000, 20, center_x=self.game.center_x, center_y=-4*self.game.center_y)

    def eventHandler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.startMovement(event.key)
            if event.key == pygame.K_ESCAPE:
                self.changeScene("MainMenu")
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.player.endMovement(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.holding = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.holding = False

    def updateLogic(self):
        self.player.followMouse(float(self.mouse_x), float(self.mouse_y))
        self.player.update()

    def updateDisplay(self):
        self.game.screen.fill(pygame.Color("Black"))
        self.player.draw(self.game.screen)
        # self.polygonalLevel.drawPoints(self.game.screen)
        self.polygonalLevel.drawLines(self.game.screen)
        print("Level distortion = " + str(self.polygonalLevel.level_distortion))

class PolygonalLevel():
    def __init__(self, tile_size, level_radius, level_height, center_x=0.0, center_y=0.0):
        self.center_x = center_x
        self.center_y = center_y
        self.setLevel(tile_size, level_radius, level_height)

    def setLevel(self, tile_size, level_radius, num_layers):    
        if type(tile_size) != int:
            raise Exception("Tile size must be and integer.")
        if type(num_layers) != int:
            raise Exception("Number of layers must an integer.")
        if num_layers*tile_size >= level_radius:
            raise Exception("Level height must be smaller than the level radius.")

        self.tile_size = tile_size       # tile size, in pixels
        self.level_radius = level_radius # level height, in pixels
        self.num_layers = num_layers     # number of layers

        self.num_sides = round(math.pi/math.atan2(self.tile_size, 2*self.level_radius))
        if self.num_sides < 3:
            self.num_sides = 3
        self.level_radius = self.tile_size/(2*math.tan(math.pi/self.num_sides))

        self.level_distortion = 2*self.num_layers*math.tan(math.pi/self.num_sides)

        self.angle = 2*math.pi/self.num_sides
        self.height_offset = self.level_radius - self.num_layers*self.tile_size

        self.tiles_x = []
        self.tiles_y = []
        self.num_points = self.num_sides*self.num_layers

        for angle_index in range(self.num_sides):
            for level_index in range(1,self.num_layers+1):
                self.tiles_x.append( self.center_x + ( self.height_offset + self.tile_size*level_index )*math.cos( self.angle*angle_index - self.angle/2 ) )
                self.tiles_y.append( self.center_y + ( self.height_offset + self.tile_size*level_index )*math.sin( self.angle*angle_index - self.angle/2 ) )

    def drawPoints(self, screen):
        for i in range(self.num_points):
            pygame.draw.circle(screen, (255, 0, 0), ( self.tiles_x[i], self.tiles_y[i] ), 1 )

    def drawLines(self, screen):
        for i in range(self.num_sides):
            start_point_x = self.center_x + self.tile_size*math.cos( self.angle*i - self.angle/2 )
            start_point_y = self.center_y + self.tile_size*math.sin( self.angle*i - self.angle/2 )
            start_point = (start_point_x, start_point_y)

            end_point_x = self.center_x + self.level_radius*math.cos( self.angle*i - self.angle/2 )
            end_point_y = self.center_y + self.level_radius*math.sin( self.angle*i - self.angle/2 )
            end_point = (end_point_x, end_point_y)

            pygame.draw.line(screen, (0, 0, 255), start_point, end_point )

            for j in range(1,self.num_layers+1):
                start_point_x = self.center_x + ( self.height_offset + self.tile_size*j )*math.cos( self.angle*i - self.angle/2 )
                start_point_y = self.center_y + ( self.height_offset + self.tile_size*j )*math.sin( self.angle*i - self.angle/2 )
                start_point = (start_point_x, start_point_y)

                end_point_x = self.center_x + ( self.height_offset + self.tile_size*j )*math.cos( self.angle*(i+1) - self.angle/2 )
                end_point_y = self.center_y + ( self.height_offset + self.tile_size*j )*math.sin( self.angle*(i+1) - self.angle/2 )
                end_point = (end_point_x, end_point_y)

                pygame.draw.line(screen, (0, 0, 255), start_point, end_point )
