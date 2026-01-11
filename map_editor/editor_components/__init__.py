"""
Tile Editor Components Package

Modular components for the tile editor to improve maintainability and scalability.
"""

from .configs import EditorConfig, EditorColors, EditorText
from .tileset_manager import TilesetManager
from .file_manager import FileManager
from .ui_panel import UIPanel
from .palette_panel import PalettePanel
from .map_canvas import MapCanvas
from .event_handler import EventHandler
from .autotile_manager import AutoTileManager

__all__ = [
    'EditorConfig',
    'EditorColors',
    'EditorText',
    'TilesetManager',
    'FileManager',
    'UIPanel',
    'PalettePanel',
    'MapCanvas',
    'EventHandler',
    'AutoTileManager',
]
