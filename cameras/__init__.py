from .camera import *
import os

# Redirect top-level `cameras` package to `src/cameras`
_here = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(_here, '..', 'src', 'cameras'))
if os.path.isdir(src_path) and src_path not in __path__:
    __path__.insert(0, src_path)
