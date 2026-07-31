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
            64, 
            [skittle.color.Color('white')], 
            1, 4,
            8, 16,
            0, glm.two_pi(),
            1/2, 2,
            skittle.render.MultiInstanceSpritesheetQuad(
                ctx, self.spritesheet
            ),
            [(i,0) for i in range(6)],
            max_particles=256)
        
        self.item = skittle.render.SpritesheetQuad(ctx, self.spritesheet, frame=(0, 4))
        self.item.scale = 2

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        ctx.clear(1.0, 1.0, 1.0)
        self.text_renderer.render(camera, f"fps: {self.scene_manager.window._clock.get_fps():.0f}\nparticles: {len(self.particle._particles)}", glm.vec2(20, 20), color=skittle.color.BLACK, overlay=True)
        self.particle.draw(camera)

        self.item.render(camera)

        skittle.input.get_world_mouse_pos(camera)

    def update(self, dt: float, camera: skittle.render.Camera):
        self.particle.emit()
        self.particle.update(dt)

        self.item.position = skittle.input.get_world_mouse_pos(camera)


class test_ParticlesAndPostProcessing(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(Scene, "particles", 1280, 720, fps_in_title=True)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.crt = skittle.render.PostProcessEffect.from_json(self.ctx, "tests/asset/postprocess/crt.json")
        self.post_processor.add(self.crt)

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
    wnd = test_ParticlesAndPostProcessing()
    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)
    wnd.run()