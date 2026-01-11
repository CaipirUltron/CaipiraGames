"""
Constants and configuration for the Tile Editor

This module contains all magic numbers, colors, dimensions, and configuration
values used throughout the tile editor, making them easy to modify and maintain.

Using frozen dataclasses ensures immutability and provides type hints.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class EditorConfig:
    """Configuration constants for editor layout and behavior"""
    
    # Screen dimensions
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 720
    FPS: int = 60
    
    # Tile dimensions
    TILE_SIZE: int = 32  # Size of each tile in the tileset PNG (16x16 pixels)
    MAP_TILE_SIZE: int = 32  # Display size of tiles on the map
    PALETTE_TILE_SIZE: int = 32  # Display size of tiles in the palette
    
    # Layout dimensions
    UI_PANEL_WIDTH: int = 220  # Width of left control panel
    UI_PANEL_X: int = 0  # X position of UI panel
    PALETTE_WIDTH: int = 200  # Width of right palette area
    TAB_HEIGHT: int = 30  # Height of tileset tabs at top of palette
    MAP_SPACING: int = 10  # Spacing between UI panel and map area
    
    # Grid constraints
    MIN_GRID_SIZE: int = 1
    MAX_GRID_SIZE: int = 200
    DEFAULT_MAP_COLS: int = 100
    DEFAULT_MAP_ROWS: int = 50
    
    # Camera movement
    CAMERA_SPEED: int = 10  # Pixels per frame when using arrow keys
    
    # Scrolling
    SCROLLBAR_WIDTH: int = 3
    SCROLLBAR_MIN_HEIGHT: int = 20
    SCROLLBAR_OFFSET: int = 5  # Distance from palette edge
    
    # Font sizes
    FONT_SIZE_NORMAL: int = 20
    FONT_SIZE_TITLE: int = 24
    FONT_SIZE_SMALL: int = 16
    
    # Button dimensions
    BUTTON_SMALL_SIZE: int = 30  # Width/height of +/- buttons
    BUTTON_VALUE_WIDTH: int = 130  # Width of value display buttons
    BUTTON_LARGE_WIDTH: int = 200  # Width of large buttons (Load Folder)
    BUTTON_HEIGHT: int = 30  # Standard button height
    
    # Tab display
    TAB_MIN_WIDTH: int = 30  # Minimum width per tab
    TAB_MAX_WIDTH: int = 80  # Maximum width per tab
    TAB_NAME_MAX_LENGTH: int = 8  # Max characters before truncation
    
    # File paths
    DEFAULT_TILESET_FOLDER: str = 'assets/tilesets/scifi'
    DEFAULT_SAVE_FILE: str = 'map_editor.json'


@dataclass(frozen=True)
class EditorColors:
    """Color constants for the editor UI"""
    
    # Background colors
    BG_COLOR: Tuple[int, int, int] = (40, 40, 50)
    UI_PANEL_BG: Tuple[int, int, int] = (50, 50, 60)
    PALETTE_BG: Tuple[int, int, int] = (60, 60, 70)
    
    # UI element colors
    GRID_COLOR: Tuple[int, int, int] = (80, 80, 90)
    SELECTION_COLOR: Tuple[int, int, int] = (255, 255, 100)
    BUTTON_COLOR: Tuple[int, int, int] = (70, 70, 80)
    BUTTON_HOVER_COLOR: Tuple[int, int, int] = (90, 90, 100)
    TEXT_COLOR: Tuple[int, int, int] = (200, 200, 200)
    TEXT_HIGHLIGHT_COLOR: Tuple[int, int, int] = (255, 255, 150)
    TEXT_DIM_COLOR: Tuple[int, int, int] = (150, 150, 150)
    
    # Border colors
    BORDER_COLOR: Tuple[int, int, int] = (200, 200, 200)
    TAB_BORDER_COLOR: Tuple[int, int, int] = (200, 200, 200)


@dataclass(frozen=True)
class EditorText:
    """Text constants and UI strings"""
    
    WINDOW_TITLE: str = "Tile Editor - CaipiraGames"
    
    # Button labels
    BUTTON_LOAD_FOLDER: str = "Load Folder..."
    BUTTON_MINUS: str = "-"
    BUTTON_PLUS: str = "+"
    
    # Section headers
    HEADER_CONTROLS: str = "=== CONTROLS ==="
    HEADER_TILESET: str = "=== TILESET ==="
    HEADER_GRID_SIZE: str = "=== GRID SIZE ==="
    HEADER_MAP_INFO: str = "=== MAP INFO ==="
    
    # Instructions (using tuple for immutability)
    INSTRUCTIONS: Tuple[str, ...] = (
        "=== CONTROLS ===",
        "Left Click: Paint",
        "Right Click: Erase",
        "Scroll Wheel: Scroll",
        "Arrow Keys: Pan Map",
        "",
        "Ctrl+S: Save",
        "Ctrl+L: Load",
        "Ctrl+N: Clear",
        "ESC: Exit",
    )
    
    # Labels
    LABEL_WIDTH: str = "Width:"
    LABEL_HEIGHT: str = "Height:"
    
    # Info format strings
    INFO_TILE: str = "Tile: {}"
    INFO_TOTAL: str = "Total: {} tiles"
    INFO_TILESET: str = "Tileset: {}"
    INFO_TILESET_LOADED: str = "{} loaded"
    INFO_TILESET_DETAILS: str = "{} ({})"
    
    # Tab text
    TAB_ELLIPSIS: str = "..."
    
    # File dialog
    DIALOG_TITLE_FOLDER: str = "Select Tileset Folder"
    DIALOG_INITIAL_DIR: str = "assets/tilesets"
    
    # Console messages
    MSG_MAP_SAVED: str = "Map saved!"
    MSG_MAP_LOADED: str = "Map loaded!"
    MSG_MAP_CLEARED: str = "Map cleared!"
    MSG_TILESET_LOADED: str = "Loaded tileset: {} ({} tiles)"
    MSG_TOTAL_TILESETS: str = "Total tilesets loaded: {}"
    MSG_NO_PNG_FILES: str = "No PNG files found in {}"
    MSG_ERROR_LOADING_TILESET: str = "Error loading {}: {}"
    MSG_ERROR_LOADING_FOLDER: str = "Error loading tileset folder: {}"
    MSG_FILE_NOT_FOUND: str = "File {} not found. Starting with empty map."
    MSG_ERROR_LOADING_MAP: str = "Error loading map: {}"
    
    # Empty tileset
    EMPTY_TILESET_NAME: str = "Empty"


# Create singleton instances for convenient access
# These are immutable due to frozen=True
config = EditorConfig()
colors = EditorColors()
text = EditorText()
