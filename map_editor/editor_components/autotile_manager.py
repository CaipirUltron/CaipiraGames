"""
AutoTile Manager Module

Handles automatic tile selection based on neighboring tiles using bitmask patterns.
Supports 4-bit (cardinal directions) and 8-bit (including diagonals) auto-tiling.
"""

import numpy as np
from typing import List, Tuple, Optional


class AutoTileManager:
    """Manages auto-tiling logic using bitmask patterns"""
    
    # Bitmask values for 4-bit (cardinal) auto-tiling
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    
    # Additional bitmask values for 8-bit (with diagonals)
    NORTHWEST = 16
    NORTHEAST = 32
    SOUTHWEST = 64
    SOUTHEAST = 128
    
    def __init__(self, use_8bit: bool = False):
        """
        Initialize the auto-tile manager
        
        Args:
            use_8bit: True for 256-tile sets, False for 16-tile sets
        """
        self.use_8bit = use_8bit
        
        # Auto-tile sets: maps base_tileset_idx -> base_tile_idx for auto-tile groups
        # Example: {0: [0, 16, 32]} means tileset 0 has auto-tile sets starting at tiles 0, 16, 32
        self.autotile_sets = {}
    
    def register_autotile_set(self, tileset_idx: int, base_tile_idx: int):
        """
        Register a base tile as the start of an auto-tile set
        
        Args:
            tileset_idx: Index of the tileset containing the auto-tile set
            base_tile_idx: Starting index of the 16-tile (or 256-tile) auto-tile group
        """
        if tileset_idx not in self.autotile_sets:
            self.autotile_sets[tileset_idx] = []
        if base_tile_idx not in self.autotile_sets[tileset_idx]:
            self.autotile_sets[tileset_idx].append(base_tile_idx)
            self.autotile_sets[tileset_idx].sort()
    
    def unregister_autotile_set(self, tileset_idx: int, base_tile_idx: int):
        """Remove an auto-tile set registration"""
        if tileset_idx in self.autotile_sets and base_tile_idx in self.autotile_sets[tileset_idx]:
            self.autotile_sets[tileset_idx].remove(base_tile_idx)
    
    def is_autotile(self, tileset_idx: int, tile_idx: int) -> bool:
        """Check if a tile belongs to an auto-tile set"""
        if tileset_idx not in self.autotile_sets:
            return False
        
        for base_idx in self.autotile_sets[tileset_idx]:
            set_size = 256 if self.use_8bit else 16
            if base_idx <= tile_idx < base_idx + set_size:
                return True
        return False
    
    def get_base_tile(self, tileset_idx: int, tile_idx: int) -> Optional[int]:
        """Get the base tile index for an auto-tile"""
        if tileset_idx not in self.autotile_sets:
            return None
        
        for base_idx in self.autotile_sets[tileset_idx]:
            set_size = 256 if self.use_8bit else 16
            if base_idx <= tile_idx < base_idx + set_size:
                return base_idx
        return None
    
    def calculate_bitmask(self, map_grid: np.ndarray, row: int, col: int,
                          tileset_idx: int, base_tile_idx: int) -> int:
        """
        Calculate the bitmask for a tile based on its neighbors
        
        Args:
            map_grid: The map grid array (rows, cols, 2)
            row: Row position of the tile
            col: Column position of the tile
            tileset_idx: Tileset index to check for matching tiles
            base_tile_idx: Base tile index of the auto-tile set
            
        Returns:
            Bitmask value (0-15 for 4-bit, 0-255 for 8-bit)
        """
        rows, cols = map_grid.shape[0], map_grid.shape[1]
        mask = 0
        set_size = 256 if self.use_8bit else 16
        
        # Helper to check if a position has a matching auto-tile
        def has_matching_tile(r, c):
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return False
            tile_ts = map_grid[r, c, 0]
            tile_idx = map_grid[r, c, 1]
            # Check if it's from the same tileset and auto-tile set
            if tile_ts == tileset_idx and base_tile_idx <= tile_idx < base_tile_idx + set_size:
                return True
            return False
        
        # Cardinal directions (always calculated)
        if has_matching_tile(row - 1, col):  # North
            mask |= self.NORTH
        if has_matching_tile(row, col + 1):  # East
            mask |= self.EAST
        if has_matching_tile(row + 1, col):  # South
            mask |= self.SOUTH
        if has_matching_tile(row, col - 1):  # West
            mask |= self.WEST
        
        # Diagonal directions (only for 8-bit mode)
        if self.use_8bit:
            if has_matching_tile(row - 1, col - 1):  # Northwest
                mask |= self.NORTHWEST
            if has_matching_tile(row - 1, col + 1):  # Northeast
                mask |= self.NORTHEAST
            if has_matching_tile(row + 1, col - 1):  # Southwest
                mask |= self.SOUTHWEST
            if has_matching_tile(row + 1, col + 1):  # Southeast
                mask |= self.SOUTHEAST
        
        return mask
    
    def apply_autotile(self, map_grid: np.ndarray, row: int, col: int,
                       tileset_idx: int, tile_idx: int) -> List[Tuple[int, int, int, int]]:
        """
        Apply auto-tiling to a position and return all tiles that need updating
        
        Args:
            map_grid: The map grid array (rows, cols, 2)
            row: Row position where tile was placed
            col: Column position where tile was placed
            tileset_idx: Tileset index of the placed tile
            tile_idx: Tile index of the placed tile
            
        Returns:
            List of (row, col, tileset_idx, tile_idx) tuples to update
        """
        # Get the base tile for this auto-tile set
        base_tile = self.get_base_tile(tileset_idx, tile_idx)
        if base_tile is None:
            return []
        
        updates = []
        
        # Update the placed tile
        mask = self.calculate_bitmask(map_grid, row, col, tileset_idx, base_tile)
        updates.append((row, col, tileset_idx, base_tile + mask))
        
        # Update all neighbors (they may need different variants now)
        neighbors = [
            (row - 1, col),      # North
            (row, col + 1),      # East
            (row + 1, col),      # South
            (row, col - 1),      # West
        ]
        
        if self.use_8bit:
            neighbors.extend([
                (row - 1, col - 1),  # Northwest
                (row - 1, col + 1),  # Northeast
                (row + 1, col - 1),  # Southwest
                (row + 1, col + 1),  # Southeast
            ])
        
        rows, cols = map_grid.shape[0], map_grid.shape[1]
        for n_row, n_col in neighbors:
            if 0 <= n_row < rows and 0 <= n_col < cols:
                n_tileset = map_grid[n_row, n_col, 0]
                n_tile = map_grid[n_row, n_col, 1]
                
                # Only update if neighbor is part of the same auto-tile set
                if n_tileset == tileset_idx and self.is_autotile(n_tileset, n_tile):
                    n_base = self.get_base_tile(n_tileset, n_tile)
                    if n_base == base_tile:  # Same auto-tile set
                        n_mask = self.calculate_bitmask(map_grid, n_row, n_col, tileset_idx, base_tile)
                        updates.append((n_row, n_col, tileset_idx, base_tile + n_mask))
        
        return updates
    
    def handle_erase_autotile(self, map_grid: np.ndarray, row: int, col: int) -> List[Tuple[int, int, int, int]]:
        """
        Handle auto-tile updates when a tile is erased
        
        Args:
            map_grid: The map grid array (rows, cols, 2)
            row: Row position where tile was erased
            col: Column position where tile was erased
            
        Returns:
            List of (row, col, tileset_idx, tile_idx) tuples for neighbors that need updating
        """
        updates = []
        
        # Check all neighbors and update them if they're auto-tiles
        neighbors = [
            (row - 1, col),      # North
            (row, col + 1),      # East
            (row + 1, col),      # South
            (row, col - 1),      # West
        ]
        
        if self.use_8bit:
            neighbors.extend([
                (row - 1, col - 1),  # Northwest
                (row - 1, col + 1),  # Northeast
                (row + 1, col - 1),  # Southwest
                (row + 1, col + 1),  # Southeast
            ])
        
        rows, cols = map_grid.shape[0], map_grid.shape[1]
        for n_row, n_col in neighbors:
            if 0 <= n_row < rows and 0 <= n_col < cols:
                n_tileset = map_grid[n_row, n_col, 0]
                n_tile = map_grid[n_row, n_col, 1]
                
                if n_tileset >= 0 and self.is_autotile(n_tileset, n_tile):
                    base_tile = self.get_base_tile(n_tileset, n_tile)
                    if base_tile is not None:
                        mask = self.calculate_bitmask(map_grid, n_row, n_col, n_tileset, base_tile)
                        updates.append((n_row, n_col, n_tileset, base_tile + mask))
        
        return updates
