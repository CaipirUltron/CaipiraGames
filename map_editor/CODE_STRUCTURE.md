# Map Editor Code Structure & Configuration Guide

## Overview

This document explains the architecture of the map editor, its modular structure, and how to configure it for your needs.

## Package Architecture

```
map_editor/
├── __init__.py                  # Package exports (TileEditor)
├── tile_editor.py               # Main editor application (~865 lines)
├── editor_components/           # Configuration and utilities subpackage
│   ├── __init__.py             # Exports config dataclasses
│   └── configs.py              # All configuration dataclasses
├── README.md                   # User documentation & features
└── CODE_STRUCTURE.md           # This file
```

### Root Level
```
tile_editor_launcher.py          # Convenient launcher script
```

## Module Descriptions

### `tile_editor.py` - Main Editor Application

**Purpose**: Core editor implementation with multi-tileset support

**Key Classes**:
- `TileEditor`: Main editor class handling UI, rendering, input, and file I/O

**Key Features**:
- Multi-tileset loading from folders
- Tab-based tileset switching
- Grid painting with tile + tileset tracking
- Camera panning for large maps
- Save/load to JSON format
- File dialogs for user-friendly I/O

**Data Structures**:
- `map_grid`: 3D numpy array `(rows, cols, 2)` storing `[tileset_idx, tile_idx]`
- `tilesets`: List of loaded pygame surfaces
- `tile_images`: List of lists containing individual tile surfaces

**Usage**:
```python
from map_editor import TileEditor

editor = TileEditor()
editor.run()
```

### `editor_components/configs.py` - Configuration Dataclasses

**Purpose**: Centralized, immutable configuration using frozen dataclasses

**Why Frozen Dataclasses?**
- **Immutability**: Values cannot be accidentally modified at runtime
- **Type Safety**: Full type hints for better IDE support
- **Thread-safe**: Safe to share across application
- **Clear Intent**: These are configurations, not mutable state

#### Configuration Classes

##### 1. `EditorConfig` - Technical Settings

Core dimensions, speeds, and paths:

```python
@dataclass(frozen=True)
class EditorConfig:
    # Screen
    screen_width: int = 1280
    screen_height: int = 720
    
    # Tiles
    tile_size: int = 16
    palette_tile_size: int = 32
    
    # Layout
    palette_area_width: int = 300
    sidebar_width: int = 200
    top_bar_height: int = 80
    
    # Grid
    default_grid_rows: int = 20
    default_grid_cols: int = 20
    max_grid_rows: int = 100
    max_grid_cols: int = 100
    
    # Camera
    camera_speed: int = 10
    
    # UI Elements
    button_width: int = 160
    button_height: int = 40
    button_margin: int = 10
    tab_width: int = 120
    tab_height: int = 30
    
    # File Paths
    default_tileset_folder: str = "assets/tilesets/scifi"
    default_output_path: str = "map1.json"
```

**How to Customize**:
- Change screen dimensions: `screen_width`, `screen_height`
- Adjust tile sizes: `tile_size`, `palette_tile_size`
- Modify layout: `palette_area_width`, `sidebar_width`
- Set grid limits: `max_grid_rows`, `max_grid_cols`
- Adjust camera speed: `camera_speed`
- Change default paths: `default_tileset_folder`, `default_output_path`

##### 2. `EditorColors` - Visual Theme

All RGB color tuples used in the editor:

```python
@dataclass(frozen=True)
class EditorColors:
    # Backgrounds
    background: tuple[int, int, int] = (50, 50, 50)
    palette_area: tuple[int, int, int] = (70, 70, 70)
    sidebar: tuple[int, int, int] = (60, 60, 60)
    top_bar: tuple[int, int, int] = (40, 40, 40)
    grid_area: tuple[int, int, int] = (45, 45, 45)
    
    # Grid
    grid_line: tuple[int, int, int] = (80, 80, 80)
    grid_highlight: tuple[int, int, int] = (255, 255, 0)
    
    # Buttons
    button_normal: tuple[int, int, int] = (100, 100, 100)
    button_hover: tuple[int, int, int] = (120, 120, 120)
    button_active: tuple[int, int, int] = (80, 80, 80)
    
    # Tabs
    tab_inactive: tuple[int, int, int] = (80, 80, 80)
    tab_active: tuple[int, int, int] = (120, 120, 180)
    tab_hover: tuple[int, int, int] = (100, 100, 100)
    
    # Text
    text_normal: tuple[int, int, int] = (255, 255, 255)
    text_dim: tuple[int, int, int] = (200, 200, 200)
    text_success: tuple[int, int, int] = (100, 255, 100)
    text_error: tuple[int, int, int] = (255, 100, 100)
    
    # Selection
    palette_selection: tuple[int, int, int] = (255, 255, 0)
    tileset_origin: tuple[int, int, int] = (255, 0, 255)
```

**How to Customize**:
- Create themes: Modify color values for dark/light themes
- Adjust contrast: Change background and UI element colors
- Customize highlights: Modify selection and grid colors
- Brand colors: Update button and tab colors

##### 3. `EditorText` - UI Strings

All user-facing text and messages:

