from .common_objects import *
import os

# Redirect top-level `objects` package to `src/objects`
_here = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(_here, '..', 'src', 'objects'))
if os.path.isdir(src_path) and src_path not in __path__:
    __path__.insert(0, src_path)
