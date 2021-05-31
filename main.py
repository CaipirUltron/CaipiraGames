from classes import Game
from classes.scenes.menus import MainMenu
from classes.scenes.ingame.level import Level

# Game settings
game_manager = Game()

# Scenes
main_menu = MainMenu(game_manager, "MainMenu")
main_game = Level(game_manager, "GameScene")

game_manager.addScene(main_menu)
game_manager.addScene(main_game)

game_manager.setActiveScene("GameScene")

if __name__ == '__main__':
    while True:
        game_manager.active_scene.runningLoop()