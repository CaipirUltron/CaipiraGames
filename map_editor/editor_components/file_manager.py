"""
File Manager Module

Handles all file I/O operations including saving/loading maps, autosave, and config management.
"""

import os
import json
import threading
import time
import numpy as np
import pygame
from .configs import EditorConfig, EditorText


class FileManager:
    """Manages file operations for maps and configurations"""
    
    def __init__(self, tileset_manager, get_map_state_callback, set_map_state_callback):
        """
        Initialize the file manager
        
        Args:
            tileset_manager: TilesetManager instance
            get_map_state_callback: Function that returns (map_grid, map_rows, map_cols, tile_size, map_tile_size, map_name)
            set_map_state_callback: Function that sets (map_grid, map_rows, map_cols, map_name, is_dirty)
        """
        self.tileset_manager = tileset_manager
        self.get_map_state = get_map_state_callback
        self.set_map_state = set_map_state_callback
        self.maps_folder = "map_editor/maps"
        self.is_dirty = False
        self.running = False
        self.autosave_thread = None
        
        # Create maps folder if it doesn't exist
        os.makedirs(self.maps_folder, exist_ok=True)
    
    def start_autosave(self):
        """Start the autosave background thread"""
        self.running = True
        self.autosave_thread = threading.Thread(target=self._autosave_worker, daemon=True)
        self.autosave_thread.start()
    
    def stop_autosave(self):
        """Stop the autosave background thread"""
        self.running = False
        if self.autosave_thread and self.autosave_thread.is_alive():
            self.autosave_thread.join(timeout=1.0)
    
    def _autosave_worker(self):
        """Background thread for auto-saving periodically if changes exist"""
        while self.running:
            time.sleep(EditorConfig.AUTOSAVE_INTERVAL)
            if self.is_dirty and self.running:
                self.save_map_silent()
                if EditorConfig.DEBUG_VERBOSE:
                    print(f"Auto-saved")
    
    def save_map_silent(self):
        """Save map without printing messages (for autosave)"""
        try:
            map_grid, map_rows, map_cols, tile_size, map_tile_size, map_name = self.get_map_state()
            filepath = os.path.join(self.maps_folder, f"{map_name}.json")
            self._save_map_internal(filepath, map_grid, map_rows, map_cols, tile_size, map_tile_size)
            self.is_dirty = False
        except Exception as e:
            if EditorConfig.DEBUG_VERBOSE:
                print(f"Auto-save error: {e}")
    
    def save_map(self, map_name):
        """
        Save the map to a JSON file
        
        Args:
            map_name: Name of the map (without extension)
        """
        map_grid, map_rows, map_cols, tile_size, map_tile_size, _ = self.get_map_state()
        filepath = os.path.join(self.maps_folder, f"{map_name}.json")
        self._save_map_internal(filepath, map_grid, map_rows, map_cols, tile_size, map_tile_size)
        self.is_dirty = False
        if EditorConfig.DEBUG_VERBOSE:
            print(f"Map saved: {map_name}.json")
    
    def _save_map_internal(self, filepath, map_grid, map_rows, map_cols, tile_size, map_tile_size):
        """Internal method to save map data to file"""
        # Collect information about all tilesets
        tilesets_info = []
        for tileset in self.tileset_manager.tilesets:
            tilesets_info.append({
                'name': tileset['name'],
                'path': tileset['path'],
                'tiles_per_row': tileset['tiles_per_row'],
                'tiles_per_col': tileset['tiles_per_col'],
                'total_tiles': tileset['total_tiles']
            })
        
        map_data = {
            "tile_width": tile_size,
            "tile_height": tile_size,
            "map_tile_size": map_tile_size,
            "width": map_cols,
            "height": map_rows,
            "tilegrid": map_grid.tolist(),
            "tileset_folder": self.tileset_manager.tileset_folder,
            "tilesets": tilesets_info
        }
        
        with open(filepath, 'w') as f:
            json.dump(map_data, f, indent=4)
    
    def load_map(self, map_name):
        """
        Load a map from a JSON file
        
        Args:
            map_name: Name of the map (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        filepath = os.path.join(self.maps_folder, f"{map_name}.json")
        if not os.path.exists(filepath):
            if EditorConfig.DEBUG_VERBOSE:
                print(EditorText.MSG_FILE_NOT_FOUND.format(filepath))
            return False
        
        try:
            with open(filepath, 'r') as f:
                map_data = json.load(f)
                
                # Load tileset folder if specified
                if "tileset_folder" in map_data and map_data["tileset_folder"]:
                    self.tileset_manager.load_tilesets_recursive(map_data["tileset_folder"])
                elif "tilesets" in map_data:
                    # Alternative: load individual tilesets from paths
                    self.tileset_manager.tilesets = []
                    for ts_info in map_data["tilesets"]:
                        if ts_info['path'] and os.path.exists(ts_info['path']):
                            try:
                                tileset_image = pygame.image.load(ts_info['path'])
                                tiles, tiles_per_row, tiles_per_col = self.tileset_manager.extract_tiles_from_image(tileset_image)
                                tileset = {
                                    'name': ts_info['name'],
                                    'path': ts_info['path'],
                                    'image': tileset_image,
                                    'tiles': tiles,
                                    'tiles_per_row': tiles_per_row,
                                    'tiles_per_col': tiles_per_col,
                                    'total_tiles': len(tiles)
                                }
                                self.tileset_manager.tilesets.append(tileset)
                            except Exception as e:
                                if EditorConfig.DEBUG_VERBOSE:
                                    print(EditorText.MSG_ERROR_LOADING_TILESET.format(ts_info['name'], e))
                
                # Validate tilesets match the map file
                if "tilesets" in map_data:
                    saved_tilesets = map_data["tilesets"]
                    
                    # Check if tileset count matches
                    if len(self.tileset_manager.tilesets) != len(saved_tilesets):
                        if EditorConfig.DEBUG_VERBOSE:
                            print(f"WARNING: Tileset count mismatch!")
                            print(f"  Map expects {len(saved_tilesets)} tilesets, but {len(self.tileset_manager.tilesets)} are loaded.")
                            print(f"  Map may not render correctly!")
                    
                    # Check if tileset names and order match
                    mismatches = []
                    for i, saved_ts in enumerate(saved_tilesets):
                        if i < len(self.tileset_manager.tilesets):
                            if self.tileset_manager.tilesets[i]['name'] != saved_ts['name']:
                                mismatches.append(f"  Index {i}: Expected '{saved_ts['name']}', got '{self.tileset_manager.tilesets[i]['name']}'")
                        else:
                            mismatches.append(f"  Index {i}: Expected '{saved_ts['name']}', but no tileset loaded")
                    
                    if mismatches:
                        if EditorConfig.DEBUG_VERBOSE:
                            print("ERROR: Tileset mismatch detected!")
                            print("The map uses different tilesets than currently loaded:")
                            for msg in mismatches:
                                print(msg)
                            print("The map will render incorrectly. Please ensure the same tilesets are loaded.")
                        return False  # Abort loading
                
                # Load map grid
                loaded_grid = np.array(map_data["tilegrid"], dtype=int)
                
                # Handle both old format (2D) and new format (3D)
                if len(loaded_grid.shape) == 2:
                    # Old format: convert to new format
                    map_rows, map_cols = loaded_grid.shape
                    map_grid = np.full((map_rows, map_cols, 2), -1, dtype=int)
                    # Assume all tiles came from tileset 0
                    for row in range(map_rows):
                        for col in range(map_cols):
                            if loaded_grid[row, col] >= 0:
                                map_grid[row, col, 0] = 0
                                map_grid[row, col, 1] = loaded_grid[row, col]
                else:
                    # New format
                    map_grid = loaded_grid
                    map_rows, map_cols = loaded_grid.shape[0], loaded_grid.shape[1]
                
                # Update map state
                self.set_map_state(map_grid, map_rows, map_cols, map_name, False)
                if EditorConfig.DEBUG_VERBOSE:
                    print(EditorText.MSG_MAP_LOADED)
                return True
        except Exception as e:
            if EditorConfig.DEBUG_VERBOSE:
                print(EditorText.MSG_ERROR_LOADING_MAP.format(e))
            return False
    
    def get_available_maps(self):
        """Get list of available map files"""
        if not os.path.exists(self.maps_folder):
            return []
        maps = [f[:-5] for f in os.listdir(self.maps_folder) if f.endswith('.json')]
        maps.sort()
        return maps
    
    def clear_map(self, map_rows, map_cols):
        """
        Clear the entire map
        
        Args:
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
            
        Returns:
            New empty map grid
        """
        return np.full((map_rows, map_cols, 2), -1, dtype=int)
    
    def save_config(self, map_name):
        """Save editor configuration (last opened map)"""
        try:
            config_data = {
                'last_map': map_name
            }
            with open(EditorConfig.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            if EditorConfig.DEBUG_VERBOSE:
                print(f"Error saving config: {e}")
    
    def load_config(self):
        """
        Load editor configuration and return last opened map name
        
        Returns:
            Last opened map name or None
        """
        try:
            if os.path.exists(EditorConfig.CONFIG_FILE):
                with open(EditorConfig.CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get('last_map')
        except Exception as e:
            if EditorConfig.DEBUG_VERBOSE:
                print(f"Error loading config: {e}")
        return None
