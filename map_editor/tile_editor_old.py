import sys
import json
import os
import pygame
from pygame.locals import *
import numpy as np
import threading
import time

from .editor_components.configs import EditorConfig, EditorColors, EditorText


class TileEditor:
    '''
    Simple tile map editor with tile palette and grid-based painting.
    '''
    def __init__(self, screen_width=EditorConfig.SCREEN_WIDTH, screen_height=EditorConfig.SCREEN_HEIGHT):
        pygame.init()
        pygame.display.set_caption(EditorText.WINDOW_TITLE)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.fps = EditorConfig.FPS
        
        # Multi-tileset support
        self.tile_size = EditorConfig.TILE_SIZE
        self.tilesets = []  # List of tileset dictionaries
        self.current_tileset_index = 0  # Active tileset for painting
        self.tileset_folder = None
        
        # Load tilesets from fixed folder
        self.load_tilesets_recursive('assets/tilesets')
        
        # UI Panel configuration (left side)
        self.ui_panel_width = EditorConfig.UI_PANEL_WIDTH
        self.ui_panel_x = EditorConfig.UI_PANEL_X
        
        # Palette configuration (right side)
        self.palette_width = EditorConfig.PALETTE_WIDTH
        self.palette_x = screen_width - self.palette_width
        self.palette_tile_size = EditorConfig.PALETTE_TILE_SIZE
        self.palette_cols = self.palette_width // self.palette_tile_size
        self.palette_scroll = 0
        self.tab_height = EditorConfig.TAB_HEIGHT
        self.palette_start_y = self.tab_height
        self.palette_rows_visible = (screen_height - self.tab_height) // self.palette_tile_size
        self.tab_rects = []  # Will store tab rectangles for click detection
        
        # Map configuration (center area)
        self.map_start_x = self.ui_panel_width + EditorConfig.MAP_SPACING
        self.map_width = self.palette_x - self.map_start_x - EditorConfig.MAP_SPACING
        self.map_height = screen_height
        self.map_tile_size = EditorConfig.MAP_TILE_SIZE
        self.map_cols = EditorConfig.DEFAULT_MAP_COLS
        self.map_rows = EditorConfig.DEFAULT_MAP_ROWS
        
        # Initialize empty map grid - stores (tileset_index, tile_index) pairs
        # (-1, -1) means no tile
        self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
        
        # Editor state
        self.selected_tile = 0  # Index of currently selected tile
        self.is_painting = False
        self.is_erasing = False
        self.camera_x = 0
        self.camera_y = 0
        
        # Grid size editing
        self.editing_cols = False
        self.editing_rows = False
        self.input_text = ""
        
        # Map name and file management
        self.map_name = "map"
        self.editing_map_name = False
        self.maps_folder = "map_editor/maps"
        self.is_dirty = False  # Track if map has unsaved changes
        self.last_autosave = time.time()
        
        # Create maps folder if it doesn't exist
        os.makedirs(self.maps_folder, exist_ok=True)
        
        # Start autosave thread
        self.running = True
        self.autosave_thread = threading.Thread(target=self._autosave_worker, daemon=True)
        self.autosave_thread.start()
        
        # Load last opened map from config
        self.load_config()
        
        # Button rectangles (will be set in draw_ui_panel)
        self.width_minus_rect = None
        self.width_value_rect = None
        self.width_plus_rect = None
        self.height_minus_rect = None
        self.height_value_rect = None
        self.height_plus_rect = None
        self.map_name_rect = None
        self.load_map_button_rect = None
        self.map_list_rects = []  # For dropdown items
        
        # UI colors
        self.bg_color = EditorColors.BG_COLOR
        self.ui_panel_bg = EditorColors.UI_PANEL_BG
        self.palette_bg = EditorColors.PALETTE_BG
        self.grid_color = EditorColors.GRID_COLOR
        self.selection_color = EditorColors.SELECTION_COLOR
        self.button_color = EditorColors.BUTTON_COLOR
        self.button_hover_color = EditorColors.BUTTON_HOVER_COLOR
        self.text_color = EditorColors.TEXT_COLOR
        
        # Fonts
        self.font = pygame.font.Font(None, EditorConfig.FONT_SIZE_NORMAL)
        self.title_font = pygame.font.Font(None, EditorConfig.FONT_SIZE_TITLE)
        self.small_font = pygame.font.Font(None, EditorConfig.FONT_SIZE_SMALL)
    
    def _autosave_worker(self):
        '''Background thread for auto-saving periodically if changes exist'''
        while self.running:
            time.sleep(EditorConfig.AUTOSAVE_INTERVAL)
            if self.is_dirty and self.running:
                self.save_map_silent()
                print(f"Auto-saved: {self.map_name}.json")
    
    def save_config(self):
        '''Save editor configuration (last opened map)'''
        try:
            config_data = {
                'last_map': self.map_name
            }
            with open(EditorConfig.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_config(self):
        '''Load editor configuration and restore last opened map'''
        try:
            if os.path.exists(EditorConfig.CONFIG_FILE):
                with open(EditorConfig.CONFIG_FILE, 'r') as f:
                    config_data = json.load(f)
                    last_map = config_data.get('last_map')
                    if last_map:
                        map_path = os.path.join(self.maps_folder, f"{last_map}.json")
                        if os.path.exists(map_path):
                            self.load_map_by_name(last_map)
                            print(f"Restored last session: {last_map}.json")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_map_silent(self):
        '''Save map without printing messages (for autosave)'''
        try:
            filepath = os.path.join(self.maps_folder, f"{self.map_name}.json")
            self.save_map(filepath)
            self.is_dirty = False
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    def get_available_maps(self):
        '''Get list of available map files'''
        if not os.path.exists(self.maps_folder):
            return []
        maps = [f[:-5] for f in os.listdir(self.maps_folder) if f.endswith('.json')]
        maps.sort()
        return maps
    
    def load_map_by_name(self, map_name):
        '''Load a map by its name'''
        filepath = os.path.join(self.maps_folder, f"{map_name}.json")
        if os.path.exists(filepath):
            self.load_map(filepath)
            self.map_name = map_name
            self.is_dirty = False
            print(f"Map loaded: {map_name}.json")
    
    def add_empty_tileset(self):
        '''Add an empty placeholder tileset'''
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
    
    def extract_tiles_from_image(self, tileset_image):
        '''Extract individual tiles from a tileset image'''
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
    
    def load_tilesets_recursive(self, root_folder):
        '''Load all PNG tilesets from folder and subfolders recursively'''
        try:
            self.tileset_folder = root_folder
            self.tilesets = []
            
            if not os.path.exists(root_folder):
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
                    print(EditorText.MSG_TILESET_LOADED.format(name, len(tiles)))
                except Exception as e:
                    print(EditorText.MSG_ERROR_LOADING_TILESET.format(rel_path, e))
            
            # Reset state
            self.current_tileset_index = 0
            self.selected_tile = 0
            self.palette_scroll = 0
            
            print(EditorText.MSG_TOTAL_TILESETS.format(len(self.tilesets)))
        except Exception as e:
            print(EditorText.MSG_ERROR_LOADING_FOLDER.format(e))
            self.add_empty_tileset()
    
    def get_current_tileset(self):
        '''Get the currently active tileset'''
        if 0 <= self.current_tileset_index < len(self.tilesets):
            return self.tilesets[self.current_tileset_index]
        return None
    
    def handle_events(self):
        '''Handle user input events'''
        keys = pygame.key.get_pressed()
        
        # Handle camera movement with arrow keys (only if not editing text)
        if not self.editing_cols and not self.editing_rows:
            camera_speed = EditorConfig.CAMERA_SPEED
            if keys[K_LEFT]:
                self.camera_x = max(0, self.camera_x - camera_speed)
            if keys[K_RIGHT]:
                max_camera_x = max(0, self.map_cols * self.map_tile_size - self.map_width)
                self.camera_x = min(max_camera_x, self.camera_x + camera_speed)
            if keys[K_UP]:
                self.camera_y = max(0, self.camera_y - camera_speed)
            if keys[K_DOWN]:
                max_camera_y = max(0, self.map_rows * self.map_tile_size - self.map_height)
                self.camera_y = min(max_camera_y, self.camera_y + camera_speed)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                # Handle text input for grid size or map name editing
                if self.editing_cols or self.editing_rows:
                    if event.key == K_RETURN:
                        self.apply_grid_size()
                    elif event.key == K_ESCAPE:
                        self.editing_cols = False
                        self.editing_rows = False
                        self.input_text = ""
                    elif event.key == K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isdigit():
                        self.input_text += event.unicode
                elif self.editing_map_name:
                    if event.key == K_RETURN:
                        if self.input_text.strip():
                            old_name = self.map_name
                            self.map_name = self.input_text.strip()
                            if old_name != self.map_name:
                                self.is_dirty = True
                        self.editing_map_name = False
                        self.input_text = ""
                    elif event.key == K_ESCAPE:
                        self.editing_map_name = False
                        self.input_text = ""
                    elif event.key == K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isprintable() and event.unicode not in '/\\:*?"<>|':
                        self.input_text += event.unicode
                else:
                    # Normal keyboard shortcuts
                    if event.key == K_ESCAPE:
                        return False
                    if event.key == K_s and (pygame.key.get_mods() & KMOD_CTRL):
                        filepath = os.path.join(self.maps_folder, f"{self.map_name}.json")
                        self.save_map(filepath)
                        self.is_dirty = False
                        print(f"Map saved: {self.map_name}.json")
                    if event.key == K_l and (pygame.key.get_mods() & KMOD_CTRL):
                        self.load_map(EditorConfig.DEFAULT_SAVE_FILE)
                        print(EditorText.MSG_MAP_LOADED)
                    if event.key == K_n and (pygame.key.get_mods() & KMOD_CTRL):
                        self.clear_map()
                        print(EditorText.MSG_MAP_CLEARED)
                    
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.is_painting = True
                    self.handle_click(event.pos)
                if event.button == 3:  # Right click
                    self.is_erasing = True
                    self.handle_erase(event.pos)
                    
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_painting = False
                if event.button == 3:
                    self.is_erasing = False
            
            if event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen_width = event.w
                self.screen_height = event.h
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # Recalculate layout
                self.palette_x = self.screen_width - self.palette_width
                self.map_width = self.palette_x - self.map_start_x - EditorConfig.MAP_SPACING
                self.map_height = self.screen_height
                self.palette_rows_visible = (self.screen_height - self.tab_height) // self.palette_tile_size
            
            if event.type == MOUSEWHEEL:
                # Handle all scrolling through this event
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos
                
                # Vertical scroll (event.y)
                if event.y != 0:
                    # Check if mouse is over palette
                    if mouse_x >= self.palette_x:
                        # Scroll palette vertically
                        current_tileset = self.get_current_tileset()
                        if current_tileset and current_tileset['total_tiles'] > 0:
                            total_rows = (current_tileset['total_tiles'] + self.palette_cols - 1) // self.palette_cols
                            max_scroll = max(0, total_rows - self.palette_rows_visible + 1)
                            self.palette_scroll = max(0, min(max_scroll, self.palette_scroll - event.y))
                    # Check if mouse is over map
                    elif self.map_start_x <= mouse_x < self.palette_x:
                        # Vertical scroll on map
                        scroll_amount = self.map_tile_size * -event.y
                        max_camera_y = max(0, self.map_rows * self.map_tile_size - self.map_height)
                        self.camera_y = max(0, min(max_camera_y, self.camera_y + scroll_amount))
                
                # Horizontal scroll (event.x) - only for map
                if event.x != 0 and self.map_start_x <= mouse_x < self.palette_x:
                    scroll_amount = self.map_tile_size * event.x
                    max_camera_x = max(0, self.map_cols * self.map_tile_size - self.map_width)
                    self.camera_x = max(0, min(max_camera_x, self.camera_x + scroll_amount))
                    
            if event.type == MOUSEMOTION:
                if self.is_painting:
                    self.handle_click(event.pos)
                if self.is_erasing:
                    self.handle_erase(event.pos)
        
        return True
    
    def apply_grid_size(self):
        '''Apply the new grid size from user input'''
        try:
            new_size = int(self.input_text)
            if EditorConfig.MIN_GRID_SIZE <= new_size <= EditorConfig.MAX_GRID_SIZE:
                if self.editing_cols:
                    old_grid = self.map_grid
                    self.map_cols = new_size
                    self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
                    # Copy old data
                    copy_cols = min(old_grid.shape[1], self.map_cols)
                    self.map_grid[:, :copy_cols, :] = old_grid[:, :copy_cols, :]
                    # Clamp camera to new bounds
                    max_camera_x = max(0, self.map_cols * self.map_tile_size - self.map_width)
                    self.camera_x = min(self.camera_x, max_camera_x)
                elif self.editing_rows:
                    old_grid = self.map_grid
                    self.map_rows = new_size
                    self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
                    # Copy old data
                    copy_rows = min(old_grid.shape[0], self.map_rows)
                    self.map_grid[:copy_rows, :, :] = old_grid[:copy_rows, :, :]
                    # Clamp camera to new bounds
                    max_camera_y = max(0, self.map_rows * self.map_tile_size - self.map_height)
                    self.camera_y = min(self.camera_y, max_camera_y)
        except ValueError:
            pass
        
        self.editing_cols = False
        self.editing_rows = False
        self.input_text = ""
    
    def handle_click(self, pos):
        '''Handle mouse click for tile selection or painting'''
        mouse_x, mouse_y = pos
        
        # Check if click is in UI panel (left side)
        if mouse_x < self.ui_panel_width:
            self.handle_ui_click(mouse_x, mouse_y)
        # Check if click is in palette area (right side)
        elif mouse_x >= self.palette_x:
            # Check if click is in tab area
            if mouse_y < self.tab_height:
                self.handle_tab_click(mouse_x, mouse_y)
            else:
                self.handle_palette_click(mouse_x, mouse_y)
        # Check if click is in map area (center)
        elif mouse_x >= self.map_start_x:
            self.handle_map_click(mouse_x, mouse_y)
    
    def handle_ui_click(self, mouse_x, mouse_y):
        '''Handle clicks in the UI panel for grid size editing and map management'''
        mouse_pos = (mouse_x, mouse_y)
        
        # Map name input
        if self.map_name_rect and self.map_name_rect.collidepoint(mouse_pos):
            self.editing_map_name = True
            self.editing_cols = False
            self.editing_rows = False
            self.input_text = self.map_name
            return
        
        # Load map button (toggles dropdown)
        if self.load_map_button_rect and self.load_map_button_rect.collidepoint(mouse_pos):
            # Toggle dropdown visibility
            if len(self.map_list_rects) > 0:
                self.map_list_rects = []  # Close dropdown
            else:
                # Open dropdown by populating rects (will be drawn in draw_ui_panel)
                available_maps = self.get_available_maps()
                self.map_list_rects = [None] * min(len(available_maps), 5)  # Placeholder
            return
        
        # Check map list items if dropdown is shown
        for i, rect in enumerate(self.map_list_rects):
            if rect and rect.collidepoint(mouse_pos):
                available_maps = self.get_available_maps()
                if i < len(available_maps):
                    self.load_map_by_name(available_maps[i])
                    self.map_list_rects = []  # Close dropdown
                return
        
        # Width - button (decrease)
        if self.width_minus_rect and self.width_minus_rect.collidepoint(mouse_pos):
            self.change_grid_width(-1)
        # Width + button (increase)
        elif self.width_plus_rect and self.width_plus_rect.collidepoint(mouse_pos):
            self.change_grid_width(1)
        # Width value (click to type)
        elif self.width_value_rect and self.width_value_rect.collidepoint(mouse_pos):
            self.editing_cols = True
            self.editing_rows = False
            self.input_text = str(self.map_cols)
        
        # Height - button (decrease)
        elif self.height_minus_rect and self.height_minus_rect.collidepoint(mouse_pos):
            self.change_grid_height(-1)
        # Height + button (increase)
        elif self.height_plus_rect and self.height_plus_rect.collidepoint(mouse_pos):
            self.change_grid_height(1)
        # Height value (click to type)
        elif self.height_value_rect and self.height_value_rect.collidepoint(mouse_pos):
            self.editing_rows = True
            self.editing_cols = False
            self.input_text = str(self.map_rows)
    
    def change_grid_width(self, delta):
        '''Change grid width by delta in real time'''
        new_cols = max(EditorConfig.MIN_GRID_SIZE, min(EditorConfig.MAX_GRID_SIZE, self.map_cols + delta))
        if new_cols != self.map_cols:
            old_grid = self.map_grid
            self.map_cols = new_cols
            self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
            # Copy old data
            copy_cols = min(old_grid.shape[1], self.map_cols)
            self.map_grid[:, :copy_cols, :] = old_grid[:, :copy_cols, :]
            # Clamp camera to new bounds
            max_camera_x = max(0, self.map_cols * self.map_tile_size - self.map_width)
            self.camera_x = min(self.camera_x, max_camera_x)
            self.is_dirty = True
    
    def change_grid_height(self, delta):
        '''Change grid height by delta in real time'''
        new_rows = max(EditorConfig.MIN_GRID_SIZE, min(EditorConfig.MAX_GRID_SIZE, self.map_rows + delta))
        if new_rows != self.map_rows:
            old_grid = self.map_grid
            self.map_rows = new_rows
            self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
            # Copy old data
            copy_rows = min(old_grid.shape[0], self.map_rows)
            self.map_grid[:copy_rows, :, :] = old_grid[:copy_rows, :, :]
            # Clamp camera to new bounds
            max_camera_y = max(0, self.map_rows * self.map_tile_size - self.map_height)
            self.camera_y = min(self.camera_y, max_camera_y)
            self.is_dirty = True
    
    def handle_tab_click(self, mouse_x, mouse_y):
        '''Handle clicks on tileset tabs'''
        mouse_pos = (mouse_x, mouse_y)
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(mouse_pos):
                self.current_tileset_index = i
                self.selected_tile = 0
                self.palette_scroll = 0
                break
    
    def handle_palette_click(self, mouse_x, mouse_y):
        '''Select a tile from the palette'''
        current_tileset = self.get_current_tileset()
        if not current_tileset or current_tileset['total_tiles'] == 0:
            return
        
        local_x = mouse_x - self.palette_x
        local_y = mouse_y - self.palette_start_y + (self.palette_scroll * self.palette_tile_size)
        
        col = local_x // self.palette_tile_size
        row = local_y // self.palette_tile_size
        
        tile_index = row * self.palette_cols + col
        if 0 <= tile_index < current_tileset['total_tiles']:
            self.selected_tile = tile_index
    
    def handle_map_click(self, mouse_x, mouse_y):
        '''Paint a tile on the map'''
        current_tileset = self.get_current_tileset()
        if not current_tileset or current_tileset['total_tiles'] == 0:
            return
        
        local_x = mouse_x - self.map_start_x
        col = (local_x + self.camera_x) // self.map_tile_size
        row = (mouse_y + self.camera_y) // self.map_tile_size
        
        if 0 <= row < self.map_rows and 0 <= col < self.map_cols:
            # Store both tileset index and tile index
            self.map_grid[row, col, 0] = self.current_tileset_index
            self.map_grid[row, col, 1] = self.selected_tile
            self.is_dirty = True
    
    def handle_erase(self, pos):
        '''Erase a tile from the map'''
        mouse_x, mouse_y = pos
        if self.map_start_x <= mouse_x < self.palette_x:
            local_x = mouse_x - self.map_start_x
            col = (local_x + self.camera_x) // self.map_tile_size
            row = (mouse_y + self.camera_y) // self.map_tile_size
            
            if 0 <= row < self.map_rows and 0 <= col < self.map_cols:
                self.map_grid[row, col, 0] = -1
                self.map_grid[row, col, 1] = -1
                self.is_dirty = True
    
    def draw_grid(self):
        '''Draw the grid lines on the map'''
        # Clip drawing to map area
        clip_rect = pygame.Rect(self.map_start_x, 0, self.map_width, self.map_height)
        self.screen.set_clip(clip_rect)
        
        # Vertical lines
        for col in range(self.map_cols + 1):
            x = self.map_start_x + col * self.map_tile_size - self.camera_x
            if self.map_start_x - self.map_tile_size < x < self.map_start_x + self.map_width:
                pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.map_height), 1)
        
        # Horizontal lines
        for row in range(self.map_rows + 1):
            y = row * self.map_tile_size - self.camera_y
            if -self.map_tile_size < y < self.map_height:
                pygame.draw.line(self.screen, self.grid_color, (self.map_start_x, y), (self.map_start_x + self.map_width, y), 1)
        
        self.screen.set_clip(None)
    
    def draw_map(self):
        '''Draw the map with placed tiles'''
        # Clip drawing to map area
        clip_rect = pygame.Rect(self.map_start_x, 0, self.map_width, self.map_height)
        self.screen.set_clip(clip_rect)
        
        for row in range(self.map_rows):
            for col in range(self.map_cols):
                tileset_idx = self.map_grid[row, col, 0]
                tile_idx = self.map_grid[row, col, 1]
                
                if tileset_idx >= 0 and tile_idx >= 0:
                    # Get the correct tileset
                    if tileset_idx < len(self.tilesets):
                        tileset = self.tilesets[tileset_idx]
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
    
    def draw_palette(self):
        '''Draw the tile palette on the right side with tabs'''
        # Draw palette background
        pygame.draw.rect(self.screen, self.palette_bg, 
                        (self.palette_x, 0, self.palette_width, self.screen_height))
        
        # Draw tabs
        self.draw_tileset_tabs()
        
        # Get current tileset
        current_tileset = self.get_current_tileset()
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
                if i == self.selected_tile:
                    pygame.draw.rect(self.screen, self.selection_color, 
                                   (x, y, self.palette_tile_size, self.palette_tile_size), 3)
        
        self.screen.set_clip(None)
        
        # Draw scrollbar indicator if needed
        total_rows = (current_tileset['total_tiles'] + self.palette_cols - 1) // self.palette_cols
        if total_rows > self.palette_rows_visible:
            scrollbar_height = max(EditorConfig.SCROLLBAR_MIN_HEIGHT, 
                                  int((self.screen_height - self.tab_height) * self.palette_rows_visible / total_rows))
            scrollbar_y = self.tab_height + int(self.palette_scroll * ((self.screen_height - self.tab_height) - scrollbar_height) / 
                            (total_rows - self.palette_rows_visible))
            pygame.draw.rect(self.screen, self.selection_color,
                           (self.palette_x - EditorConfig.SCROLLBAR_OFFSET, scrollbar_y, 
                            EditorConfig.SCROLLBAR_WIDTH, scrollbar_height))
    
    def draw_tileset_tabs(self):
        '''Draw tabs for switching between tilesets'''
        self.tab_rects = []
        
        if not self.tilesets:
            return
        
        # Calculate tab width
        tab_width = self.palette_width // len(self.tilesets) if len(self.tilesets) > 0 else self.palette_width
        tab_width = max(EditorConfig.TAB_MIN_WIDTH, min(tab_width, EditorConfig.TAB_MAX_WIDTH))
        
        for i, tileset in enumerate(self.tilesets):
            x = self.palette_x + i * tab_width
            
            # Tab background
            tab_color = self.button_hover_color if i == self.current_tileset_index else self.button_color
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
    
    def draw_ui_panel(self):
        '''Draw the UI panel on the left side with instructions and controls'''
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
        map_title = self.font.render("=== MAP FILE ===", True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(map_title, (10, y_offset))
        y_offset += 25
        
        # Map name label
        name_label = self.font.render("Name:", True, self.text_color)
        self.screen.blit(name_label, (10, y_offset))
        y_offset += 20
        
        # Map name input
        self.map_name_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_LARGE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = self.button_hover_color if self.editing_map_name else self.button_color
        pygame.draw.rect(self.screen, button_color, self.map_name_rect)
        pygame.draw.rect(self.screen, self.text_color, self.map_name_rect, 2)
        
        if self.editing_map_name:
            name_text = self.font.render(self.input_text + "_", True, self.selection_color)
        else:
            name_text = self.font.render(self.map_name, True, self.text_color)
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
            available_maps = self.get_available_maps()
            self.map_list_rects = []  # Rebuild list
            for i, map_name in enumerate(available_maps[:5]):  # Show max 5 maps
                rect = pygame.Rect(10, y_offset + i * 25, EditorConfig.BUTTON_LARGE_WIDTH, 25)
                self.map_list_rects.append(rect)
                pygame.draw.rect(self.screen, self.button_color, rect)
                pygame.draw.rect(self.screen, self.text_color, rect, 1)
                map_text = self.small_font.render(map_name, True, self.text_color)
                self.screen.blit(map_text, (rect.x + 5, rect.y + 5))
            y_offset += len(available_maps[:5]) * 25
        
        y_offset += 10
        
        # Grid size controls
        grid_title = self.font.render(EditorText.HEADER_GRID_SIZE, True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(grid_title, (10, y_offset))
        y_offset += 25
        
        # Width control
        width_label = self.font.render(EditorText.LABEL_WIDTH, True, self.text_color)
        self.screen.blit(width_label, (10, y_offset))
        y_offset += 20
        
        # Width controls: [-] [value] [+]
        # Minus button
        self.width_minus_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, self.width_minus_rect)
        pygame.draw.rect(self.screen, self.text_color, self.width_minus_rect, 2)
        minus_text = self.title_font.render(EditorText.BUTTON_MINUS, True, self.text_color)
        minus_text_rect = minus_text.get_rect(center=self.width_minus_rect.center)
        self.screen.blit(minus_text, minus_text_rect)
        
        # Value display/input
        self.width_value_rect = pygame.Rect(45, y_offset, EditorConfig.BUTTON_VALUE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = self.button_hover_color if self.editing_cols else self.button_color
        pygame.draw.rect(self.screen, button_color, self.width_value_rect)
        pygame.draw.rect(self.screen, self.text_color, self.width_value_rect, 2)
        
        if self.editing_cols:
            width_text = self.font.render(self.input_text + "_", True, self.selection_color)
        else:
            width_text = self.font.render(str(self.map_cols), True, self.text_color)
        text_rect = width_text.get_rect(center=self.width_value_rect.center)
        self.screen.blit(width_text, text_rect)
        
        # Plus button
        self.width_plus_rect = pygame.Rect(180, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, self.width_plus_rect)
        pygame.draw.rect(self.screen, self.text_color, self.width_plus_rect, 2)
        plus_text = self.title_font.render(EditorText.BUTTON_PLUS, True, self.text_color)
        plus_text_rect = plus_text.get_rect(center=self.width_plus_rect.center)
        self.screen.blit(plus_text, plus_text_rect)
        
        y_offset += 40
        
        # Height control
        height_label = self.font.render(EditorText.LABEL_HEIGHT, True, self.text_color)
        self.screen.blit(height_label, (10, y_offset))
        y_offset += 20
        
        # Height controls: [-] [value] [+]
        # Minus button
        self.height_minus_rect = pygame.Rect(10, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, self.height_minus_rect)
        pygame.draw.rect(self.screen, self.text_color, self.height_minus_rect, 2)
        minus_text = self.title_font.render(EditorText.BUTTON_MINUS, True, self.text_color)
        minus_text_rect = minus_text.get_rect(center=self.height_minus_rect.center)
        self.screen.blit(minus_text, minus_text_rect)
        
        # Value display/input
        self.height_value_rect = pygame.Rect(45, y_offset, EditorConfig.BUTTON_VALUE_WIDTH, EditorConfig.BUTTON_HEIGHT)
        button_color = self.button_hover_color if self.editing_rows else self.button_color
        pygame.draw.rect(self.screen, button_color, self.height_value_rect)
        pygame.draw.rect(self.screen, self.text_color, self.height_value_rect, 2)
        
        if self.editing_rows:
            height_text = self.font.render(self.input_text + "_", True, self.selection_color)
        else:
            height_text = self.font.render(str(self.map_rows), True, self.text_color)
        text_rect = height_text.get_rect(center=self.height_value_rect.center)
        self.screen.blit(height_text, text_rect)
        
        # Plus button
        self.height_plus_rect = pygame.Rect(180, y_offset, EditorConfig.BUTTON_SMALL_SIZE, EditorConfig.BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.button_color, self.height_plus_rect)
        pygame.draw.rect(self.screen, self.text_color, self.height_plus_rect, 2)
        plus_text = self.title_font.render(EditorText.BUTTON_PLUS, True, self.text_color)
        plus_text_rect = plus_text.get_rect(center=self.height_plus_rect.center)
        self.screen.blit(plus_text, plus_text_rect)
        
        y_offset += 40
        
        # Map info
        info_title = self.font.render(EditorText.HEADER_MAP_INFO, True, EditorColors.TEXT_HIGHLIGHT_COLOR)
        self.screen.blit(info_title, (10, y_offset))
        y_offset += 25
        
        # Count tiles (check first dimension of third axis for non-empty tiles)
        total_tiles_placed = np.sum(self.map_grid[:, :, 0] >= 0)
        
        current_tileset = self.get_current_tileset()
        current_tileset_info = EditorText.INFO_TILESET_LOADED.format(len(self.tilesets))
        if current_tileset:
            current_tileset_info = EditorText.INFO_TILESET_DETAILS.format(current_tileset['name'], current_tileset['total_tiles'])
        
        info_texts = [
            EditorText.INFO_TILE.format(self.selected_tile),
            EditorText.INFO_TOTAL.format(total_tiles_placed),
            EditorText.INFO_TILESET.format(current_tileset_info)
        ]
        
        for text in info_texts:
            text_surf = self.font.render(text, True, EditorColors.TEXT_DIM_COLOR)
            self.screen.blit(text_surf, (10, y_offset))
            y_offset += 22
    
    def draw_ui(self):
        '''Draw UI elements and instructions'''
        font = pygame.font.Font(None, 24)
        instructions = [
            "Left Click: Paint",
            "Right Click: Erase",
            "Ctrl+S: Save",
            "Ctrl+L: Load",
            "Ctrl+N: Clear",
            "ESC: Exit"
        ]
        
        y_offset = 10
        for text in instructions:
            text_surf = font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surf, (self.palette_x + 10, y_offset))
            y_offset += 25
    
    def save_map(self, filename):
        '''Save the map to a JSON file with multi-tileset support'''
        # Collect information about all tilesets used in the map
        tilesets_info = []
        for tileset in self.tilesets:
            tilesets_info.append({
                'name': tileset['name'],
                'path': tileset['path'],
                'tiles_per_row': tileset['tiles_per_row'],
                'tiles_per_col': tileset['tiles_per_col'],
                'total_tiles': tileset['total_tiles']
            })
        
        map_data = {
            "tile_width": self.tile_size,
            "tile_height": self.tile_size,
            "map_tile_size": self.map_tile_size,
            "width": self.map_cols,
            "height": self.map_rows,
            "tilegrid": self.map_grid.tolist(),
            "tileset_folder": self.tileset_folder,
            "tilesets": tilesets_info
        }
        
        with open(filename, 'w') as f:
            json.dump(map_data, f, indent=4)
    
    def load_map(self, filename):
        '''Load a map from a JSON file with multi-tileset support'''
        try:
            with open(filename, 'r') as f:
                map_data = json.load(f)
                
                # Load tileset folder if specified
                if "tileset_folder" in map_data and map_data["tileset_folder"]:
                    self.load_tilesets_recursive(map_data["tileset_folder"])
                elif "tilesets" in map_data:
                    # Alternative: load individual tilesets from paths
                    self.tilesets = []
                    for ts_info in map_data["tilesets"]:
                        if ts_info['path'] and os.path.exists(ts_info['path']):
                            try:
                                tileset_image = pygame.image.load(ts_info['path'])
                                tiles, tiles_per_row, tiles_per_col = self.extract_tiles_from_image(tileset_image)
                                tileset = {
                                    'name': ts_info['name'],
                                    'path': ts_info['path'],
                                    'image': tileset_image,
                                    'tiles': tiles,
                                    'tiles_per_row': tiles_per_row,
                                    'tiles_per_col': tiles_per_col,
                                    'total_tiles': len(tiles)
                                }
                                self.tilesets.append(tileset)
                            except Exception as e:
                                print(EditorText.MSG_ERROR_LOADING_TILESET.format(ts_info['name'], e))
                
                # Validate tilesets match the map file
                if "tilesets" in map_data:
                    saved_tilesets = map_data["tilesets"]
                    
                    # Check if tileset count matches
                    if len(self.tilesets) != len(saved_tilesets):
                        print(f"WARNING: Tileset count mismatch!")
                        print(f"  Map expects {len(saved_tilesets)} tilesets, but {len(self.tilesets)} are loaded.")
                        print(f"  Map may not render correctly!")
                    
                    # Check if tileset names and order match
                    mismatches = []
                    for i, saved_ts in enumerate(saved_tilesets):
                        if i < len(self.tilesets):
                            if self.tilesets[i]['name'] != saved_ts['name']:
                                mismatches.append(f"  Index {i}: Expected '{saved_ts['name']}', got '{self.tilesets[i]['name']}'")
                        else:
                            mismatches.append(f"  Index {i}: Expected '{saved_ts['name']}', but no tileset loaded")
                    
                    if mismatches:
                        print("ERROR: Tileset mismatch detected!")
                        print("The map uses different tilesets than currently loaded:")
                        for msg in mismatches:
                            print(msg)
                        print("The map will render incorrectly. Please ensure the same tilesets are loaded.")
                        return  # Abort loading
                
                # Load map grid
                loaded_grid = np.array(map_data["tilegrid"], dtype=int)
                
                # Handle both old format (2D) and new format (3D)
                if len(loaded_grid.shape) == 2:
                    # Old format: convert to new format
                    self.map_rows, self.map_cols = loaded_grid.shape
                    self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
                    # Assume all tiles came from tileset 0
                    for row in range(self.map_rows):
                        for col in range(self.map_cols):
                            if loaded_grid[row, col] >= 0:
                                self.map_grid[row, col, 0] = 0
                                self.map_grid[row, col, 1] = loaded_grid[row, col]
                else:
                    # New format
                    self.map_grid = loaded_grid
                    self.map_rows, self.map_cols = loaded_grid.shape[0], loaded_grid.shape[1]
                
                print(EditorText.MSG_MAP_LOADED)
        except FileNotFoundError:
            print(EditorText.MSG_FILE_NOT_FOUND.format(filename))
        except Exception as e:
            print(EditorText.MSG_ERROR_LOADING_MAP.format(e))
    
    def clear_map(self):
        '''Clear the entire map'''
        self.map_grid = np.full((self.map_rows, self.map_cols, 2), -1, dtype=int)
        self.is_dirty = True
    
    def run(self):
        '''Main editor loop'''
        running = True
        while running:
            running = self.handle_events()
            
            # Clear screen
            self.screen.fill(self.bg_color)
            
            # Draw elements in order
            self.draw_grid()
            self.draw_map()
            self.draw_ui_panel()
            self.draw_palette()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        # Cleanup
        self.running = False
        if self.autosave_thread.is_alive():
            self.autosave_thread.join(timeout=1.0)
        self.save_config()
        
        pygame.quit()


if __name__ == '__main__':
    editor = TileEditor()
    editor.run()
