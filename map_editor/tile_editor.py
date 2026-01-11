"""
Tile Editor - Main Module

A multi-tileset tile map editor with intuitive UI for game development.
Refactored for better maintainability and scalability.
"""

import sys
import pygame
from pygame.locals import *
import numpy as np

from .editor_components.configs import EditorConfig, EditorColors, EditorText
from .editor_components.tileset_manager import TilesetManager
from .editor_components.file_manager import FileManager
from .editor_components.ui_panel import UIPanel
from .editor_components.palette_panel import PalettePanel
from .editor_components.map_canvas import MapCanvas
from .editor_components.event_handler import EventHandler
from .editor_components.autotile_manager import AutoTileManager


class TileEditor:
    """
    Main tile map editor class - orchestrates all components
    """
    
    def __init__(self, screen_width=EditorConfig.SCREEN_WIDTH, screen_height=EditorConfig.SCREEN_HEIGHT):
        """Initialize the tile editor and all its components"""
        pygame.init()
        pygame.display.set_caption(EditorText.WINDOW_TITLE)
        
        # Screen setup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.fps = EditorConfig.FPS
        
        # Core data
        self.tile_size = EditorConfig.TILE_SIZE
        self.map_tile_size = EditorConfig.MAP_TILE_SIZE
        self.map_cols = EditorConfig.DEFAULT_MAP_COLS
        self.map_rows = EditorConfig.DEFAULT_MAP_ROWS
        self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
        self.map_name = "map"
        
        # Editor state
        self.current_tileset_index = 0
        self.selected_tile = 0
        self.is_painting = False
        self.is_erasing = False
        self.editing_cols = False
        self.editing_rows = False
        self.editing_map_name = False
        self.input_text = ""
        self.autotile_enabled = EditorConfig.AUTO_TILE_ENABLED
        
        # Initialize components
        self.tileset_manager = TilesetManager(self.tile_size)
        self.tileset_manager.load_tilesets_recursive('assets/tilesets')
        
        self.file_manager = FileManager(
            self.tileset_manager,
            self._get_map_state,
            self._set_map_state
        )
        
        self.ui_panel = UIPanel(self.screen, screen_width, screen_height)
        self.palette_panel = PalettePanel(self.screen, screen_width, screen_height)
        self.map_canvas = MapCanvas(
            self.screen, screen_width, screen_height,
            EditorConfig.UI_PANEL_WIDTH, EditorConfig.PALETTE_WIDTH
        )
        self.event_handler = EventHandler()
        self.autotile_manager = AutoTileManager(
            use_8bit=EditorConfig.AUTO_TILE_8BIT_MODE
        )
        
        
        # Colors
        self.bg_color = EditorColors.BG_COLOR
        
        # Start autosave and load last session
        self.file_manager.start_autosave()
        last_map = self.file_manager.load_config()
        if last_map:
            map_path = f"{self.file_manager.maps_folder}/{last_map}.json"
            import os
            if os.path.exists(map_path):
                self.file_manager.load_map(last_map)
                if EditorConfig.DEBUG_VERBOSE:
                    print(f"Restored last session: {last_map}.json")
    
    def _get_map_state(self):
        """Callback for file manager to get current map state"""
        return (
            self.map_grid,
            self.map_rows,
            self.map_cols,
            self.tile_size,
            self.map_tile_size,
            self.map_name
        )
    
    def _set_map_state(self, map_grid, map_rows, map_cols, map_name, is_dirty):
        """Callback for file manager to set map state"""
        self.map_grid = map_grid
        self.map_rows = map_rows
        self.map_cols = map_cols
        self.map_name = map_name
        self.file_manager.is_dirty = is_dirty
    
    def handle_events(self):
        """Process all user input events"""
        # Handle keyboard shortcuts (only when not editing text)
        if not self.editing_cols and not self.editing_rows and not self.editing_map_name:
            action = self.event_handler.handle_keyboard_shortcuts()
            if action == 'quit':
                return False
            elif action == 'save':
                self.file_manager.save_map(self.map_name)
            elif action == 'clear':
                self.map_grid = self.file_manager.clear_map(self.map_rows, self.map_cols)
                self.file_manager.is_dirty = True
                if EditorConfig.DEBUG_VERBOSE:
                    print(EditorText.MSG_MAP_CLEARED)
            elif action == 'toggle_autotile':
                self.autotile_enabled = not self.autotile_enabled
                if EditorConfig.DEBUG_VERBOSE:
                    print(f"Auto-tile mode: {'ON' if self.autotile_enabled else 'OFF'}")
            
            # Handle camera movement
            dx, dy = self.event_handler.handle_camera_keys(
                self.map_rows, self.map_cols,
                self.map_tile_size, self.map_canvas.map_width, self.map_canvas.map_height
            )
            if dx != 0 or dy != 0:
                self.map_canvas.move_camera(dx, dy, self.map_rows, self.map_cols)
        
        # Process pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                if not self._handle_keydown(event):
                    return False
            
            elif event.type == MOUSEBUTTONDOWN:
                self._handle_mousedown(event)
            
            elif event.type == MOUSEBUTTONUP:
                self._handle_mouseup(event)
            
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            
            elif event.type == MOUSEWHEEL:
                self._handle_scroll(event)
            
            elif event.type == MOUSEMOTION:
                self._handle_mousemotion(event)
        
        return True
    
    def _handle_keydown(self, event):
        """Handle keyboard input"""
        # Grid size editing
        if self.editing_cols or self.editing_rows:
            new_text, action = self.event_handler.process_text_input(event, self.input_text)
            self.input_text = new_text
            if action == 'submit':
                self._apply_grid_size()
            elif action == 'cancel':
                self.editing_cols = False
                self.editing_rows = False
                self.input_text = ""
        
        # Map name editing
        elif self.editing_map_name:
            new_text, action = self.event_handler.process_text_input(event, self.input_text, allow_special_chars=False)
            self.input_text = new_text
            if action == 'submit':
                if self.input_text.strip():
                    old_name = self.map_name
                    self.map_name = self.input_text.strip()
                    if old_name != self.map_name:
                        self.file_manager.is_dirty = True
                self.editing_map_name = False
                self.input_text = ""
            elif action == 'cancel':
                self.editing_map_name = False
                self.input_text = ""
        
        return True
    
    def _handle_mousedown(self, event):
        """Handle mouse button down events"""
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            # Check if shift is held AND mouse is in palette to register autotile
            mods = pygame.key.get_mods()
            if mods & KMOD_SHIFT and mouse_x >= self.palette_panel.palette_x:
                self._register_autotile(mouse_x, mouse_y)
            else:
                self.is_painting = True
                self._handle_click(event.pos)
        elif event.button == 3:  # Right click
            self.is_erasing = True
            self._handle_erase(event.pos)
    
    def _handle_mouseup(self, event):
        """Handle mouse button up events"""
        if event.button == 1:
            self.is_painting = False
        elif event.button == 3:
            self.is_erasing = False
    
    def _handle_resize(self, event):
        """Handle window resize"""
        self.screen_width = event.w
        self.screen_height = event.h
        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        self.ui_panel.update_screen_size(event.w, event.h)
        self.palette_panel.update_screen_size(event.w, event.h)
        self.map_canvas.update_screen_size(event.w, event.h, self.palette_panel.palette_x)
    
    def _handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        
        # Vertical scroll
        if event.y != 0:
            # Check if mouse is over palette
            if mouse_x >= self.palette_panel.palette_x:
                current_tileset = self.tileset_manager.get_tileset(self.current_tileset_index)
                if current_tileset and current_tileset['total_tiles'] > 0:
                    self.palette_panel.handle_scroll(event.y, current_tileset['total_tiles'])
            # Check if mouse is over map
            elif self.map_canvas.is_in_map_area(mouse_x, self.palette_panel.palette_x):
                self.map_canvas.scroll_map(0, -event.y, self.map_rows, self.map_cols)
        
        # Horizontal scroll (only for map)
        if event.x != 0 and self.map_canvas.is_in_map_area(mouse_x, self.palette_panel.palette_x):
            self.map_canvas.scroll_map(event.x, 0, self.map_rows, self.map_cols)
    
    def _handle_mousemotion(self, event):
        """Handle mouse motion for painting/erasing"""
        if self.is_painting:
            self._handle_click(event.pos)
        if self.is_erasing:
            self._handle_erase(event.pos)
    
    def _handle_click(self, pos):
        """Handle mouse click for UI, palette, or map"""
        mouse_x, mouse_y = pos
        
        # Check UI panel
        if mouse_x < self.ui_panel.ui_panel_width:
            self._handle_ui_click(mouse_x, mouse_y)
        # Check palette
        elif mouse_x >= self.palette_panel.palette_x:
            self._handle_palette_click(mouse_x, mouse_y)
        # Check map area
        elif mouse_x >= self.map_canvas.map_start_x:
            self._handle_map_click(mouse_x, mouse_y)
    
    def _handle_ui_click(self, mouse_x, mouse_y):
        """Handle clicks in UI panel"""
        action, data = self.ui_panel.handle_click(mouse_x, mouse_y)
        
        if action == 'map_name':
            self.editing_map_name = True
            self.editing_cols = False
            self.editing_rows = False
            self.input_text = self.map_name
        elif action == 'load_button':
            # Toggle dropdown
            if len(self.ui_panel.map_list_rects) > 0:
                self.ui_panel.map_list_rects = []
            else:
                available_maps = self.file_manager.get_available_maps()
                self.ui_panel.map_list_rects = [None] * min(len(available_maps), 5)
        elif action == 'load_map':
            available_maps = self.file_manager.get_available_maps()
            if data < len(available_maps):
                self.file_manager.load_map(available_maps[data])
                self.ui_panel.map_list_rects = []
        elif action == 'width_minus':
            self._change_grid_width(-1)
        elif action == 'width_plus':
            self._change_grid_width(1)
        elif action == 'width_value':
            self.editing_cols = True
            self.editing_rows = False
            self.editing_map_name = False
            self.input_text = str(self.map_cols)
        elif action == 'height_minus':
            self._change_grid_height(-1)
        elif action == 'height_plus':
            self._change_grid_height(1)
        elif action == 'height_value':
            self.editing_rows = True
            self.editing_cols = False
            self.editing_map_name = False
            self.input_text = str(self.map_rows)
        elif action == 'autotile_toggle':
            self.autotile_enabled = not self.autotile_enabled
            if EditorConfig.DEBUG_VERBOSE:
                print(f"Auto-tile mode: {'ON' if self.autotile_enabled else 'OFF'}")
    
    def _handle_palette_click(self, mouse_x, mouse_y):
        """Handle clicks in palette panel"""
        # Check tab click
        tab_index = self.palette_panel.handle_tab_click(mouse_x, mouse_y)
        if tab_index is not None:
            self.current_tileset_index = tab_index
            self.selected_tile = 0
            self.palette_panel.reset_scroll()
            return
        
        # Check tile click
        current_tileset = self.tileset_manager.get_tileset(self.current_tileset_index)
        if current_tileset and current_tileset['total_tiles'] > 0:
            tile_index = self.palette_panel.handle_palette_click(
                mouse_x, mouse_y, current_tileset['total_tiles']
            )
            if tile_index is not None:
                self.selected_tile = tile_index
                
    def _register_autotile(self, mouse_x, mouse_y):
        """Register the clicked tile as a base for an auto-tile set"""
        current_tileset = self.tileset_manager.get_tileset(self.current_tileset_index)
        if current_tileset and current_tileset['total_tiles'] > 0:
            tile_index = self.palette_panel.handle_palette_click(
                mouse_x, mouse_y, current_tileset['total_tiles']
            )
            if tile_index is not None:
                self.autotile_manager.register_autotile_set(
                    self.current_tileset_index, tile_index
                )
                if EditorConfig.DEBUG_VERBOSE:
                    mode = "8-bit" if self.autotile_manager.use_8bit else "4-bit"
                    print(f"Registered {mode} auto-tile set at tileset {self.current_tileset_index}, tile {tile_index}")
    
    def _handle_map_click(self, mouse_x, mouse_y):
        """Handle painting on the map"""
        current_tileset = self.tileset_manager.get_tileset(self.current_tileset_index)
        if not current_tileset or current_tileset['total_tiles'] == 0:
            return
        
        result = self.map_canvas.handle_paint(
            mouse_x, mouse_y, self.map_rows, self.map_cols,
            self.current_tileset_index, self.selected_tile
        )
        if result:
            row, col, tileset_idx, tile_idx = result
            # Only mark dirty if tile actually changed
            if self.map_grid[row, col, 0] != tileset_idx or self.map_grid[row, col, 1] != tile_idx:
                # Apply auto-tiling if enabled
                if self.autotile_enabled and self.autotile_manager.is_autotile(tileset_idx, tile_idx):
                    tile_updates = self.autotile_manager.apply_autotile(
                        self.map_grid, row, col, tileset_idx, tile_idx
                    )
                    # Apply all updates
                    for update_row, update_col, update_ts, update_tile in tile_updates:
                        if 0 <= update_row < self.map_rows and 0 <= update_col < self.map_cols:
                            self.map_grid[update_row, update_col, 0] = update_ts
                            self.map_grid[update_row, update_col, 1] = update_tile
                else:
                    # Normal placement without auto-tiling
                    self.map_grid[row, col, 0] = tileset_idx
                    self.map_grid[row, col, 1] = tile_idx
                self.file_manager.is_dirty = True
    
    def _handle_erase(self, pos):
        """Handle erasing tiles"""
        mouse_x, mouse_y = pos
        if not self.map_canvas.is_in_map_area(mouse_x, self.palette_panel.palette_x):
            return
        
        result = self.map_canvas.handle_erase(mouse_x, mouse_y, self.map_rows, self.map_cols)
        if result:
            row, col = result
            # Only mark dirty if tile was not already empty
            if self.map_grid[row, col, 0] != -1 or self.map_grid[row, col, 1] != -1:
                # Apply auto-tiling if enabled (update neighbors)
                if self.autotile_enabled:
                    tile_updates = self.autotile_manager.handle_erase_autotile(
                        self.map_grid, row, col
                    )
                    # Apply all updates (including erasing this tile)
                    for update_row, update_col, update_ts, update_tile in tile_updates:
                        if 0 <= update_row < self.map_rows and 0 <= update_col < self.map_cols:
                            self.map_grid[update_row, update_col, 0] = update_ts
                            self.map_grid[update_row, update_col, 1] = update_tile
                else:
                    # Normal erase without auto-tiling
                    self.map_grid[row, col, 0] = -1
                    self.map_grid[row, col, 1] = -1
                self.file_manager.is_dirty = True
    
    def _apply_grid_size(self):
        """Apply new grid size from input"""
        try:
            new_size = int(self.input_text)
            if EditorConfig.MIN_GRID_SIZE <= new_size <= EditorConfig.MAX_GRID_SIZE:
                if self.editing_cols:
                    self._resize_grid_width(new_size)
                elif self.editing_rows:
                    self._resize_grid_height(new_size)
        except ValueError:
            pass
        
        self.editing_cols = False
        self.editing_rows = False
        self.input_text = ""
    
    def _change_grid_width(self, delta):
        """Change grid width by delta"""
        new_cols = max(EditorConfig.MIN_GRID_SIZE, min(EditorConfig.MAX_GRID_SIZE, self.map_cols + delta))
        if new_cols != self.map_cols:
            self._resize_grid_width(new_cols)
    
    def _change_grid_height(self, delta):
        """Change grid height by delta"""
        new_rows = max(EditorConfig.MIN_GRID_SIZE, min(EditorConfig.MAX_GRID_SIZE, self.map_rows + delta))
        if new_rows != self.map_rows:
            self._resize_grid_height(new_rows)
    
    def _resize_grid_width(self, new_cols):
        """Resize grid width, preserving existing tiles"""
        old_grid = self.map_grid
        self.map_cols = new_cols
        self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
        copy_cols = min(old_grid.shape[1], self.map_cols)
        self.map_grid[:, :copy_cols, :] = old_grid[:, :copy_cols, :]
        self.file_manager.is_dirty = True
    
    def _resize_grid_height(self, new_rows):
        """Resize grid height, preserving existing tiles"""
        old_grid = self.map_grid
        self.map_rows = new_rows
        self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
        copy_rows = min(old_grid.shape[0], self.map_rows)
        self.map_grid[:copy_rows, :, :] = old_grid[:copy_rows, :, :]
        self.file_manager.is_dirty = True
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Draw everything
            self.screen.fill(self.bg_color)
            self.map_canvas.draw_map(self.map_grid, self.map_rows, self.map_cols, self.tileset_manager.tilesets)
            self.map_canvas.draw_grid(self.map_rows, self.map_cols)
            self.palette_panel.draw(self.tileset_manager.tilesets, self.current_tileset_index, self.selected_tile)
            
            current_tileset = self.tileset_manager.get_tileset(self.current_tileset_index)
            self.ui_panel.draw(
                self.map_name, self.editing_map_name, self.input_text,
                self.editing_cols, self.editing_rows, self.map_cols, self.map_rows,
                self.map_grid, self.tileset_manager.tilesets, current_tileset,
                self.file_manager.get_available_maps, self.autotile_enabled
            )
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        # Cleanup
        self.file_manager.stop_autosave()
        self.file_manager.save_config(self.map_name)
        pygame.quit()


if __name__ == '__main__':
    editor = TileEditor()
    editor.run()
