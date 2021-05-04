from classes.game import Game
from classes.scenes.menus.main_menu import MainMenu
from classes.scenes.game_scenes.game_scene import GameScene

myGame = Game()

mainMenu = MainMenu(myGame, "MainMenu")
mainGame = GameScene(myGame, "GameScene")

myGame.addScene(mainMenu)
myGame.addScene(mainGame)

myGame.setActiveScene("MainMenu")
# myGame.setActiveScene("MainGame")

if __name__ == '__main__':
    while True:
        myGame.active_scene.runningLoop()