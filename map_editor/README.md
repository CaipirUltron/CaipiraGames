# Tile Editor for CaipiraGames

A simple, intuitive tile editor for creating levels using multiple tilesets.

## Features

- **Multi-Tileset Support**: Load multiple tilesets from a folder and mix tiles from different sets
- **Tileset Tabs**: Easy switching between tilesets with tab interface
- **UI Control Panel** (left side): Instructions, tileset loader, and editable grid size controls
- **Tile Palette** (right side): All available tiles from the active tileset, scrollable
- **Grid-based Map** (center): Paintable grid for level design with camera scrolling
- **Dynamic Grid Size**: Change map dimensions on-the-fly (1-200 width/height)
- **Mouse Controls**: Easy painting and erasing with mouse
- **Camera/Scrolling**: Navigate large maps and tile palettes
- **Save/Load**: JSON format preserves multi-tileset information
- **Visual Feedback**: Selected tile is highlighted with yellow border

## Layout

```
┌──────────────┬─────────────────────────────┬──────────────┐
│              │                             │ [Tab1][Tab2] │
│  UI PANEL    │      MAP GRID (Center)      │──────────────│
│  (Left)      │      - Scrollable           │              │
│              │      - Arrow Keys           │    TILE      │
│  Load Folder │      - Paint/Erase          │  PALETTE     │
│  Grid Size:  │      - Multi-Tileset        │  (Right)     │
│  - Width     │                             │              │
│  - Height    │                             │  Scrollable  │
│  Map Info    │                             │  with Mouse  │
│              │                             │  Wheel       │
└──────────────┴─────────────────────────────┴──────────────┘
```

## Multi-Tileset Workflow

### 1. Loading Tilesets
The editor now supports loading multiple PNG tilesets from a single folder:

1. Click **"Load Folder..."** button in the left UI panel
2. Select a folder containing your PNG tileset files
3. All PNG files in that folder are automatically loaded
4. Each tileset appears as a tab at the top of the palette area

**Example folder structure:**
```
assets/tilesets/scifi/
  ├── level_tileset.png      (walls, floors, decorations)
  ├── platform_moving.png    (special objects)
  └── enemies.png            (enemy sprites)
```

### 2. Working with Multiple Tilesets
- **Switch Tilesets**: Click the tabs at the top of the palette (right side)
- **Active Tileset**: The selected tab is highlighted
- **Mix Tiles**: Paint tiles from different tilesets on the same map
- **Tile Memory**: Each tile remembers which tileset it came from

### 3. Painting with Multi-Tileset
1. Select a tileset by clicking its tab
2. Click a tile from the palette below
3. Paint on the map
4. Switch to another tileset and repeat
5. Tiles from all tilesets coexist on the same map

## How to Use

### Running the Editor
```bash
python3 tile_editor_launcher.py
```

### Initial Setup
On first run, the editor attempts to load tilesets from the default folder. To use your own tilesets:
1. Click **"Load Folder..."** in the left panel
2. Navigate to your tileset folder
3. Select the folder (not individual files)
4. All PNG files in that folder will be loaded as separate tilesets

### Controls

**Mouse:**
- **Click Tileset Tab** (top of palette): Switch between loaded tilesets
- **Left Click** on palette: Select a tile from the active tileset
- **Left Click** on map: Paint the selected tile (remembers source tileset)
- **Right Click** on map: Erase a tile
- **Click and Drag**: Continuous painting/erasing
- **Scroll Wheel** over palette: Scroll through available tiles in active tileset
- **Scroll Wheel** over map: Scroll map vertically
- **Horizontal Trackpad Gesture**: Scroll map horizontally

**Keyboard:**
- **Arrow Keys** (←↑↓→): Pan the map camera
- **Ctrl+S**: Save map to `map_editor.json`
- **Ctrl+L**: Load map from `map_editor.json`
- **Ctrl+N**: Clear the entire map
- **ESC**: Exit the editor

