import pygame, sys
from pygame.locals import *

from classes.scenes import Scene
from classes.basics.tilemap import TileMap, Background
from classes.cameras import Camera, follow
from classes.characters.player import Player

class Level(Scene):
    '''
    Class for an example game level.
    '''
    def __init__(self, game, name):
        super().__init__(game, name)

        self.curr_material = 1
        self.buttons = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        # Add player
        self.player = Player()

        # Add camera
        self.camera = Camera(self.player, follow, (self.game.width, self.game.height))

        # Initialize level
        self.level = TileMap( self.camera, 'map1' )

        # Add background
        background = Background()
        self.level.add(background)

    def getInput(self):

        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.level.save_level(self.filename)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.buttons["left"] = True
                if event.key == pygame.K_RIGHT:
                    self.buttons["right"] = True
                if event.key == pygame.K_UP:
                    self.buttons["up"] =True
                if event.key == pygame.K_DOWN:
                    self.buttons["down"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.buttons["left"] = False
                if event.key == pygame.K_RIGHT:
                    self.buttons["right"] = False
                if event.key == pygame.K_UP:
                    self.buttons["up"] = False
                if event.key == pygame.K_DOWN:
                    self.buttons["down"] = False
            if event.type == MOUSEWHEEL:
                self.player.orientation += event.y
  
    def updateLogic(self):
        
        # Loop on the number of materials
        if self.curr_material > self.level.num_materials:
            self.curr_material = 1
        elif self.curr_material < 1:
            self.curr_material = self.level.num_materials

        x, y = self.camera.screen2world( (self.mouse_x,self.mouse_y) )
        value, indexes = self.level.get_value( x, y )

        print("Material = " + str(value))
        print("Indexes = " + str(indexes))

        self.level.update()

    def updateDisplay(self):
        self.game.screen.fill((0, 0, 0))
        self.level.draw(self.game.screen)