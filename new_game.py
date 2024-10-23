'''
Main game code. 
Creates GM (Game Manager object) to control the game.
Creates game scenes and executes the runningLoop() of the active scene.
'''
import pygame
from classes import GameManager
from classes.scenes.game import LevelEditor

if not 'game_manager' in locals(): GM = GameManager()

LevelEditor(GM, "LevelEditor")
GM.setActiveScene("LevelEditor")

if __name__ == '__main__':
    while True:
        if GM.active_scene:
            GM.active_scene.runningLoop()
        else:
            pygame.exit()
            raise Exception("Game has no active scene!")