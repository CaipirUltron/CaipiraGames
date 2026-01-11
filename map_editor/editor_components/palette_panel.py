"""
Palette Panel Module

Handles the right side palette panel with tileset tabs and tile selection.
"""

import pygame
from .configs import EditorConfig, EditorColors, EditorText


class PalettePanel:
    """Manages the right palette panel for tile selection"""
    
    def __init__(self, screen, screen_width, screen_height):
        """
        Initialize the palette panel
        
        Args:
            screen: Pygame screen surface
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.palette_width = EditorConfig.PALETTE_WIDTH
        self.palette_x = screen_width - self.palette_width
        self.palette_tile_size = EditorConfig.PALETTE_TILE_SIZE
        self.palette_cols = self.palette_width // self.palette_tile_size
        self.tab_height = EditorConfig.TAB_HEIGHT
        self.palette_start_y = self.tab_height
        self.palette_rows_visible = (screen_height - self.tab_height) // self.palette_tile_size
        
        # Scroll state
        self.palette_scroll = 0
        
        # Tab rectangles for click detection
        self.tab_rects = []
        
        # Colors
        self.palette_bg = EditorColors.PALETTE_BG
        self.button_color = EditorColors.BUTTON_COLOR
        self.button_hover_color = EditorColors.BUTTON_HOVER_COLOR
        self.selection_color = EditorColors.SELECTION_COLOR
        self.text_color = EditorColors.TEXT_COLOR
        
        # Fonts
        self.small_font = pygame.font.Font(None, EditorConfig.FONT_SIZE_SMALL)
    
    def update_screen_size(self, screen_width, screen_height):
        """Update palette dimensions when screen is resized"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.palette_x = screen_width - self.palette_width
        self.palette_rows_visible = (screen_height - self.tab_height) // self.palette_tile_size
    
    def draw(self, tilesets, current_tileset_index, selected_tile):
        """
        Draw the palette panel with tabs and tiles
        
        Args:
            tilesets: List of tileset dictionaries
            current_tileset_index: Index of currently selected tileset
            selected_tile: Index of currently selected tile
        """
        # Draw palette background
        pygame.draw.rect(self.screen, self.palette_bg, 
                        (self.palette_x, 0, self.palette_width, self.screen_height))
        
        # Draw tabs
        self._draw_tileset_tabs(tilesets, current_tileset_index)
        
        # Get current tileset
        current_tileset = None
        if 0 <= current_tileset_index < len(tilesets):
            current_tileset = tilesets[current_tileset_index]
        
        if not current_tileset or current_tileset['total_tiles'] == 0:
            self.screen.set_clip(None)
            return
        
        # Clip drawing to palette area (below tabs)
        clip_rect = pygame.Rect(self.palette_x, self.palette_start_y, 
                                self.palette_width, self.screen_height - self.palette_start_y)
        self.screen.set_clip(clip_rect)
        
        # Draw tiles from current tileset
        tiles = current_tileset['tiles']
        for i, tile in enumerate(tiles):
            col = i % self.palette_cols
            row = i // self.palette_cols
            
            x = self.palette_x + col * self.palette_tile_size
            y = self.palette_start_y + row * self.palette_tile_size - (self.palette_scroll * self.palette_tile_size)
            
            # Only draw if visible
            if self.palette_start_y - self.palette_tile_size < y < self.screen_height:
                scaled_tile = pygame.transform.scale(tile, (self.palette_tile_size, self.palette_tile_size))
                self.screen.blit(scaled_tile, (x, y))
                
                # Draw selection highlight
                if i == selected_tile:
                    pygame.draw.rect(self.screen, self.selection_color, 
                                   (x, y, self.palette_tile_size, self.palette_tile_size), 3)
        
        self.screen.set_clip(None)
        
        # Draw scrollbar indicator if needed
        self._draw_scrollbar(current_tileset['total_tiles'])
    
    def _draw_tileset_tabs(self, tilesets, current_tileset_index):
        """Draw tabs for switching between tilesets"""
        self.tab_rects = []
        
        if not tilesets:
            return
        
        # Calculate tab width
        tab_width = self.palette_width // len(tilesets) if len(tilesets) > 0 else self.palette_width
        tab_width = max(EditorConfig.TAB_MIN_WIDTH, min(tab_width, EditorConfig.TAB_MAX_WIDTH))
        
        for i, tileset in enumerate(tilesets):
            x = self.palette_x + i * tab_width
            
            # Tab background
            tab_color = self.button_hover_color if i == current_tileset_index else self.button_color
            tab_rect = pygame.Rect(x, 0, tab_width, self.tab_height)
            self.tab_rects.append(tab_rect)
            pygame.draw.rect(self.screen, tab_color, tab_rect)
            pygame.draw.rect(self.screen, EditorColors.TAB_BORDER_COLOR, tab_rect, 1)
            
            # Tab label (truncated name)
            name = tileset['name']
            if len(name) > EditorConfig.TAB_NAME_MAX_LENGTH:
                name = name[:EditorConfig.TAB_NAME_MAX_LENGTH-1] + EditorText.TAB_ELLIPSIS
            text = self.small_font.render(name, True, self.text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            self.screen.blit(text, text_rect)
    
    def _draw_scrollbar(self, total_tiles):
        """Draw scrollbar indicator if palette is scrollable"""
        total_rows = (total_tiles + self.palette_cols - 1) // self.palette_cols
        if total_rows > self.palette_rows_visible:
            scrollbar_height = max(EditorConfig.SCROLLBAR_MIN_HEIGHT, 
                                  int((self.screen_height - self.tab_height) * self.palette_rows_visible / total_rows))
            scrollbar_y = self.tab_height + int(self.palette_scroll * ((self.screen_height - self.tab_height) - scrollbar_height) / 
                            (total_rows - self.palette_rows_visible))
            pygame.draw.rect(self.screen, self.selection_color,
                           (self.palette_x - EditorConfig.SCROLLBAR_OFFSET, scrollbar_y, 
                            EditorConfig.SCROLLBAR_WIDTH, scrollbar_height))
    
    def handle_scroll(self, delta, total_tiles):
        """
        Handle vertical scrolling
        
        Args:
            delta: Scroll delta (positive = scroll down, negative = scroll up)
            total_tiles: Total number of tiles in current tileset
        """
        total_rows = (total_tiles + self.palette_cols - 1) // self.palette_cols
        max_scroll = max(0, total_rows - self.palette_rows_visible + 1)
        self.palette_scroll = max(0, min(max_scroll, self.palette_scroll - delta))
    
    def handle_tab_click(self, mouse_x, mouse_y):
        """
        Check if a tab was clicked
        
        Args:
            mouse_x: X position of mouse
            mouse_y: Y position of mouse
            
        Returns:
            Tileset index if tab clicked, None otherwise
        """
        if mouse_y >= self.tab_height:
            return None
        
        mouse_pos = (mouse_x, mouse_y)
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None
    
    def handle_palette_click(self, mouse_x, mouse_y, total_tiles):
        """
        Check if a tile in the palette was clicked
        
        Args:
            mouse_x: X position of mouse
            mouse_y: Y position of mouse
            total_tiles: Total tiles in current tileset
            
        Returns:
            Tile index if valid tile clicked, None otherwise
        """
        if mouse_y < self.palette_start_y:
            return None
        
        local_x = mouse_x - self.palette_x
        local_y = mouse_y - self.palette_start_y + (self.palette_scroll * self.palette_tile_size)
        
        col = local_x // self.palette_tile_size
        row = local_y // self.palette_tile_size
        
        tile_index = row * self.palette_cols + col
        if 0 <= tile_index < total_tiles:
            return tile_index
        return None
    
    def reset_scroll(self):
        """Reset scroll position to top"""
        self.palette_scroll = 0
