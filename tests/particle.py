import _ctx

from pyglm import glm
import moderngl
import skittle
import pygame


class Scene(skittle.scene.Scene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, ctx: moderngl.Context, camera: skittle.render.Camera) -> None:
        super().__init__(scene_manager, ctx, camera)

        self.text_renderer = skittle.render.TextRenderer.from_json(ctx, "tests/asset/glyphxel_definition.json")
        self.spritesheet = skittle.resource.spritesheet("tests/asset/spritesheet.png")
        self.particle = skittle.render.ParticleEmitter(
            glm.vec2(0), 
            3, 
            skittle.Color('red'), 
            32, -glm.pi()/2, 5, 0, 
            skittle.render.MultiInstanceSpritesheetQuad(
                ctx, self.spritesheet
            ), (0, 0))

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.particle.draw(camera)

    def update(self, dt: float):
        self.particle.emit(variance=1)
        self.particle.update(dt)


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