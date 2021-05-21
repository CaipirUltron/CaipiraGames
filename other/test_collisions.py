import math

import pygame as pg
import pymunk as pm
from pymunk import Vec2d


def flipy(p):
    """Convert chipmunk coordinates to pygame coordinates."""
    return Vec2d(p[0], -p[1]+600)


class GameObject(pg.sprite.Sprite):
    """A sprite with an attached physics body."""

    def __init__(self, pos, space):
        super().__init__()
        self.image = pg.Surface((80, 70), pg.SRCALPHA)
        offset = Vec2d(80/2, 70/2)  # Offset for poly drawing below.
        self.orig_image = self.image
        self.rect = self.image.get_rect(topleft=pos)

        self.space = space

        self.body = pm.Body(0, 0)
        # Attach the sprite to the body, so that we can access it later.
        self.body.sprite = self
        self.body.position = pos
        self.space.add(self.body)
        # Add 2 shapes to the body.
        # Vertices of the shapes.
        vertices = (
            [(-25, 14), (0, 24), (0, 0), (30, 0), (30, -20), (0, -20)],
            [(20, 34), (40, 24), (10, 0), (-10, 0)],
            )
        for verts in vertices:
            shape = pm.Poly(self.body, verts, radius=.1)
            shape.density = 1
            shape.friction = .9
            self.space.add(shape)
            # Need to transform the verts before they can
            # be used to draw a poly on self.image.
            verts2 = [vert.rotated(self.body.angle) + offset
                      for vert in shape.get_vertices()]
            verts2 = [(x, -y+70) for x, y in verts2]
            pg.draw.polygon(self.image, (60, 80, 140), verts2)

    def update(self, dt):
        # Synchronize the position of the sprite rect and Pymunk body.
        self.rect.center = flipy(self.body.position)
        # Rotate the image.
        self.image = pg.transform.rotate(
            self.orig_image, math.degrees(self.body.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.bottom > 560:  # Off-screen.
            self.space.remove(self.body, self.body.shapes)
            self.kill()


class Game:

    def __init__(self):
        self.fps = 30
        self.done = False
        self.green = pg.Color('springgreen')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((800, 600))
        self.all_sprites = pg.sprite.Group()

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, -900.0)
        # A static body platform.
        body = pm.Body(0, 0, pm.Body.STATIC)
        verts = [[150, 100], [650, 100], [650, 200], [150, 200]]
        poly = pm.Poly(body, verts, radius=.1)
        poly.friction = 0.5
        self.space.add(body, poly)

        self.shape_filter = pm.ShapeFilter()

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(self.fps) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()
            self.current_fps = self.clock.get_fps()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left button adds GameObjects.
                    self.all_sprites.add(
                        GameObject(flipy(event.pos), self.space))
                elif event.button == 3:  # Right button.
                    # Remove the body and shapes under
                    # the mouse cursor.
                    query = self.space.point_query(
                        flipy(pg.mouse.get_pos()), 0.0, self.shape_filter)
                    for info in query:
                        body = info.shape.body
                        # Don't remove the platform.
                        if hasattr(body, 'sprite'):
                            try:
                                self.space.remove(body, body.shapes)
                                body.sprite.kill()
                            except KeyError:
                                pass

    def run_logic(self):
        self.space.step(1/60)
        self.all_sprites.update(self.dt)

    def draw(self):
        self.screen.fill((166, 166, 150))
        # Platform rect.
        pg.draw.rect(self.screen, (120, 130, 110), (150, 400, 500, 100))
        self.all_sprites.draw(self.screen)

        # Draw the outlines of the shapes.
        for shape in self.space.shapes:
            pts = [flipy(pos.rotated(shape.body.angle) + shape.body.position)
                   for pos in shape.get_vertices()]
            pg.draw.lines(self.screen, self.green, True, pts, 1)

        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    Game().run()
    pg.quit()