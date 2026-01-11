"""
Event Handler Module

Handles all user input events including keyboard, mouse, and window events.
"""

import pygame
from pygame.locals import *
from .configs import EditorConfig


class EventHandler:
    """Handles all user input events"""
    
    def __init__(self):
        """Initialize the event handler"""
        self.keys_pressed = {}
    
    def handle_keyboard_shortcuts(self):
        """
        Check for keyboard shortcuts (Ctrl+S, Ctrl+L, Ctrl+N, T, ESC)
        
        Returns:
            Action string or None: 'quit', 'save', 'load', 'clear', 'toggle_autotile', or None
        """
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        ctrl_pressed = mods & KMOD_CTRL
        
        if keys[K_ESCAPE]:
            return 'quit'
        if ctrl_pressed and keys[K_s]:
            return 'save'
        if ctrl_pressed and keys[K_l]:
            return 'load'
        if ctrl_pressed and keys[K_n]:
            return 'clear'
        if keys[K_t] and not self.keys_pressed.get(K_t, False):
            self.keys_pressed[K_t] = True
            return 'toggle_autotile'
        
        # Reset key state when released
        if not keys[K_t]:
            self.keys_pressed[K_t] = False
        
        return None
    
    def handle_camera_keys(self, map_rows, map_cols, map_tile_size, map_width, map_height):
        """
        Handle camera movement with arrow keys
        
        Args:
            map_rows: Number of rows in the map
            map_cols: Number of columns in the map
            map_tile_size: Size of map tiles in pixels
            map_width: Width of map area
            map_height: Height of map area
            
        Returns:
            Tuple of (delta_x, delta_y) for camera movement
        """
        keys = pygame.key.get_pressed()
        camera_speed = EditorConfig.CAMERA_SPEED
        dx, dy = 0, 0
        
        if keys[K_LEFT]:
            dx = -camera_speed
        if keys[K_RIGHT]:
            dx = camera_speed
        if keys[K_UP]:
            dy = -camera_speed
        if keys[K_DOWN]:
            dy = camera_speed
        
        return dx, dy
    
    def process_text_input(self, event, current_text, allow_special_chars=True):
        """
        Process text input events
        
        Args:
            event: Pygame KEYDOWN event
            current_text: Current text string
            allow_special_chars: Whether to allow special characters (for file names, set False)
            
        Returns:
            Tuple of (new_text, action) where action is 'submit', 'cancel', or 'update'
        """
        if event.key == K_RETURN:
            return (current_text, 'submit')
        elif event.key == K_ESCAPE:
            return (current_text, 'cancel')
        elif event.key == K_BACKSPACE:
            return (current_text[:-1], 'update')
        elif event.unicode.isdigit():
            return (current_text + event.unicode, 'update')
        elif not allow_special_chars and event.unicode.isprintable() and event.unicode not in '/\\:*?"<>|':
            return (current_text + event.unicode, 'update')
        elif allow_special_chars and event.unicode.isprintable():
            return (current_text + event.unicode, 'update')
        
        return (current_text, 'update')
