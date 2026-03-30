import os
import sys

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.animation import SpriteAnimation


def main():
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    GAME_FPS = 60
    ANIM_FPS = 10

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Animation Demo - LEFT/A: backward | RIGHT/D: forward | SPACE: run | ESC: quit")
    clock = pygame.time.Clock()

    json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'assets', 'sprites', 'characters', 'tank.json')
    )

    animations = SpriteAnimation.from_json(json_path, fps=ANIM_FPS)
    walk_anim = next(a for a in animations if a.name == 'walk')
    print(f"✓ Loaded {len(animations)} animation(s) from {json_path}")

    is_moving = False
    was_playing = False

    running = True
    while running:
        clock.tick(GAME_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        was_moving = is_moving

        if left and not right:
            is_moving = True
            walk_anim.flip(True)
        elif right and not left:
            is_moving = True
            walk_anim.flip(False)
        else:
            is_moving = False

        if not is_moving and was_moving:
            walk_anim.reset()

        if is_moving and not was_playing:
            walk_anim.start()
        elif not is_moving and was_playing:
            walk_anim.stop()
        was_playing = is_moving

        walk_anim.update()

        is_running = keys[pygame.K_SPACE] and is_moving
        walk_anim.set_fps(ANIM_FPS * 2 if is_running else ANIM_FPS)

        # Draw
        screen.fill((50, 50, 50))

        scale = 2.5
        current_frame = walk_anim.get_current_frame()
        scaled_frame = pygame.transform.scale(
            current_frame,
            (int(current_frame.get_width() * scale), int(current_frame.get_height() * scale))
        )
        screen.blit(scaled_frame, scaled_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        font = pygame.font.Font(None, 36)
        frame_num = walk_anim.sm.current_state

        screen.blit(font.render(f"Frame: {frame_num + 1}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Direction: {'LEFT' if walk_anim._flipped else 'RIGHT'}", True, (100, 200, 255)), (10, 50))
        screen.blit(font.render(f"Mode: {'RUNNING' if is_running else 'WALKING'}", True, (255, 200, 0) if is_running else (200, 200, 200)), (10, 90))
        screen.blit(font.render("Moving: YES" if is_moving else "Moving: NO", True, (0, 255, 0) if is_moving else (255, 0, 0)), (10, 130))

        small_font = pygame.font.Font(None, 22)
        screen.blit(small_font.render("LEFT/A: backward | RIGHT/D: forward | SPACE: run (2x speed) | ESC: quit", True, (200, 200, 200)), (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    walk_anim.stop()
    pygame.quit()
    print("✓ Animation demo closed")


if __name__ == "__main__":
    main()