**UI Panel Buttons (Left Side):**
- **Load Folder...**: Open folder browser to load tilesets
- **Width -/+**: Decrease/increase map width
- **Height -/+**: Decrease/increase map height
- **Click Width/Height Value**: Type exact dimensions and press Enter

**Grid Size Editing:**
1. Click **-** or **+** buttons to adjust incrementally, OR
2. Click on the width/height value display
3. Type the new size (1-200)
4. Press **Enter** to apply or **ESC** to cancel

### Workflow
1. Launch the editor with `python3 tile_editor_launcher.py`
2. Click **"Load Folder..."** and select a folder with PNG tileset files
3. Multiple tileset tabs appear at the top of the palette (right side)
4. Click a tab to select which tileset to use
5. Click on a tile in the palette to select it (yellow border appears)
6. (Optional) Adjust grid size using +/- buttons on the left
7. Click on the center grid to place tiles from the selected tileset
8. Switch to another tileset tab and continue painting
9. Use arrow keys or mouse scroll to navigate large maps
10. Right-click to erase tiles
11. Use **Ctrl+S** to save your multi-tileset map
12. Use **Ctrl+L** to load a previously saved map (auto-loads all tilesets)

## File Format

The editor saves maps in JSON format with multi-tileset support:

```json
{
    "tile_width": 16,
    "tile_height": 16,
    "map_tile_size": 32,
    "width": 100,
    "height": 50,
    "tileset_folder": "assets/tilesets/scifi",
    "tilesets": [
        {
            "name": "level_tileset",
            "path": "assets/tilesets/scifi/level_tileset.png",
            "tiles_per_row": 18,
            "tiles_per_col": 18,
            "total_tiles": 324
        },
        {
            "name": "platform_moving",
            "path": "assets/tilesets/scifi/platform_moving.png",
            "tiles_per_row": 30,
            "tiles_per_col": 65,
            "total_tiles": 1950
        }
    ],
    "tilegrid": [
        [
            [0, 15],    // [tileset_index, tile_index]
            [1, 42],    // tile from second tileset
            [-1, -1],   // empty tile
            ...
        ],
        ...
    ]
}
```

**Key Points:**
- `tileset_folder`: Path to folder containing all tilesets
- `tilesets`: Array of tileset metadata (name, path, dimensions)
- `tilegrid`: 3D array where each element is `[tileset_index, tile_index]`
  - `tileset_index`: Which tileset the tile comes from (0-based)
  - `tile_index`: Which tile from that tileset (0-based, row-major order)
  - `[-1, -1]`: Empty/transparent tile
  
**Backwards Compatibility:**
- Old maps with single tileset format are automatically converted
- Single tileset maps have all tiles assigned to `tileset_index = 0`

## Customization

You can modify these parameters in [tile_editor.py](classes/scenes/game/tile_editor.py):

- `map_cols`, `map_rows`: Initial map dimensions (default: 100x50, adjustable 1-200 in UI)
- `map_tile_size`: Display size of tiles in the map (default: 32x32 pixels)
- `palette_tile_size`: Display size in palette (default: 32x32 pixels)
- `tile_size`: Original tile size in tilesets (default: 16x16 pixels)
- `ui_panel_width`: Width of the left control panel (default: 220 pixels)
- `palette_width`: Width of the right tile palette (default: 200 pixels)
- `tab_height`: Height of tileset tabs (default: 30 pixels)

## Multi-Tileset Technical Details

### Data Structure
Each tile in the map stores two pieces of information:
- **Tileset Index**: Which tileset the tile came from (index in `tilesets` array)
- **Tile Index**: Which tile within that tileset (row-major order, 0-based)

### Tileset Storage
Internally, each tileset is stored as:
```python
{
    'name': str,           # Filename without .png extension
    'path': str,           # Full path to PNG file
    'image': Surface,      # Pygame surface of tileset image
    'tiles': [Surface],    # List of extracted 16x16 tile surfaces
    'tiles_per_row': int,  # Number of tiles per row in tileset
    'tiles_per_col': int,  # Number of tiles per column
    'total_tiles': int     # Total number of tiles in tileset
}
```

