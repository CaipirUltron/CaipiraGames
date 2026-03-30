from .game_object import *
from .tilemap import *
from .circular_tilemap import *
from .state_machine import StateMachine
from .animation import SpriteAnimation
import os

# Redirect top-level `common` package to `src/common`
_here = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(_here, '..', 'src', 'common'))
if os.path.isdir(src_path) and src_path not in __path__:
    __path__.insert(0, src_path)
