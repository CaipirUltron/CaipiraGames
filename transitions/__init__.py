from .transition import *
from .fade import *
import os

# Redirect top-level `transitions` package to `src/transitions`
_here = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(_here, '..', 'src', 'transitions'))
if os.path.isdir(src_path) and src_path not in __path__:
    __path__.insert(0, src_path)