### Grid Size Changes
- When resizing the grid, existing tile data is preserved
- New grid areas are initialized as empty `[-1, -1]`
- Camera position is automatically clamped to new bounds

## Scrolling Features

### Map Scrolling
- Automatic scrolling support when grid dimensions exceed screen space
- **Arrow Keys**: Navigate horizontally (←→) and vertically (↑↓)
- **Mouse Wheel**: Scroll vertically when hovering over map
- **Trackpad Horizontal Gesture**: Scroll horizontally when hovering over map
- Camera position automatically clamped to map bounds

### Palette Scrolling
- Scrolls when active tileset has more tiles than fit on screen
- **Mouse Wheel**: Scroll vertically while hovering over palette
- **Yellow Scrollbar**: Visual indicator on left edge showing scroll position
- Each tileset maintains independent scroll position

### Tileset Tab Navigation
- Click tabs to instantly switch between loaded tilesets
- Active tab is highlighted
- Tab names are truncated if too long (shows "name..." format)
- Up to 6 tabs fit comfortably (more tabs will be narrower)

## Integration with Game

To use multi-tileset maps created with this editor in your game:

1. **Load the JSON file** and parse the tileset information
2. **Load each tileset image** from the paths specified in the `tilesets` array
3. **Iterate through `tilegrid`**:
   - For each `[tileset_idx, tile_idx]` pair:
     - If `tileset_idx >= 0`, get the tileset from `tilesets[tileset_idx]`
     - Extract the tile at position `tile_idx` from that tileset
     - Render at the appropriate position
   - If `[-1, -1]`, skip (transparent/empty)

**Example pseudocode:**
```python
# Load map
with open('map_editor.json') as f:
    map_data = json.load(f)

# Load all tilesets
tilesets = []
for ts_info in map_data['tilesets']:
    tileset_image = load_image(ts_info['path'])
    tiles = extract_tiles(tileset_image, tile_size=16)
    tilesets.append(tiles)

# Render map
for row in range(map_data['height']):
    for col in range(map_data['width']):
        tileset_idx, tile_idx = map_data['tilegrid'][row][col]
        if tileset_idx >= 0 and tile_idx >= 0:
            tile = tilesets[tileset_idx][tile_idx]
            render_tile(tile, x=col*32, y=row*32)
```

## Tips and Best Practices

- **Organize Tilesets**: Keep related tilesets in the same folder (e.g., `level1_tilesets/`, `environment_tiles/`)
- **Descriptive Names**: Use clear PNG filenames - they become tab labels
- **Consistent Tile Size**: All tilesets should use the same tile size (default: 16x16 pixels)
- **Folder Persistence**: Keep tileset folders in the same location for loading saved maps
- **Large Maps**: Use Ctrl+S frequently when working on large maps (100x50 or bigger)
- **Testing**: Save and test-load your map to ensure all tilesets reload correctly

## Troubleshooting

**Q: Tabs aren't appearing**
- Ensure you selected a folder (not individual files)
- Check that the folder contains PNG files
- PNG files must be valid images with dimensions divisible by 16

**Q: Map looks different after loading**
- Ensure tileset folder location hasn't changed
- Check that all tileset PNG files still exist at their saved paths
- Verify tileset PNGs haven't been modified

**Q: Can't scroll the map**
- Map must be larger than the visible area to scroll
- Try increasing grid size with +/- buttons
- Use arrow keys if mouse wheel isn't working

**Q: Tiles from old map are wrong after loading new tilesets**
- This is expected - tile indices map to different tiles in different tilesets
- Always use **Ctrl+N** (Clear) when switching tileset folders

**Q: Editor is slow with many tilesets**
- Consider splitting tilesets into multiple folders by theme/level
- Each folder should contain related tilesets only (3-5 files recommended)
