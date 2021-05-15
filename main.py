from classes import Game
from classes.scenes.menus import MainMenu
from classes.scenes.game_scenes import LevelEditor, SquidGame

myGame = Game()

mainMenu = MainMenu(myGame, "MainMenu")

# Comment out to execute the Squid Game
mainGame = LevelEditor(myGame, "GameScene")

# Comment out to execute the Tile Editor
# mainGame = SquidGame(myGame, "GameScene")

myGame.addScene(mainMenu)
myGame.addScene(mainGame)

myGame.setActiveScene("MainMenu")
# myGame.setActiveScene("GameScene")

if __name__ == '__main__':
    while True:
        myGame.active_scene.runningLoop()