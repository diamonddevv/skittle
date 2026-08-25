import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle
import random

from skittle.camera import Camera

class Test(skittle.window.Window):

    URL: str = "https://scontent-man2-1.cdninstagram.com/v/t51.82787-15/732663393_18078637844670346_2825249175333996486_n.webp?_nc_cat=111&ig_cache_key=MzkzMTA3OTMyMDE4ODQ1NzY1OQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=6ac--z8--C8Q7kNvwHCnNHS&_nc_oc=Adr6nO24lg9jtA1iqy4DofGIc4pEQHlIgINCljpe1pHTJiUw5HSCjYh23Uox_EbfkM_IafcN_NOOLEVEmLG0LuSY&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-man2-1.cdninstagram.com&_nc_gid=kYchdlGzKUBJLExcIS-ekQ&_nc_ss=7a22e&oh=00_AQH4AblO-CQyfzArx__ZtEAJ30y2hXf7KcxLpP6_rEIftA&oe=6A9217BD"

    def __init__(self) -> None:
        super().__init__(None, "test", 1280, 720, target_fps=0, fps_in_title=True)
        self.age = 0.0

        self.hearts = skittle.resource.spritesheet("tests/asset/spritesheet.png")

        self.glyphxel = skittle.render.TextRenderer.from_json(self.ctx, "tests/asset/glyphxel_definition.json")

        self.heart_mesh = skittle.render.mesh.SpritesheetMesh(self.ctx, self.hearts)
        self.many_hearts = skittle.render.mesh.InstancedSpritesheetMesh(self.ctx, self.hearts)


        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.sprite_idx_x = 0
        self.sprite_idx_y = 0

        allowed_cells: list[tuple[int, int]] = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), 
            (0, 1), (1, 1), (2, 1), 
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),                 (7, 2), 
            (0, 3), (1, 3), (2, 3), (3, 3),                         (7, 3), 
            (0, 4), (1, 4), (2, 4), (3, 4),                         (7, 4), 
            (0, 5), (1, 5), (2, 5), (3, 5), (4, 5),                 (7, 5), 
            (0, 6), (1, 6), (2, 6),                         (6, 6), (7, 6), 
            (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), 
        ]
        self.many_hearts.bake_instances([
            skittle.render.RenderInstance(
                glm.vec2(x * 12 * 8, -y * 8 * 8), 
                random.choice(allowed_cells), 
                skittle.color.WHITE, 
                0, 
                glm.vec2(8, 8)
                ) 
            for x in range(100) for y in range(50)
            ])
        
        self.coltest_rect = skittle.math.Rect(
            -200, -200,
            180, 80
        )

        self.post_processor.add(skittle.render.PostProcessEffect.from_json(self.ctx, "tests/asset/postprocess/crt.json"))
        self.post_processor.add(skittle.render.PostProcessEffect.from_json(self.ctx, "tests/asset/postprocess/green.json"))
        self.post_processor.set_active("crt", False)
        self.post_processor.set_active("green", True)

        
        skittle.audio.load_sound("scotland", "tests/asset/sound/SCOTLAND.wav")
        skittle.audio.play_sound("scotland")

        self.tilemap = skittle.resource.Tilemap.from_json(self.ctx, "tests/asset/tilemap/map.json")
        self.tilemap.bake()


    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):

        self.glyphxel.render(camera, f"instances: {self.many_hearts._render_instances}\nframerate: {self._clock.get_fps():.0f} fps", glm.vec2(0, -100), scale=5)

        self.many_hearts.render(camera, position=glm.vec2(0, 100))

        skittle.draw.rect(ctx, camera, self.coltest_rect, skittle.color.GREEN if self.coltest_rect.collides_point(skittle.input.get_world_mouse_pos(camera, overlay=False)) else skittle.color.RED, filled=True, overlay=False)

        self.tilemap.render(camera, glm.vec2(-1200, 200))
    

    def update(self, dt: float, camera: Camera):
        self.age += dt

        #for i in self.many_hearts.indexes():
        #    self.many_hearts.update_instance(i, lambda old: (old[0], old[1], old[2], old[3], old[4], old[5] + dt * glm.quarter_pi() * 5 * glm.sin(hash(str(i))), old[6]))

        if skittle.input.keys_click()[skittle.input.KEY_SPACE]:
            skittle.audio.play_sound('scotland', pitch=random.uniform(0.9, 1.1))
            self.post_processor.toggle_active("crt")

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