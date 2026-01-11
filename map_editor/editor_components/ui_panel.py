"""
UI Panel Module

Handles the left side UI panel with controls, grid size editing, and map file management.
"""

import pygame
import numpy as np
from .configs import EditorConfig, EditorColors, EditorText


class UIPanel:
    """Manages the left UI panel with controls and information"""
    
    def __init__(self, screen, screen_width, screen_height):
        """
        Initialize the UI panel
        
        Args:
            screen: Pygame screen surface
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_panel_width = EditorConfig.UI_PANEL_WIDTH
        self.ui_panel_x = EditorConfig.UI_PANEL_X
        
        # Colors
        self.ui_panel_bg = EditorColors.UI_PANEL_BG
        self.button_color = EditorColors.BUTTON_COLOR
        self.button_hover_color = EditorColors.BUTTON_HOVER_COLOR
        self.text_color = EditorColors.TEXT_COLOR
        self.selection_color = EditorColors.SELECTION_COLOR
        
        # Fonts
        self.font = pygame.font.Font(None, EditorConfig.FONT_SIZE_NORMAL)
        self.title_font = pygame.font.Font(None, EditorConfig.FONT_SIZE_TITLE)
        self.small_font = pygame.font.Font(None, EditorConfig.FONT_SIZE_SMALL)
        
        # Button rectangles
        self.width_minus_rect = None
        self.width_value_rect = None
        self.width_plus_rect = None
        self.height_minus_rect = None
        self.height_value_rect = None
        self.height_plus_rect = None
        self.map_name_rect = None
        self.load_map_button_rect = None
        self.map_list_rects = []
        self.autotile_toggle_rect = None
    
    def update_screen_size(self, screen_width, screen_height):
        """Update panel dimensions when screen is resized"""
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def draw(self, map_name, editing_map_name, input_text, editing_cols, editing_rows, 
             map_cols, map_rows, map_grid, tilesets, current_tileset, get_available_maps_callback, 
             autotile_enabled=False):
        """
        Draw the UI panel
        
        Args:
            map_name: Current map name
            editing_map_name: Whether currently editing map name
            input_text: Current input text
            editing_cols: Whether editing column count
            editing_rows: Whether editing row count
            map_cols: Number of map columns
            map_rows: Number of map rows
            map_grid: The map grid array
            tilesets: List of tilesets
            current_tileset: Currently selected tileset
            get_available_maps_callback: Function to get list of available maps
            autotile_enabled: Whether auto-tiling is enabled
        """
        # Draw panel background
        pygame.draw.rect(self.screen, self.ui_panel_bg,
                        (0, 0, self.ui_panel_width, self.screen_height))
        
        y_offset = 10
        
        # Title
        title = self.title_font.render("TILE EDITOR", True, self.text_color)
        self.screen.blit(title, (10, y_offset))
        y_offset += 35
        
        # Instructions
        for text in EditorText.INSTRUCTIONS:
            if text.startswith("==="):
                text_surf = self.font.render(text, True, EditorColors.TEXT_HIGHLIGHT_COLOR)
            else:
                text_surf = self.font.render(text, True, self.text_color)
            self.screen.blit(text_surf, (10, y_offset))
            y_offset += 22
        
        y_offset += 10
        
        # Map file controls
        y_offset = self._draw_map_controls(y_offset, map_name, editing_map_name, input_text, get_available_maps_callback)
        y_offset += 10
        
        # Grid size controls
        y_offset = self._draw_grid_controls(y_offset, editing_cols, editing_rows, input_text, map_cols, map_rows)
        y_offset += 40
        
        # Auto-tile toggle
        y_offset = self._draw_autotile_toggle(y_offset, autotile_enabled)
        y_offset += 40
        
        # Map info
        self._draw_map_info(y_offset, map_grid, tilesets, current_tileset)
    
    def _draw_map_controls(self, y_offset, map_name, editing_map_name, input_text, get_available_maps_callback):
        """Draw map file management controls"""
        # Map file title
        map_title = self.font.render("=== MAP FILE ===", True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(map_title, (10, y_offset))
        y_offset += 25
        
        # Map name label
        name_label = self.font.render("Name:", True, self.text_color)
        self.screen.blit(name_label, (10, y_offset))
        y_offset += 20
        
        # Map name input
        self.map_name_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_LARGE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = self.button_hover_color if editing_map_name else self.button_color
        pygame.draw.rect(self.screen, button_color, self.map_name_rect)
        pygame.draw.rect(self.screen, self.text_color, self.map_name_rect, 2)
        
        if editing_map_name:
            name_text = self.font.render(input_text + "_", True, self.selection_color)
        else:
            name_text = self.font.render(map_name, True, self.text_color)
        text_rect = name_text.get_rect(center=self.map_name_rect.center)
        self.screen.blit(name_text, text_rect)
        
        y_offset += 40
        
        # Load map button
        self.load_map_button_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_LARGE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, self.load_map_button_rect)
        pygame.draw.rect(self.screen, self.text_color, self.load_map_button_rect, 2)
        load_text = self.font.render("Load Map...", True, self.text_color)
        text_rect = load_text.get_rect(center=self.load_map_button_rect.center)
        self.screen.blit(load_text, text_rect)
        
        y_offset += 35
        
        # Draw map list dropdown if opened
        if len(self.map_list_rects) > 0:
            available_maps = get_available_maps_callback()
            self.map_list_rects = []  # Rebuild list
            for i, map_name_item in enumerate(available_maps[:5]):  # Show max 5 maps
                rect = pygame.Rect(10, y_offset + i * 25, EditorConfig.BUTTON_LARGE_WIDTH, 25)
                self.map_list_rects.append(rect)
                pygame.draw.rect(self.screen, self.button_color, rect)
                pygame.draw.rect(self.screen, self.text_color, rect, 1)
                map_text = self.small_font.render(map_name_item, True, self.text_color)
                self.screen.blit(map_text, (rect.x + 5, rect.y + 5))
            y_offset += len(available_maps[:5]) * 25
        
        return y_offset
    
    def _draw_grid_controls(self, y_offset, editing_cols, editing_rows, input_text, map_cols, map_rows):
        """Draw grid size controls"""
        # Grid size title
        grid_title = self.font.render(EditorText.HEADER_GRID_SIZE, True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(grid_title, (10, y_offset))
        y_offset += 25
        
        # Width control
        width_label = self.font.render(EditorText.LABEL_WIDTH, True, self.text_color)
        self.screen.blit(width_label, (10, y_offset))
        y_offset += 20
        
        # Width controls: [-] [value] [+]
        y_offset = self._draw_dimension_control(y_offset, editing_cols, input_text, map_cols, is_width=True)
        y_offset += 40
        
        # Height control
        height_label = self.font.render(EditorText.LABEL_HEIGHT, True, self.text_color)
        self.screen.blit(height_label, (10, y_offset))
        y_offset += 20
        
        # Height controls: [-] [value] [+]
        y_offset = self._draw_dimension_control(y_offset, editing_rows, input_text, map_rows, is_width=False)
        
        return y_offset
    
    def _draw_dimension_control(self, y_offset, is_editing, input_text, value, is_width):
        """Draw a dimension control (width or height)"""
        # Minus button
        minus_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, minus_rect)
        pygame.draw.rect(self.screen, self.text_color, minus_rect, 2)
        minus_text = self.title_font.render(EditorText.BUTTON_MINUS, True, self.text_color)
        minus_text_rect = minus_text.get_rect(center=minus_rect.center)
        self.screen.blit(minus_text, minus_text_rect)
        
        # Value display/input
        value_rect = pygame.Rect(45, y_offset, EditorConfig.BUTTON_VALUE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = self.button_hover_color if is_editing else self.button_color
        pygame.draw.rect(self.screen, button_color, value_rect)
        pygame.draw.rect(self.screen, self.text_color, value_rect, 2)
        
        if is_editing:
            display_text = self.font.render(input_text + "_", True, self.selection_color)
        else:
            display_text = self.font.render(str(value), True, self.text_color)
        text_rect = display_text.get_rect(center=value_rect.center)
        self.screen.blit(display_text, text_rect)
        
        # Plus button
        plus_rect = pygame.Rect(180, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, plus_rect)
        pygame.draw.rect(self.screen, self.text_color, plus_rect, 2)
        plus_text = self.title_font.render(EditorText.BUTTON_PLUS, True, self.text_color)
        plus_text_rect = plus_text.get_rect(center=plus_rect.center)
        self.screen.blit(plus_text, plus_text_rect)
        
        # Store rectangles for click detection
        if is_width:
            self.width_minus_rect = minus_rect
            self.width_value_rect = value_rect
            self.width_plus_rect = plus_rect
        else:
            self.height_minus_rect = minus_rect
            self.height_value_rect = value_rect
            self.height_plus_rect = plus_rect
        
        return y_offset
    
    def _draw_autotile_toggle(self, y_offset, autotile_enabled):
        """Draw auto-tile toggle button"""
        # Auto-tile title
        autotile_title = self.font.render("=== AUTO-TILE ===", True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(autotile_title, (10, y_offset))
        y_offset += 25
        
        # Toggle button
        self.autotile_toggle_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_LARGE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = EditorColors.BUTTON_HOVER_COLOR if autotile_enabled else self.button_color
        pygame.draw.rect(self.screen, button_color, self.autotile_toggle_rect)
        pygame.draw.rect(self.screen, self.text_color, self.autotile_toggle_rect, 2)
        
        toggle_text = f"{'ON' if autotile_enabled else 'OFF'} (T)"
        text_surf = self.font.render(toggle_text, True, EditorColors.TEXT_HIGHLIGHT_COLOR if autotile_enabled else self.text_color)
        text_rect = text_surf.get_rect(center=self.autotile_toggle_rect.center)
        self.screen.blit(text_surf, text_rect)
        
        y_offset += 35
        
        return y_offset
    
    def _draw_map_info(self, y_offset, map_grid, tilesets, current_tileset):
        """Draw map information"""
        # Map info title
        info_title = self.font.render(EditorText.HEADER_MAP_INFO, True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(info_title, (10, y_offset))
        y_offset += 25
        
        # Count tiles
        total_tiles_placed = np.sum(map_grid[:, :, 0] >= 0)
        
        current_tileset_info = EditorText.INFO_TILESET_LOADED.format(len(tilesets))
        if current_tileset:
            current_tileset_info = EditorText.INFO_TILESET_DETAILS.format(current_tileset['name'], current_tileset['total_tiles'])
        
        info_texts = [
            EditorText.INFO_TOTAL.format(total_tiles_placed),
            EditorText.INFO_TILESET.format(current_tileset_info)
        ]
        
        for text in info_texts:
            text_surf = self.font.render(text, True, EditorColors.TEXT_DIM_COLOR)
            self.screen.blit(text_surf, (10, y_offset))
            y_offset += 22
    
    def handle_click(self, mouse_x, mouse_y):
        """
        Handle clicks in the UI panel
        
        Args:
            mouse_x: X position of mouse
            mouse_y: Y position of mouse
            
        Returns:
            Tuple of (action, data) where action is one of:
            - 'map_name': User clicked map name input
            - 'load_button': User clicked load button
            - 'load_map': data contains selected map name
            - 'width_minus': Decrease width
            - 'width_plus': Increase width
            - 'width_value': Click to edit width
            - 'height_minus': Decrease height
            - 'height_plus': Increase height
            - 'height_value': Click to edit height
            - None: Click didn't hit any button
        """
        mouse_pos = (mouse_x, mouse_y)
        
        # Map name input
        if self.map_name_rect and self.map_name_rect.collidepoint(mouse_pos):
            return ('map_name', None)
        # Auto-tile toggle
        elif self.autotile_toggle_rect and self.autotile_toggle_rect.collidepoint(mouse_pos):
            return ('autotile_toggle', None)
        
        
        # Load map button
        if self.load_map_button_rect and self.load_map_button_rect.collidepoint(mouse_pos):
            return ('load_button', None)
        
        # Check map list items
        for i, rect in enumerate(self.map_list_rects):
            if rect and rect.collidepoint(mouse_pos):
                return ('load_map', i)
        
        # Width controls
        if self.width_minus_rect and self.width_minus_rect.collidepoint(mouse_pos):
            return ('width_minus', None)
        elif self.width_plus_rect and self.width_plus_rect.collidepoint(mouse_pos):
            return ('width_plus', None)
        elif self.width_value_rect and self.width_value_rect.collidepoint(mouse_pos):
            return ('width_value', None)
        
        # Height controls
        elif self.height_minus_rect and self.height_minus_rect.collidepoint(mouse_pos):
            return ('height_minus', None)
        elif self.height_plus_rect and self.height_plus_rect.collidepoint(mouse_pos):
            return ('height_plus', None)
        elif self.height_value_rect and self.height_value_rect.collidepoint(mouse_pos):
            return ('height_value', None)
        
        return (None, None)
