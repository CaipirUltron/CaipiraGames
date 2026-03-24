"""
Enhanced Spritesheet Stitcher - Pack sprites with animation tracking.

Combines individual sprite images and existing spritesheets into a single
character spritesheet with automatic JSON schema generation for the Animation class.

Key features:
- Empty initialization; dimensions auto-detect from first sprite
- Add individual sprites or entire spritesheets with animation mapping
- Flexible layout: tight-pack with optional row/column constraints
- Automatic JSON schema generation compatible with Animation.from_json()
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow (PIL) is required. Install with: pip install Pillow")


class Stitcher:
    """
    Pack individual sprites and spritesheets into a single character spritesheet.
    
    Maintains internal animation name registry and sprite-to-animation mapping.
    Generates output spritesheet PNG and JSON schema for the Animation class.
    """
    
    SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    def __init__(self):
        """Initialize empty Stitcher. Dimensions set on first sprite addition."""
        self.sprites: List[Image.Image] = []
        self.animation_map: List[int] = []  # animation_id for each sprite in add order
        self.animation_names: Dict[int, str] = {}  # animation_id -> name
        self.frame_width: Optional[int] = None
        self.frame_height: Optional[int] = None
        self.next_animation_id: int = 0
        self.max_width: Optional[int] = None
        self.max_height: Optional[int] = None
    
    def add_sprite(self, image_path: str, animation_name: str) -> None:
        """
        Add a single sprite image assigned to an animation.
        
        Args:
            image_path: Path to sprite image
            animation_name: Name of animation this sprite belongs to
        
        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If sprite dimensions incompatible with existing sprites
        """
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Sprite image not found: {image_path}")
        
        img = Image.open(img_path).convert("RGBA")
        img_width, img_height = img.size
        
        # Set or validate dimensions
        if self.frame_width is None:
            self.frame_width = img_width
            self.frame_height = img_height
            print(f"[Stitcher] Frame size detected: {self.frame_width}x{self.frame_height}")
        elif (img_width, img_height) != (self.frame_width, self.frame_height):
            raise ValueError(
                f"Sprite {img_path.name} size ({img_width}x{img_height}) "
                f"incompatible with frame size ({self.frame_width}x{self.frame_height})"
            )
        
        # Register or retrieve animation_id
        anim_id = self._get_or_create_animation_id(animation_name)
        
        self.sprites.append(img)
        self.animation_map.append(anim_id)
        print(f"  ✓ Added sprite: {img_path.name} → animation '{animation_name}'")
    
    def add_spritesheet(
        self,
        path: str,
        rows: int,
        cols: int,
        animation_matrix: Optional[Union[str, List[List[Union[str, int]]]]] = None,
    ) -> None:
        """
        Add an existing spritesheet, extracting NxM sprites with animation mapping.
        
        Args:
            path: Path to spritesheet image
            rows: Number of rows of sprites
            cols: Number of columns of sprites
            animation_matrix: Optional animation assignment matrix:
                - str: Single animation name (all sprites assigned to it)
                - List[List[str]]: Matrix of animation names (e.g., [["walk", "run"], ...])
                - List[List[int]]: Matrix of animation IDs with separate animation_names dict
                
                If omitted, all sprites assigned to animation named "default"
        
        Raises:
            FileNotFoundError: If spritesheet doesn't exist
            ValueError: If dimensions incompatible or matrix doesn't match grid
        """
        sheet_path = Path(path)
        if not sheet_path.exists():
            raise FileNotFoundError(f"Spritesheet not found: {path}")
        
        sheet_img = Image.open(sheet_path).convert("RGBA")
        sheet_width, sheet_height = sheet_img.size
        
        # Calculate frame dimensions from sheet
        sprite_width = sheet_width // cols
        sprite_height = sheet_height // rows
        
        if sprite_width * cols != sheet_width or sprite_height * rows != sheet_height:
            raise ValueError(
                f"Spritesheet {sheet_width}x{sheet_height} cannot be evenly divided "
                f"into {rows}x{cols} grid"
            )
        
        # Set or validate frame dimensions
        if self.frame_width is None:
            self.frame_width = sprite_width
            self.frame_height = sprite_height
            print(f"[Stitcher] Frame size detected: {self.frame_width}x{self.frame_height}")
        elif (sprite_width, sprite_height) != (self.frame_width, self.frame_height):
            raise ValueError(
                f"Spritesheet sprites ({sprite_width}x{sprite_height}) "
                f"incompatible with frame size ({self.frame_width}x{self.frame_height})"
            )
        
        # Parse animation matrix
        anim_matrix: List[List[int]] = []
        if animation_matrix is None:
            # All sprites same animation
            anim_id = self._get_or_create_animation_id("default")
            anim_matrix = [[anim_id] * cols for _ in range(rows)]
        elif isinstance(animation_matrix, str):
            # Single animation name
            anim_id = self._get_or_create_animation_id(animation_matrix)
            anim_matrix = [[anim_id] * cols for _ in range(rows)]
        elif isinstance(animation_matrix, list):
            # Matrix of names or IDs
            if len(animation_matrix) != rows:
                raise ValueError(f"Animation matrix rows ({len(animation_matrix)}) != sprite rows ({rows})")
            for i, row in enumerate(animation_matrix):
                if len(row) != cols:
                    raise ValueError(f"Animation matrix row {i} has {len(row)} cols, expected {cols}")
                anim_id_row = []
                for cell in row:
                    if isinstance(cell, str):
                        anim_id = self._get_or_create_animation_id(cell)
                    else:
                        anim_id = int(cell)
                    anim_id_row.append(anim_id)
                anim_matrix.append(anim_id_row)
        
        # Extract and add sprites
        print(f"[Stitcher] Extracting {rows}x{cols} sprites from {sheet_path.name}")
        for r in range(rows):
            for c in range(cols):
                x = c * sprite_width
                y = r * sprite_height
                sprite = sheet_img.crop((x, y, x + sprite_width, y + sprite_height))
                self.sprites.append(sprite)
                self.animation_map.append(anim_matrix[r][c])
        print(f"  ✓ Extracted {rows * cols} sprites")
    
    def set_max_width(self, num_sprites: int) -> None:
        """
        Set maximum sprites per row. Layout wraps to new row when exceeded.
        
        Args:
            num_sprites: Max sprite count per row
        """
        if num_sprites <= 0:
            raise ValueError(f"Max width must be positive, got {num_sprites}")
        self.max_width = num_sprites
        print(f"[Stitcher] Set max width: {num_sprites} sprites/row")
    
    def set_max_height(self, num_sprites: int) -> None:
        """
        Set maximum sprites per column. Layout wraps to new column when exceeded.
        
        Args:
            num_sprites: Max sprite count per column
        """
        if num_sprites <= 0:
            raise ValueError(f"Max height must be positive, got {num_sprites}")
        self.max_height = num_sprites
        print(f"[Stitcher] Set max height: {num_sprites} sprites/column")
    
    def _get_or_create_animation_id(self, name: str) -> int:
        """Get existing animation_id or create new one for animation name."""
        for anim_id, anim_name in self.animation_names.items():
            if anim_name == name:
                return anim_id
        anim_id = self.next_animation_id
        self.animation_names[anim_id] = name
        self.next_animation_id += 1
        return anim_id
    
    def _calculate_layout(self) -> Tuple[int, int]:
        """
        Calculate output grid dimensions (rows, cols) respecting constraints.
        
        Returns:
            Tuple of (output_rows, output_cols)
        """
        total_sprites = len(self.sprites)
        
        if self.max_width is not None:
            # Max width constraint: calculate rows needed
            output_cols = self.max_width
            output_rows = (total_sprites + output_cols - 1) // output_cols
        elif self.max_height is not None:
            # Max height constraint: calculate cols needed
            output_rows = self.max_height
            output_cols = (total_sprites + output_rows - 1) // output_rows
        else:
            # Default: balanced square layout
            output_cols = math.ceil(math.sqrt(total_sprites))
            output_rows = (total_sprites + output_cols - 1) // output_cols
        
        return output_rows, output_cols
    
    def _build_output_animation_map(
        self, output_rows: int, output_cols: int
    ) -> List[List[int]]:
        """
        Build 2D output animation map from sprite list and layout.
        
        Returns:
            2D list where element [r][c] is animation_id at that grid position
        """
        output_map: List[List[int]] = []
        sprite_idx = 0
        
        for r in range(output_rows):
            row = []
            for c in range(output_cols):
                if sprite_idx < len(self.sprites):
                    row.append(self.animation_map[sprite_idx])
                    sprite_idx += 1
                else:
                    # Pad with -1 (unused)
                    row.append(-1)
            output_map.append(row)
        
        return output_map
    
    def _build_animation_schema(
        self, output_map: List[List[int]]
    ) -> Dict[str, Dict[str, int]]:
        """
        Build animation metadata schema from output grid.
        
        Scans output_map row by row, tracking both row and column where each
        animation starts, plus frame count.
        Generates {"animation_name": {"row": R, "col": C, "frame_count": M}, ...}
        
        Returns:
            Dict mapping animation name to row, col, and frame count
        """
        schema: Dict[str, Dict[str, int]] = {}
        
        for row_idx, row in enumerate(output_map):
            # Find contiguous animation segments in this row
            current_anim_id: Optional[int] = None
            segment_start: int = 0
            
            for col_idx, anim_id in enumerate(row):
                # Check if segment ends (animation changes or cell is unused)
                if anim_id == -1 or (current_anim_id is not None and anim_id != current_anim_id):
                    if current_anim_id is not None and current_anim_id != -1:
                        # Record completed segment
                        anim_name = self.animation_names[current_anim_id]
                        frame_count = col_idx - segment_start
                        
                        if anim_name not in schema:
                            schema[anim_name] = {
                                "row": row_idx,
                                "col": segment_start,
                                "frame_count": frame_count
                            }
                        else:
                            # Animation already exists, update frame_count
                            schema[anim_name]["frame_count"] += frame_count
                    
                    if anim_id != -1:
                        current_anim_id = anim_id
                        segment_start = col_idx
                    else:
                        current_anim_id = None
                elif current_anim_id is None and anim_id != -1:
                    current_anim_id = anim_id
                    segment_start = col_idx
            
            # Finalize last segment in row
            if current_anim_id is not None and current_anim_id != -1:
                anim_name = self.animation_names[current_anim_id]
                frame_count = len(row) - segment_start
                if anim_name not in schema:
                    schema[anim_name] = {
                        "row": row_idx,
                        "col": segment_start,
                        "frame_count": frame_count
                    }
                else:
                    schema[anim_name]["frame_count"] += frame_count
        
        return schema
    
    def create_spritesheet(
        self, output_folder: Optional[str] = None, output_name: str = "spritesheet"
    ) -> Tuple[str, str]:
        """
        Generate and save spritesheet PNG and JSON schema.
        
        Args:
            output_folder: Folder to save files (defaults to current directory)
            output_name: Base filename without extension (default "spritesheet")
                        Will create {output_name}.png and {output_name}.json
        
        Returns:
            Tuple of (png_path, json_path)
        
        Raises:
            ValueError: If no sprites loaded or dimensions not set
        """
        if not self.sprites:
            raise ValueError("No sprites loaded. Add sprites before creating spritesheet.")
        if self.frame_width is None or self.frame_height is None:
            raise ValueError("Frame dimensions not set. This should not happen.")
        
        # Calculate layout
        output_rows, output_cols = self._calculate_layout()
        output_map = self._build_output_animation_map(output_rows, output_cols)
        
        # Create output image
        output_width = output_cols * self.frame_width
        output_height = output_rows * self.frame_height
        output_img = Image.new("RGBA", (output_width, output_height), (0, 0, 0, 0))
        
        print(f"\n[Stitcher] Packing {len(self.sprites)} sprites into grid...")
        print(f"  Layout: {output_rows}x{output_cols} ({output_width}x{output_height} pixels)")
        
        # Place sprites
        sprite_idx = 0
        for r in range(output_rows):
            for c in range(output_cols):
                if sprite_idx < len(self.sprites):
                    x = c * self.frame_width
                    y = r * self.frame_height
                    output_img.paste(self.sprites[sprite_idx], (x, y), self.sprites[sprite_idx])
                    sprite_idx += 1
        
        # Build animation schema
        animation_schema = self._build_animation_schema(output_map)
        
        # Determine output paths
        output_dir = Path(output_folder) if output_folder else Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        png_path = output_dir / f"{output_name}.png"
        json_path = output_dir / f"{output_name}.json"
        
        # Save PNG
        output_img.save(png_path, "PNG")
        print(f"  ✓ Sprite sheet saved: {png_path.resolve()}")
        
        # Build and save JSON
        json_data = {
            "image": f"{output_name}.png",
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "grid_width": output_cols,
            "animations": animation_schema,
        }
        
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)
        print(f"  ✓ Schema saved: {json_path.resolve()}")
        
        # Print summary
        print(f"\n[Stitcher] Summary:")
        print(f"  Animations: {len(animation_schema)}")
        for anim_name, anim_meta in animation_schema.items():
            print(f"    - {anim_name}: row {anim_meta['row']}, {anim_meta['frame_count']} frames")
        
        return str(png_path), str(json_path)
