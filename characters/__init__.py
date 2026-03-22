from .character import *
from .player import *
import os

# Redirect top-level `characters` package to `src/characters`
_here = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(_here, '..', 'src', 'characters'))
if os.path.isdir(src_path) and src_path not in __path__:
    __path__.insert(0, src_path)
