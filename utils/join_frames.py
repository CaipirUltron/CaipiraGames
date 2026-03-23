"""
Image Stitcher - Join multiple image frames into a single spritesheet.

This utility combines multiple numbered image files (1.png, 2.png, etc.)
from a folder into a single spritesheet image. Useful for animation frames.

Supports two layout modes:
- ROW: Arrange frames horizontally (left to right)
- COLUMN: Arrange frames vertically (top to bottom)

Usage:
    Direct usage:
        stitch = JoinFrames(input_dir="assets/sprites/enemy/walk", mode="ROW")
        stitch.create_spritesheet(output_path="spritesheet.png")
    
    Command-line:
        python join_frames.py assets/sprites/enemy/walk --mode ROW --output spritesheet.png
        python join_frames.py assets/sprites/enemy/walk --mode COLUMN --output spritesheet.png
        python join_frames.py assets/sprites/enemy/walk  # Defaults to ROW, auto output
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
import argparse

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow (PIL) is required. Install with: pip install Pillow")


class JoinFrames:
    """
    Combines multiple image files into a single spritesheet.
    
    Attributes:
        input_dir (str): Directory containing numbered image files
        mode (str): Layout mode - "ROW" (horizontal) or "COLUMN" (vertical)
        padding (int): Padding between frames in pixels (default 0)
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    def __init__(self, input_dir: str, mode: str = "ROW", padding: int = 0):
        """
        Initialize JoinFrames.
        
        Args:
            input_dir: Directory containing numbered image files (1.png, 2.png, etc.)
            mode: Layout mode - "ROW" (left to right) or "COLUMN" (top to bottom)
            padding: Padding between frames in pixels (default 0)
        
        Raises:
            ValueError: If mode is invalid
            FileNotFoundError: If input directory doesn't exist
        """
        if mode not in ("ROW", "COLUMN"):
            raise ValueError(f"Mode must be 'ROW' or 'COLUMN', got '{mode}'")
        
        if not os.path.isdir(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        self.input_dir = Path(input_dir)
        self.mode = mode.upper()
        self.padding = max(0, padding)
        self.images: List[Image.Image] = []
        self.frames_loaded = 0
    
    def _load_images(self) -> None:
        """Load and sort numbered image files from input directory."""
        images_dict = {}
        
        # Find all supported image files
        for format_ext in self.SUPPORTED_FORMATS:
            pattern = f"*{format_ext}"
            for file_path in self.input_dir.glob(pattern):
                # Try to extract number from filename (e.g., "1.png" -> 1)
                try:
                    name_without_ext = file_path.stem
                    # Handle cases like "1", "1-" at start, or "frame_1"
                    frame_num = int(''.join(filter(str.isdigit, name_without_ext.split('_')[-1])))
                    images_dict[frame_num] = file_path
                except (ValueError, IndexError):
                    # Skip files that don't have a numeric component
                    pass
        
        if not images_dict:
            raise FileNotFoundError(
                f"No numbered image files found in {self.input_dir}\n"
                f"Expected files like: 1.png, 2.png, 3.png, etc.\n"
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Sort by frame number and load
        print(f"[JoinFrames] Found {len(images_dict)} images")
        for frame_num in sorted(images_dict.keys()):
            file_path = images_dict[frame_num]
            try:
                img = Image.open(file_path)
                self.images.append(img)
                print(f"  ✓ Loaded {file_path.name} (frame {frame_num})")
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {e}")
                raise
        
        self.frames_loaded = len(self.images)
        print(f"[JoinFrames] Successfully loaded {self.frames_loaded} images")
    
    def _calculate_dimensions(self) -> Tuple[int, int]:
        """
        Calculate spritesheet dimensions based on mode and images.
        
        Returns:
            Tuple of (width, height) for the output spritesheet
        """
        if not self.images:
            raise ValueError("No images loaded. Call _load_images() first.")
        
        # Assume all images have same dimensions (get from first image)
        frame_width, frame_height = self.images[0].size
        num_frames = len(self.images)
        
        if self.mode == "ROW":
            # Horizontal layout: all frames in one row
            width = num_frames * frame_width + (num_frames - 1) * self.padding
            height = frame_height
        else:  # COLUMN
            # Vertical layout: all frames in one column
            width = frame_width
            height = num_frames * frame_height + (num_frames - 1) * self.padding
        
        return width, height
    
    def create_spritesheet(
        self,
        output_path: Optional[str] = None,
        bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
    ) -> str:
        """
        Create and save the spritesheet.
        
        Args:
            output_path: Path to save spritesheet. If None, auto-generates name
                        in current directory: "spritesheet_ROW.png" or "spritesheet_COLUMN.png"
            bg_color: Background color as RGBA tuple (default transparent)
        
        Returns:
            Path to created spritesheet file
        
        Raises:
            ValueError: If no images loaded
        """
        # Load images if not already done
        if not self.images:
            self._load_images()
        
        # Calculate dimensions
        width, height = self._calculate_dimensions()
        frame_width, frame_height = self.images[0].size
        
        # Create output image with transparent background
        spritesheet = Image.new("RGBA", (width, height), bg_color)
        
        print(f"\n[JoinFrames] Creating spritesheet...")
        print(f"  Layout: {self.mode}")
        print(f"  Size: {width}x{height} pixels")
        print(f"  Frames: {len(self.images)}")
        
        # Paste frames into spritesheet
        if self.mode == "ROW":
            # Horizontal layout
            x_offset = 0
            for i, img in enumerate(self.images):
                spritesheet.paste(img, (x_offset, 0), img if img.mode == "RGBA" else None)
                x_offset += frame_width + self.padding
        else:  # COLUMN
            # Vertical layout
            y_offset = 0
            for i, img in enumerate(self.images):
                spritesheet.paste(img, (0, y_offset), img if img.mode == "RGBA" else None)
                y_offset += frame_height + self.padding
        
        # Determine output path
        if output_path is None:
            # Auto-generate filename in input directory
            output_path = self.input_dir / f"spritesheet_{self.mode}.png"
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save spritesheet
        spritesheet.save(output_path, "PNG")
        print(f"  ✓ Saved to: {output_path.resolve()}")
        
        return str(output_path)
    
    def get_frame_info(self) -> dict:
        """
        Get information about the loaded frames and output spritesheet.
        
        Returns:
            Dict containing frame dimensions, count, and layout info
        """
        if not self.images:
            return {}
        
        frame_width, frame_height = self.images[0].size
        width, height = self._calculate_dimensions()
        
        return {
            "mode": self.mode,
            "frame_count": len(self.images),
            "frame_width": frame_width,
            "frame_height": frame_height,
            "spritesheet_width": width,
            "spritesheet_height": height,
            "padding": self.padding,
        }


def main():
    """CLI interface for JoinFrames."""
    parser = argparse.ArgumentParser(
        description="Join multiple numbered image files into a single spritesheet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python join_frames.py assets/sprites/enemy/walk
  python join_frames.py assets/sprites/enemy/walk --mode COLUMN
  python join_frames.py assets/sprites/player/run --output player_run.png --mode ROW
  python join_frames.py assets/effects/explosion --padding 2 --output explosion_spritesheet.png
        """
    )
    
    parser.add_argument(
        "input_dir",
        help="Input directory containing numbered image files (1.png, 2.png, etc.)"
    )
    parser.add_argument(
        "--mode",
        choices=["ROW", "COLUMN"],
        default="ROW",
        help="Layout mode: ROW (horizontal) or COLUMN (vertical) [default: ROW]"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output spritesheet path [default: spritesheet_<MODE>.png]"
    )
    parser.add_argument(
        "--padding", "-p",
        type=int,
        default=0,
        help="Padding between frames in pixels [default: 0]"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print frame information without creating spritesheet"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"[JoinFrames] Loading images from: {args.input_dir}\n")
        
        # Create stitcher
        stitcher = JoinFrames(
            input_dir=args.input_dir,
            mode=args.mode,
            padding=args.padding
        )
        
        # Load images
        stitcher._load_images()
        
        # Print info if requested
        if args.info:
            info = stitcher.get_frame_info()
            print("\n[JoinFrames] Frame Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            return
        
        # Create spritesheet
        output_file = stitcher.create_spritesheet(output_path=args.output)
        
        # Print summary
        info = stitcher.get_frame_info()
        print(f"\n[JoinFrames] Summary:")
        print(f"  Input: {args.input_dir}")
        print(f"  Output: {output_file}")
        print(f"  Frames: {info['frame_count']}")
        print(f"  Layout: {info['mode']}")
        print(f"  Spritesheet size: {info['spritesheet_width']}x{info['spritesheet_height']}")
        print(f"\n[✓] Spritesheet created successfully!")
        
    except Exception as e:
        print(f"\n[✗] Error: {e}", flush=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
