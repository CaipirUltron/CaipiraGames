import sys

import pygame
from pygame.locals import *

import pymunk, pymunk.pygame_util

from classes.scenes import Scene
from classes.common import TileMap
from classes.objects import Background
from classes.cameras import Camera, follow
from classes.characters.player import Player


class LevelEditor(Scene):
    '''
    Game level editor scene.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.curr_material = 1
        self.buttons = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "mouse_left": False,
            "mouse_scroll": False,
            "mouse_right": False
        }

        self.button_separation = 40
        self.button_radius = 15
        self.ponter_size = 8
        self.mouse_x, self.mouse_y = 0.0, 0.0
        self.x, self.y = 0.0, 0.0
        self.value_at = 0
        self.indexes_at = (0,0)

        # Creates some objects
        self.player = Player()
        self.bg = Background()

        # Add camera
        self.camera = Camera(self.player, follow, (self.game.width, self.game.height))
        
        # Initialize level
        self.filename = 'map1'
        self.map = TileMap.from_file( self.filename, self.camera, self.space )
        self.draw_options = pymunk.pygame_util.DrawOptions(self.game.screen)

        # Adds more objects to the map
        self.map.add(self.player)
        # self.map.add(self.bg)

    def getInput(self):

        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                self.map.save_level(self.filename)
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.buttons["left"] = True
                if event.key == K_RIGHT:
                    self.buttons["right"] = True
                if event.key == K_UP:
                    self.buttons["up"] =True
                if event.key == K_DOWN:
                    self.buttons["down"] = True
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    self.buttons["left"] = False
                if event.key == K_RIGHT:
                    self.buttons["right"] = False
                if event.key == K_UP:
                    self.buttons["up"] = False
                if event.key == K_DOWN:
                    self.buttons["down"] = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.buttons["mouse_left"] = True
                if event.button == 2:
                    self.buttons["mouse_scroll"] = True
                if event.button == 3:
                    self.buttons["mouse_right"] = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.buttons["mouse_left"] = False
                if event.button == 2:
                    self.buttons["mouse_scroll"] = False
                if event.button == 3:
                    self.buttons["mouse_right"] = False
            if event.type == MOUSEWHEEL:
                # self.player.orientation += event.y
                if event.y < 0:
                    self.curr_material += 1
                if event.y > 0:
                    self.curr_material -= 1
  
    def updateLogic(self):
        
        # Loop on the number of materials
        if self.curr_material > self.map.num_materials:
            self.curr_material = 1
        elif self.curr_material < 1:
            self.curr_material = self.map.num_materials

        # Get material and indexes at the mouse position
        x, y = self.camera.screen2world( (self.mouse_x, self.mouse_y) )
        self.value_at, self.indexes_at = self.map.get_value_at( x, y )

        print("World coordinates = ", x, y )
        print("Material = " + str(self.value_at))
        print("Indexes = " + str(self.indexes_at))

        # if self.indexes_at == (0,0):
        #     self.game.transformScene('MainMenu', 'Smooth')

        # Update map matrix
        if self.indexes_at:
            if self.buttons["mouse_left"]:
                self.map.set_value_at(self.curr_material, self.indexes_at)
            if self.buttons["mouse_right"]:
                self.map.set_value_at(0, self.indexes_at)

        self.map.update()

    def updateDisplay(self):
        self.game.screen.fill(Color("BLACK"))
        self.map.draw(self.game.screen)

        # # Update tiles
        # if self.indexes_at:
        #     touching_tiles = self.map.get_tiles_at(self.mouse_x, self.mouse_y)
        #     if touching_tiles:
        #         for tile in touching_tiles:
        #             if self.buttons["mouse_left"]:
        #                 self.space.remove(tile.shape, tile.body)
        #                 tile.kill()
        #                 self.map.add_tile(self.indexes_at, self.map.materials[self.map.tilegrid[self.indexes_at]])
        #             if self.buttons["mouse_right"]:
        #                 self.space.remove(tile.shape, tile.body)
        #                 tile.kill()
        #     else:
        #         if self.buttons["mouse_left"]:
        #             self.map.add_tile(self.indexes_at, self.map.materials[self.map.tilegrid[self.indexes_at]])

        # Draw mouse pointer
        pygame.draw.circle(self.game.screen, self.map.materials[self.curr_material], (self.mouse_x,self.mouse_y), self.ponter_size )

        # Draw menu
        for material in self.map.materials:
            pygame.draw.circle(self.game.screen, self.map.materials[material], ( 2*self.button_radius , int(material)*self.button_separation ), self.button_radius )

        # self.space.debug_draw(self.draw_options)