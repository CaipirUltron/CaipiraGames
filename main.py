'''
Main game code. 
Creates GM (Game Manager object) to control the game.
Creates game scenes and executes the runningLoop() of the active scene.
'''

from classes import GameManager
from classes.scenes.menus import MainMenu
from classes.scenes.ingame.level import Level
from classes.transitions import Fade, Transition

if not 'game_manager' in locals():
    GM = GameManager()

MainMenu(GM, "MainMenu")
Level(GM, "GameScene")

Transition(GM, 'Empty')
Fade(GM, 'FadeOut', type='out', period = 1)
Fade(GM, 'FadeIn', type='in', period = 1)
Fade(GM, 'SmoothFade', type='smooth', period = 1)

GM.setActiveScene("MainMenu")

if __name__ == '__main__':
    while True:
        if GM.active_scene:
            GM.active_scene.runningLoop()
        else:
            raise Exception("Game has no active scene!")