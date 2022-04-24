'''
Main game code. 
Creates GM (Game Manager object) to control the game.
Creates game scenes and executes the runningLoop() of the active scene.
'''

import sys
from classes import GameManager
from classes.scenes.menus import MainMenu
from classes.scenes.ingame.level import Level

if not 'game_manager' in locals():
    GM = GameManager()

main_menu = MainMenu(GM, "MainMenu")
main_game = Level(GM, "GameScene")

GM.setActiveScene("GameScene")

if __name__ == '__main__':
    while True:
        if GM.active_scene:
            GM.active_scene.runningLoop()
        else:
            raise Exception("Game has no active scene!")