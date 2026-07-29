import _ctx

from pyglm import glm
import moderngl
import skittle
import pygame

class BlockParticle(skittle.render.ParticleMesh):
    FRAGMENT: str = """
#version 330 core

in vec2 v_uv;
out vec4 fragColor;

uniform vec4 u_tint;
uniform sampler2D u_texture;

void main() {
    fragColor = u_tint;
}
"""

    def __init__(self, ctx: moderngl.Context) -> None:
        super().__init__(
            ctx, skittle.render.Mesh.VERTEX, BlockParticle.FRAGMENT, "", ("", ), 0)

class Scene(skittle.scene.Scene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, ctx: moderngl.Context, camera: skittle.render.Camera) -> None:
        super().__init__(scene_manager, ctx, camera)

        self.text_renderer = skittle.render.TextRenderer.from_json(ctx, "tests/asset/glyphxel_definition.json")
        self.particle = skittle.render.Particle(glm.vec2(0), 3, skittle.Color('red'), 1, 0, 5, 0, BlockParticle(ctx))

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        pass


class test_Particles(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(Scene, "particles", 500, 500, fps_in_title=True)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

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
    wnd = test_Particles()
    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)
    wnd.run()