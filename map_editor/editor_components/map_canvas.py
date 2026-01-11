"""
Map Canvas Module

Handles the central map area including rendering, camera, and tile painting/erasing.
"""

import pygame
from .configs import EditorConfig, EditorColors


class MapCanvas:
    """Manages the central map drawing area"""
    
    def __init__(self, screen, screen_width, screen_height, ui_panel_width, palette_width):
        """
        Initialize the map canvas
        
        Args:
            screen: Pygame screen surface
            screen_width: Width of the screen
            screen_height: Height of the screen
            ui_panel_width: Width of left UI panel
            palette_width: Width of right palette panel
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_panel_width = ui_panel_width
        self.palette_width = palette_width
        
        # Map area configuration
        self.map_start_x = self.ui_panel_width + EditorConfig.MAP_SPACING
        self.map_width = screen_width - palette_width - self.map_start_x - EditorConfig.MAP_SPACING
        self.map_height = screen_height
        self.map_tile_size = EditorConfig.MAP_TILE_SIZE
        
        # Camera position
        self.camera_x = 0
        self.camera_y = 0
        
        # Colors
        self.bg_color = EditorColors.BG_COLOR
        self.grid_color = EditorColors.GRID_COLOR
    
    def update_screen_size(self, screen_width, screen_height, palette_x):
        """Update canvas dimensions when screen is resized"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = palette_x - self.map_start_x - EditorConfig.MAP_SPACING
        self.map_height = screen_height
    
    def draw_grid(self, map_rows, map_cols):
        """
        Draw the grid lines on the map
        
        Args:
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
        """
        # Clip drawing to map area
        clip_rect = pygame.Rect(self.map_start_x, 0, self.map_width, self.map_height)
        self.screen.set_clip(clip_rect)
        
        # Vertical lines
        for col in range(map_cols + 1):
            x = self.map_start_x + col * self.map_tile_size - self.camera_x
            if self.map_start_x - self.map_tile_size < x < self.map_start_x + self.map_width:
                pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.map_height), 1)
        
        # Horizontal lines
        for row in range(map_rows + 1):
            y = row * self.map_tile_size - self.camera_y
            if -self.map_tile_size < y < self.map_height:
                pygame.draw.line(self.screen, self.grid_color, (self.map_start_x, y), 
                               (self.map_start_x + self.map_width, y), 1)
        
        self.screen.set_clip(None)
    
    def draw_map(self, map_grid, map_rows, map_cols, tilesets):
        """
        Draw the map with placed tiles
        
        Args:
            map_grid: 3D numpy array containing tile data
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
            tilesets: List of tileset dictionaries
        """
        # Clip drawing to map area
        clip_rect = pygame.Rect(self.map_start_x, 0, self.map_width, self.map_height)
        self.screen.set_clip(clip_rect)
        
        for row in range(map_rows):
            for col in range(map_cols):
                tileset_idx = map_grid[row, col, 0]
                tile_idx = map_grid[row, col, 1]
                
                if tileset_idx >= 0 and tile_idx >= 0:
                    # Get the correct tileset
                    if tileset_idx < len(tilesets):
                        tileset = tilesets[tileset_idx]
                        if tile_idx < len(tileset['tiles']):
                            x = self.map_start_x + col * self.map_tile_size - self.camera_x
                            y = row * self.map_tile_size - self.camera_y
                            
                            # Only draw if visible
                            if (self.map_start_x - self.map_tile_size < x < self.map_start_x + self.map_width and 
                                -self.map_tile_size < y < self.map_height):
                                tile = tileset['tiles'][tile_idx]
                                scaled_tile = pygame.transform.scale(tile, 
                                                                     (self.map_tile_size, self.map_tile_size))
                                self.screen.blit(scaled_tile, (x, y))
        
        self.screen.set_clip(None)
    
    def handle_paint(self, mouse_x, mouse_y, map_rows, map_cols, current_tileset_index, selected_tile):
        """
        Handle painting a tile on the map
        
        Args:
            mouse_x: X position of mouse
            mouse_y: Y position of mouse
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
            current_tileset_index: Index of currently selected tileset
            selected_tile: Index of currently selected tile
            
        Returns:
            Tuple of (row, col) if valid position, None otherwise
        """
        if mouse_x < self.map_start_x:
            return None
        
        local_x = mouse_x - self.map_start_x
        col = (local_x + self.camera_x) // self.map_tile_size
        row = (mouse_y + self.camera_y) // self.map_tile_size
        
        if 0 <= row < map_rows and 0 <= col < map_cols:
            return (row, col, current_tileset_index, selected_tile)
        return None
    
    def handle_erase(self, mouse_x, mouse_y, map_rows, map_cols):
        """
        Handle erasing a tile from the map
        
        Args:
            mouse_x: X position of mouse
            mouse_y: Y position of mouse
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
            
        Returns:
            Tuple of (row, col) if valid position, None otherwise
        """
        if mouse_x < self.map_start_x:
            return None
        
        local_x = mouse_x - self.map_start_x
        col = (local_x + self.camera_x) // self.map_tile_size
        row = (mouse_y + self.camera_y) // self.map_tile_size
        
        if 0 <= row < map_rows and 0 <= col < map_cols:
            return (row, col)
        return None
    
    def move_camera(self, dx, dy, map_rows, map_cols):
        """
        Move the camera by a delta
        
        Args:
            dx: Delta x (horizontal movement)
            dy: Delta y (vertical movement)
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
        """
        # Horizontal movement
        if dx != 0:
            max_camera_x = max(0, map_cols * self.map_tile_size - self.map_width)
            self.camera_x = max(0, min(max_camera_x, self.camera_x + dx))
        
        # Vertical movement
        if dy != 0:
            max_camera_y = max(0, map_rows * self.map_tile_size - self.map_height)
            self.camera_y = max(0, min(max_camera_y, self.camera_y + dy))
    
    def scroll_map(self, delta_x, delta_y, map_rows, map_cols):
        """
        Scroll the map (used for wheel scrolling)
        
        Args:
            delta_x: Horizontal scroll delta
            delta_y: Vertical scroll delta
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
        """
        scroll_x = self.map_tile_size * delta_x
        scroll_y = self.map_tile_size * delta_y
        self.move_camera(scroll_x, scroll_y, map_rows, map_cols)
    
    def is_in_map_area(self, mouse_x, palette_x):
        """
        Check if mouse is in map area
        
        Args:
            mouse_x: X position of mouse
            palette_x: X position of palette panel
            
        Returns:
            True if mouse is in map area
        """
        return self.map_start_x <= mouse_x < palette_x
