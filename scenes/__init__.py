from .scene import *
import os

# Make this package a thin wrapper that exposes the modules from src/scenes
# by inserting the real src/scenes path at the front of the package __path__.
_here = os.path.dirname(__file__)
src_scenes = os.path.abspath(os.path.join(_here, '..', 'src', 'scenes'))
if os.path.isdir(src_scenes) and src_scenes not in __path__:
    __path__.insert(0, src_scenes)

# Nothing else needed — users can now `import scenes.game` which will load
# the module from `src/scenes/game.py`.
