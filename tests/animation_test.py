import os
import sys

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.animation import Animation


def main():
    """Main pygame application demonstrating Animation.from_spritesheet()."""
    pygame.init()
    
    # Screen setup
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Animation.from_spritesheet() Demo - LEFT/A: backward | RIGHT/D: forward | SPACE: run")
    clock = pygame.time.Clock()
    
    # Load animation from JSON metadata using the packed astronaut spritesheet
    json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'sprites', 'characters', 'tank.json')
    )
    
    walk_anim = Animation.from_json(
        json_path,
        'walk',  # animation name defined in astronaut.json
        base_frame_delay=0.1,
        verbose=True
    )
    print(f"\n✓ Successfully loaded astronaut walk animation from packed spritesheet: {json_path}\n")
    
    # Game state
    is_moving = False
    is_running = False
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Check for movement input
        keys = pygame.key.get_pressed()
        left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        # Handle movement direction
        if left_pressed and not right_pressed:
            is_moving = True
            walk_anim.set_direction(-1)  # Walking backward (left)
        elif right_pressed and not left_pressed:
            is_moving = True
            walk_anim.set_direction(1)  # Walking forward (right)
        else:
            # Both pressed, neither pressed, or other - stop movement
            is_moving = False
        
        # Check for running input (space bar)
        if keys[pygame.K_SPACE] and is_moving:
            is_running = True
            walk_anim.set_speed_multiplier(2.0)  # 2x speed
        else:
            is_running = False
            walk_anim.set_speed_multiplier(1.0)  # Normal speed
        
        # Advance animation frame when moving; reset to first frame when still
        if is_moving:
            walk_anim.update(dt)
        else:
            walk_anim.reset()
        
        # Draw
        screen.fill((50, 50, 50))  # Dark background
        
        # Draw current frame centered on screen
        scale = 2.5
        current_frame = walk_anim.get_current_frame()
        # Scale the sprite to 1.5x its original size
        scaled_frame = pygame.transform.scale(
            current_frame,
            (int(current_frame.get_width() * scale), int(current_frame.get_height() * scale))
        )
        frame_rect = scaled_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(scaled_frame, frame_rect)
        
        # Draw info text
        font = pygame.font.Font(None, 36)
        current_state = walk_anim.sm.current_state
        frame_num = current_state.value if hasattr(current_state.value, '__int__') else list(walk_anim.state_enum).index(current_state) + 1
        
        frame_text = font.render(f"Frame: {frame_num}/7", True, (255, 255, 255))
        direction_text = font.render(f"Direction: {'RIGHT' if walk_anim.direction == 1 else 'LEFT'}", True, (100, 200, 255))
        movement_text = font.render(f"Mode: {'RUNNING' if is_running else 'WALKING'}", True, (255, 200, 0) if is_running else (200, 200, 200))
        status_text = font.render("Moving: YES" if is_moving else "Moving: NO", True, (0, 255, 0) if is_moving else (255, 0, 0))
        
        screen.blit(frame_text, (10, 10))
        screen.blit(direction_text, (10, 50))
        screen.blit(movement_text, (10, 90))
        screen.blit(status_text, (10, 130))
        
        # Instructions
        small_font = pygame.font.Font(None, 22)
        instruct_text = small_font.render("LEFT/A: backward | RIGHT/D: forward | SPACE: run (2x speed) | ESC: quit", True, (200, 200, 200))
        screen.blit(instruct_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n✓ Animation demo closed")


if __name__ == "__main__":
    main()
