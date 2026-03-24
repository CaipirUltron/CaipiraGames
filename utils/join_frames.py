"""
Spritesheet Stitcher - Combine sprites and spritesheets into single character sheets.

For usage examples, see the __main__ section below.
"""

from stitcher import Stitcher
from pathlib import Path

__all__ = ["Stitcher"]


def stitch_spritesheets():
    """
    Combine all astronaut_*.png spritesheets into a single astronaut.png
    with corresponding astronaut.json animation schema.
    
    Edit the animation_matrix configuration below to define how sprites
    are mapped to animations.
    """
    stitcher = Stitcher()
    
    # Load all astronaut spritesheets
    astronaut_sheets = [
        ("assets/sprites/characters/astronaut_idle.png", "idle", 3),
        ("assets/sprites/characters/astronaut_walk.png", "walk", 10),
        ("assets/sprites/characters/astronaut_jump.png", "jump", 6),
        ("assets/sprites/characters/astronaut_duck.png", "duck", 1),
        ("assets/sprites/characters/astronaut_stand.png", "stand", 4),
        ("assets/sprites/characters/astronaut_hurt.png", "hurt", 2),
        ("assets/sprites/characters/astronaut_cling.png", "cling", 1),
        ("assets/sprites/characters/astronaut_shoot_up.png", "shoot_up", 1),
        ("assets/sprites/characters/astronaut_shoot_walk.png", "shoot_walk", 10),
    ]
    
    for sheet_path, anim_name, columns in astronaut_sheets:
        if not Path(sheet_path).exists():
            print(f"  ⊘ {sheet_path} not found, skipping...")
            continue
        try:
            # Placeholder: Adjust rows, cols, and animation_matrix as needed
            stitcher.add_spritesheet(sheet_path, rows=1, cols=columns, animation_matrix=anim_name)
            print(f"[Config needed] {sheet_path}")
        except Exception as e:
            print(f"  ✗ Error loading {sheet_path}: {e}")
    
    # TODO: Set layout constraints if desired
    stitcher.set_max_width(8)
    
    # Generate output with custom filename
    png_path, json_path = stitcher.create_spritesheet(
        output_folder="assets/sprites/characters/",
        output_name="astronaut"
    )
    print(f"[✓] Astronaut spritesheet created: {png_path}")
    print(f"[✓] Schema saved: {json_path}")


if __name__ == "__main__":
    print(__doc__)
    print("\n[Example] Stitching astronaut spritesheets...\n")
    stitch_spritesheets()