```python
@dataclass(frozen=True)
class EditorText:
    # Buttons
    button_new: str = "New Map"
    button_save: str = "Save"
    button_load: str = "Load"
    button_apply_size: str = "Apply Size"
    
    # Headers
    header_tilesets: str = "Tilesets"
    header_tools: str = "Tools"
    header_map_size: str = "Map Size"
    
    # Messages
    msg_save_success: str = "Map saved successfully!"
    msg_save_error: str = "Error saving map!"
    msg_load_success: str = "Map loaded successfully!"
    msg_load_error: str = "Error loading map!"
    msg_no_tilesets: str = "No tilesets loaded"
    
    # Format Strings
    fmt_camera_pos: str = "Camera: {}, {}"
    fmt_grid_cell: str = "Cell: {}, {}"
    fmt_tileset_info: str = "Tileset: {}"
    fmt_grid_size: str = "Grid: {}x{}"
```

**How to Customize**:
- Localization: Translate all strings to different languages
- Branding: Update labels to match your project
- Messages: Customize success/error feedback
- Info display: Modify format strings for status info

### `editor_components/__init__.py` - Package Exports

**Purpose**: Makes config dataclasses easily importable

```python
from .configs import EditorConfig, EditorColors, EditorText

__all__ = ['EditorConfig', 'EditorColors', 'EditorText']
```

**Usage**:
```python
from map_editor.editor_components import EditorConfig, EditorColors, EditorText
```

### `map_editor/__init__.py` - Main Package Export

**Purpose**: Exposes TileEditor at package level

```python
from .tile_editor import TileEditor

__all__ = ['TileEditor']
```

## Configuration Usage Pattern

### Singleton Instances

Three singleton instances are created in `configs.py`:

```python
config = EditorConfig()
colors = EditorColors()
text = EditorText()
```

### Importing and Using

```python
from .editor_components.configs import config, colors, text

# Use in code
screen = pygame.display.set_mode((config.screen_width, config.screen_height))
pygame.draw.rect(surface, colors.background, rect)
button_label = text.button_save
```

### Benefits

1. **Maintainability**: All settings in one place
2. **Readability**: `config.tile_size` vs magic number `16`
3. **Type Safety**: IDE autocomplete and type checking
4. **Immutability**: Can't accidentally modify configs
5. **Scalability**: Easy to add new settings

## Customization Guide

### Creating a Custom Configuration

To create custom configurations without modifying source:

```python
from map_editor.editor_components.configs import EditorConfig, EditorColors
from map_editor import TileEditor

# Create custom config (dataclasses are immutable, so create new instances)
custom_config = EditorConfig(
    screen_width=1920,
    screen_height=1080,
    tile_size=32,
    default_tileset_folder="my_tiles"
)

# Manually pass configs to editor (requires modification)
# Or use monkey patching (not recommended for production):
import map_editor.editor_components.configs as cfg
cfg.config = custom_config
```

### Future Enhancement: Config File Loading

Potential implementation for loading from JSON:

```python
import json
from dataclasses import replace

def load_config(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return replace(EditorConfig(), **data)
```

## Design Principles

### 1. Separation of Concerns
- **Editor logic** (`tile_editor.py`): UI, input, rendering, file I/O
- **Configuration** (`configs.py`): All customizable values
- **Documentation** (README.md, this file): User guide and architecture

### 2. Immutability
- Frozen dataclasses prevent accidental modification
- Configurations are read-only at runtime
- Changes require creating new instances

### 3. Type Safety
- All attributes have type hints
- IDE support for autocomplete and validation
- Catches errors at development time

### 4. Single Responsibility
- Each dataclass handles one aspect: technical, visual, or textual
- Easy to find and modify specific settings
- Clear organization

## Integration with Your Game

### Loading Maps in Game Code

```python
import json
import pygame

def load_map(map_path, tilesets_folder):
    with open(map_path) as f:
        data = json.load(f)
    
    # Load tilesets
    tilesets = []
    for tileset_name in data['tilesets']:
        tileset = pygame.image.load(f"{tilesets_folder}/{tileset_name}")
        tilesets.append(tileset)
    
    # Parse grid
    grid = data['tilegrid']  # 3D array: [row][col] = [tileset_idx, tile_idx]
    
    return grid, tilesets, data['tileset_folder']
```

### Rendering a Map

```python
def render_map(surface, grid, tilesets, tile_size=16):
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            tileset_idx, tile_idx = cell
            if tileset_idx >= 0 and tile_idx >= 0:
                tileset = tilesets[tileset_idx]
                # Calculate tile position in tileset
                tiles_per_row = tileset.get_width() // tile_size
                tile_x = (tile_idx % tiles_per_row) * tile_size
                tile_y = (tile_idx // tiles_per_row) * tile_size
                
                # Blit to screen
                dest_x = col_idx * tile_size
                dest_y = row_idx * tile_size
                surface.blit(tileset, (dest_x, dest_y), 
                           (tile_x, tile_y, tile_size, tile_size))
```

## Testing & Validation

After any configuration changes, verify:
- ✅ Editor launches without errors
- ✅ UI elements render at correct positions
- ✅ Grid dimensions match settings
- ✅ Colors display correctly
- ✅ Text appears in all areas
- ✅ Save/load preserves data

## Conclusion

The map editor is built with modularity, configurability, and maintainability in mind. The frozen dataclass approach provides a clean, type-safe way to manage all settings while keeping the codebase organized and scalable.

For feature documentation and usage instructions, see [README.md](README.md).
