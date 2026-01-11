"""
Tileset Manager Module

Handles loading, parsing, and managing multiple tilesets for the tile editor.
"""

import os
import pygame
from .configs import EditorConfig, EditorText


class TilesetManager:
    """Manages tileset loading and access"""
    
    def __init__(self, tile_size):
        """
        Initialize the tileset manager
        
        Args:
            tile_size: Size of each tile in pixels (e.g., 16x16)
        """
        self.tile_size = tile_size
        self.tilesets = []
        self.tileset_folder = None
    
    def load_tilesets_recursive(self, root_folder):
        """
        Load all PNG tilesets from folder and subfolders recursively
        
        Args:
            root_folder: Path to the root folder containing tileset images
        """
        try:
            self.tileset_folder = root_folder
            self.tilesets = []
            
            if not os.path.exists(root_folder):
                if EditorConfig.DEBUG_VERBOSE:
                    print(f"Tileset folder not found: {root_folder}")
                self.add_empty_tileset()
                return
            
            # Find all PNG files recursively
            png_files = []
            for dirpath, dirnames, filenames in os.walk(root_folder):
                for filename in filenames:
                    if filename.lower().endswith('.png'):
                        full_path = os.path.join(dirpath, filename)
                        # Get relative path from root folder for better naming
                        rel_path = os.path.relpath(full_path, root_folder)
                        png_files.append((full_path, rel_path))
            
            png_files.sort(key=lambda x: x[1])  # Sort by relative path
            
            if not png_files:
                if EditorConfig.DEBUG_VERBOSE:
                    print(EditorText.MSG_NO_PNG_FILES.format(root_folder))
                self.add_empty_tileset()
                return
            
            # Load each tileset
            for full_path, rel_path in png_files:
                try:
                    tileset_image = pygame.image.load(full_path)
                    tiles, tiles_per_row, tiles_per_col = self.extract_tiles_from_image(tileset_image)
                    
                    # Use relative path without extension as name
                    name = os.path.splitext(rel_path)[0].replace(os.sep, '/')
                    
                    tileset = {
                        'name': name,
                        'path': full_path,
                        'image': tileset_image,
                        'tiles': tiles,
                        'tiles_per_row': tiles_per_row,
                        'tiles_per_col': tiles_per_col,
                        'total_tiles': len(tiles)
                    }
                    self.tilesets.append(tileset)
                    if EditorConfig.DEBUG_VERBOSE:
                        print(EditorText.MSG_TILESET_LOADED.format(name, len(tiles)))
                except Exception as e:
                    if EditorConfig.DEBUG_VERBOSE:
                        print(EditorText.MSG_ERROR_LOADING_TILESET.format(rel_path, e))
            
            if EditorConfig.DEBUG_VERBOSE:
                print(EditorText.MSG_TOTAL_TILESETS.format(len(self.tilesets)))
        except Exception as e:
            if EditorConfig.DEBUG_VERBOSE:
                print(EditorText.MSG_ERROR_LOADING_FOLDER.format(e))
            self.add_empty_tileset()
    
    def extract_tiles_from_image(self, tileset_image):
        """
        Extract individual tiles from a tileset image
        
        Args:
            tileset_image: Pygame surface containing the tileset
            
        Returns:
            Tuple of (tiles_list, tiles_per_row, tiles_per_col)
        """
        tiles = []
        width = tileset_image.get_width()
        height = tileset_image.get_height()
        tiles_per_row = width // self.tile_size
        tiles_per_col = height // self.tile_size
        
        for row in range(tiles_per_col):
            for col in range(tiles_per_row):
                x = col * self.tile_size
                y = row * self.tile_size
                tile_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                tile_surf.blit(tileset_image, (0, 0), (x, y, self.tile_size, self.tile_size))
                tiles.append(tile_surf)
        return tiles, tiles_per_row, tiles_per_col
    
    def add_empty_tileset(self):
        """Add an empty placeholder tileset"""
        empty_tileset = {
            'name': EditorText.EMPTY_TILESET_NAME,
            'path': None,
            'image': None,
            'tiles': [],
            'tiles_per_row': 0,
            'tiles_per_col': 0,
            'total_tiles': 0
        }
        self.tilesets.append(empty_tileset)
    
    def get_tileset(self, index):
        """
        Get a tileset by index
        
        Args:
            index: Index of the tileset
            
        Returns:
            Tileset dictionary or None if index is invalid
        """
        if 0 <= index < len(self.tilesets):
            return self.tilesets[index]
        return None
    
    def get_tileset_count(self):
        """Get the total number of loaded tilesets"""
        return len(self.tilesets)
