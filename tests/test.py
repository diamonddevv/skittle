import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle
import random

from skittle.camera import Camera

class Test(skittle.window.Window):
    def __init__(self) -> None:
        super().__init__(None, "test", 500, 500, target_fps=0, fps_in_title=True)
        
        self.hearts = skittle.resource.spritesheet("tests/asset/spritesheet.png")
        self.glyphxel = skittle.render.TextRenderer.from_json(self.ctx, "tests/asset/glyphxel_definition.json")

        self.heart_mesh = skittle.render.mesh.SpritesheetMesh(self.ctx, self.hearts)
        self.many_hearts = skittle.render.mesh.InstancedSpritesheetMesh(self.ctx, self.hearts)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.sprite_idx_x = 0
        self.sprite_idx_y = 0

        self.many_hearts.bake_instances([(x * 16, y * 16, random.randint(0, 2), random.randint(0, 7), skittle.color.WHITE, random.uniform(0, glm.two_pi()), glm.vec2(random.uniform(1/2, 2))) for x in range(500) for y in range(250)])


    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        

        self.glyphxel.render(camera, "hello, world!", glm.vec2(0, 0))
        self.glyphxel.render(camera, "scaled", glm.vec2(0, 100), scale=2)
        self.glyphxel.render(camera, "fixed", glm.vec2(20, 20), overlay=True, color=skittle.color.CYAN)

        self.heart_mesh.render(camera, position=glm.vec2(0, 0))
        self.many_hearts.render(camera, position=glm.vec2(100, 100))

    def update(self, dt: float, camera: Camera):
        if skittle.input.keys_click()[skittle.input.KEY_SPACE]:
            self.heart_mesh.set_sprite((3, 0) if self.heart_mesh.frame == (0, 0) else (0, 0))

    def handle_zoom(self, event: pygame.Event):
        if event.y == 0:
            return
        self.camera.zoom *= (1.1 if event.y > 0 else 0.9)

    def handle_pan(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # i dont know why pygame doesnt expose constants for the mouse buttons?
                self.panning = True
                self.last_mouse_pos = event.pos
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False

        if event.type == pygame.MOUSEMOTION:
            if self.panning:
                current_pos = glm.vec2(event.pos)
                delta = (current_pos - self.last_mouse_pos) / self.camera.zoom
                self.camera.move(*delta)
                self.last_mouse_pos = current_pos

if __name__ == "__main__":
    wnd = Test()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()