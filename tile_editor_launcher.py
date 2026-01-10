#!/usr/bin/env python3
'''
Standalone launcher for the tile editor.
'''

from classes.scenes.game.tile_editor import TileEditor

if __name__ == '__main__':
    editor = TileEditor()
    editor.run()
