import pygame, math

from scene import Scene
from characters import Player

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


class MainGame(Scene):
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, game, name):
        super().__init__(game, name)
        self.deltaTime = 1/self.game.fps
        self.player = Player("sprites/player", self.deltaTime)
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