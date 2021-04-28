import sys, os, os.path
import pygame

from menu import MainMenu

GAME_FPS = 60.0
BLACK, WHITE = (0,0,0), (255,255,255)
HD1080_RESOLUTION = (1920,1080)
HD720_RESOLUTION = (1280,720)
WINXP_RESOLUTION = (800, 600)
HD1080_SMALL_RESOLUTION = (480, 270)
ATARI_RESOLUTION = (192, 160)

def get_sprites(sprite_folder):
    """ 
    Method for getting sprites from a given folder. Returns a list of 
    """
    sprites = []
    for file_name in os.listdir(sprite_folder):
        file_path = sprite_folder+"/"+file_name
        sprites.append( pygame.image.load(file_path) )
    return sprites

class Game:
    """ 
    General game class, encapsulating the game state.
    """
    def __init__(self, game_res=HD720_RESOLUTION):
        self.running, self.playing = True, False
        self.clock = pygame.time.Clock()
        self.reset_keys()

        self.RESOLUTION = game_res
        self.window = pygame.display.set_mode(self.RESOLUTION)

        self.display = pygame.Surface(self.window.get_size())
        self.font_name = pygame.font.get_default_font()

        self.player = Player("sprites/player", self.RESOLUTION, 1/GAME_FPS)
        self.curr_menu = MainMenu(self)

    def runGameLoop(self):
        """ 
        Internal game loop.
        """
        self.display.fill(BLACK)
        while self.playing:

            self.handleGameEvents()

            if self.START_KEY:
                self.playing = False

            self.player.update()
            self.window.blit(self.display, (0,0))
            self.player.draw(self.window)

            pygame.display.update()
            self.reset_keys()

            self.clock.tick(GAME_FPS)

    def handleGameEvents(self):
        """
        Method for handling all game events occurring inside of the game.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.isRunning = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.player.startMovement(event.key)
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.player.endMovement(event.key)

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface, text_rect)

class Character():
    """ 
    Abstract class for general game character.
    General attributes are (x,y) positions, width and height, animation sprites, etc.
    """
    def __init__(self, sprite_folder, screen_res, deltaTime, x=0.0, y=0.0):
        self.sprite_folder = sprite_folder
        self.screen_resolution = screen_res
        self.deltaTime = deltaTime

        self.x, self.y = x, y
        self.speed_x, self.speed_y = 0.0, 0.0
        self.default_speed = 50.0

        self.idle_sprites = get_sprites(self.sprite_folder+"/idle")
        self.walk_sprites = get_sprites(self.sprite_folder+"/walk")

        self.current_sprite = self.idle_sprites[0]

        self.width = self.current_sprite.get_rect().size[0]
        self.height = self.current_sprite.get_rect().size[1]

    def get_position(self):
        return self.x, self.y

    def check_wall_collision(self):
        if self.x <= 0:
            self.x = 0.0
        elif self.x >= self.screen_resolution[0]-self.width:
            self.x = self.screen_resolution[0]-self.width
        if self.y <= 0:
            self.y = 0.0
        elif self.y >= self.screen_resolution[1]-self.height:
            self.y = self.screen_resolution[1]-self.height

    def set_speed(self, vel_x, vel_y):
        self.speed_x = vel_x
        self.speed_y = vel_y

    def update(self):
        normalization_factor = ( self.speed_x**2 + self.speed_y**2 )**0.5
        if normalization_factor != 0.0:
            self.x += self.deltaTime*self.default_speed*self.speed_x/normalization_factor
            self.y += self.deltaTime*self.default_speed*self.speed_y/normalization_factor

        self.check_wall_collision()

    def draw(self, screen):
        screen.blit(self.current_sprite, (self.x, self.y) )

class Player(Character):
    """ 
    Class for the player character. The implementation of player controls can be found here.
    """
    def startMovement(self, pressed_key):
        if pressed_key == pygame.K_LEFT:
            self.speed_x += -1
        if pressed_key == pygame.K_RIGHT:
            self.speed_x += +1
        if pressed_key == pygame.K_UP:
            self.speed_y += -1
        if pressed_key == pygame.K_DOWN:
            self.speed_y += +1

    def endMovement(self, released_key):
        if released_key == pygame.K_LEFT:
            self.speed_x -= -1
        if released_key == pygame.K_RIGHT:
            self.speed_x -= +1
        if released_key == pygame.K_UP:
            self.speed_y -= -1
        if released_key == pygame.K_DOWN:
            self.speed_y -= +1

class Enemy(Character):
    """ 
    Class for an enemy character.
    The implementation of enemy controls and AI can be found here.
    """