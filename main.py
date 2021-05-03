from classes.game import *
from classes.main_menu import *
from classes.game import *

myGame = Game()

mainMenu = MainMenu(myGame, "MainMenu")
mainGame = MainGame(myGame, "MainGame")

myGame.addScene(mainMenu)
myGame.addScene(mainGame)

myGame.setActiveScene("MainMenu")
# myGame.setActiveScene("MainGame")

if __name__ == '__main__':
    while True:
        myGame.active_scene.runningLoop()