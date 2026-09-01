import _ctx

from pyglm import glm
import moderngl
import pygame
import skittle
import random

from skittle.camera import Camera

class Test(skittle.window.Window):

    URL: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Cat_demonstrating_static_cling_with_styrofoam_peanuts.jpg/330px-Cat_demonstrating_static_cling_with_styrofoam_peanuts.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail"

    def __init__(self) -> None:
        super().__init__(None, "test", target_fps=60, fps_in_title=True)
        self.age = 0.0

        self.hearts = skittle.resource.spritesheet("tests/asset/spritesheet.png")

        self.glyphxel = skittle.render.TextRenderer.from_json(self.ctx, "tests/asset/glyphxel_definition.json")

        self.heart_mesh = skittle.render.mesh.SpritesheetMesh(self.ctx, self.hearts)
        self.many_hearts = skittle.render.mesh.InstancedSpritesheetMesh(self.ctx, self.hearts)

        self.electrostatics_cat = skittle.render.texture(self.ctx, skittle.resource.image_from_url(Test.URL, "fynndiamond@gmail.com"))

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

        self.post_processor.add(skittle.resource.postprocessor(self.ctx, "tests/asset/postprocess/crt.json"))
        self.post_processor.set_active("crt", False)

        
        skittle.audio.load_sound("scotland", "tests/asset/sound/SCOTLAND.wav")
        skittle.audio.play_sound("scotland")

        self.tilemap = skittle.resource.tilemap(self.ctx, "tests/asset/tilemap/map.json")
        self.tilemap.bake()


        self.phys_world = skittle.physics.PhysicsWorld()

        self.wall_bb = skittle.physics.PhysicsObject(50, 100, "wall", self, 300, -500, static=True)

        self.physball = Physball(size=10)
        self.physball.physobj.try_move(glm.vec2(800, -500))

        self.phys_world.track(self.wall_bb)
        self.phys_world.track(self.physball.physobj)

        self.tween_pos = glm.vec2(500, -1000)


    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        self.ctx.clear(1, 0.6, 0.2, 1)

        self.glyphxel.render(camera, f"instances: {self.many_hearts._render_instances}\nframerate: {self._clock.get_fps():.0f} fps", glm.vec2(0, -100), scale=5)

        self.many_hearts.render(camera, position=glm.vec2(0, 100))

        skittle.draw.rect(ctx, camera, self.coltest_rect, 
                          skittle.color.GREEN if self.coltest_rect.collides_point(skittle.input.get_world_mouse_pos(camera, overlay=False)) else skittle.color.RED, 
                          overlay=False)

        self.tilemap.render(camera, glm.vec2(-1200, 200))

        skittle.draw.circle(ctx, camera, skittle.input.get_world_mouse_pos(camera), 10, skittle.color.YELLOW)
        skittle.draw.circle(ctx, camera, skittle.input.get_world_mouse_pos(camera, True), 6, skittle.color.CYAN, layer=2, overlay=True)

        self.wall_bb._render_bounding_box(ctx, camera)
        self.physball.draw(ctx, camera)

        skittle.draw.circle(ctx, camera, self.tween_pos, 12, skittle.color.BLACK)


        self.electrostatics_cat.render(camera, glm.vec2(-800, 500))
    

    def update(self, dt: float, camera: Camera):
        self.age += dt

        self.physball.update(dt, camera)

        #for i in self.many_hearts.indexes():
        #    self.many_hearts.update_instance(i, lambda old: (old[0], old[1], old[2], old[3], old[4], old[5] + dt * glm.quarter_pi() * 5 * glm.sin(hash(str(i))), old[6]))

        keyclick = skittle.input.keys_click()
        if keyclick[skittle.input.KEY_SPACE]: skittle.audio.play_sound('scotland', pitch=random.uniform(0.9, 1.1))
        if keyclick[skittle.input.KEY_s]: self.post_processor.toggle_active("crt")
        if keyclick[skittle.input.KEY_t]: skittle.tween.tween(self.tween_pos, self, "tween_pos", 3, self.tween_pos + glm.vec2(-1400, 500), skittle.tween.EASE_LINEAR)

        self.phys_world.update(dt)
        skittle.tween.update_tweens(dt)

        self.electrostatics_cat._color_overlay = skittle.color.Color(255, 255, 255, int((glm.sin(self.age) + 1) / 2 * 255))

        
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


class Physball():
    def __init__(self, size: float = 20) -> None:
        self.size = size
        self.pos = glm.vec2()
        self.physobj = skittle.physics.PhysicsObject(size*2, size*2, "physball", self, report_only=False)
        self.physobj.collision_signal.bind(self.on_collide)

        self.speed = 80
        self.accel = 10

    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        skittle.draw.circle(ctx, camera, self.physobj.get_confirmed_pos(), self.size, skittle.color.GREEN)
        self.physobj._render_bounding_box(ctx, camera)

    def update(self, dt: float, camera: skittle.camera.Camera):
        self.pos = self.physobj.get_confirmed_pos()

        self.physobj.try_move(self.pos + glm.vec2(-1, 0) * self.speed * dt)
        #self.physobj.try_move(skittle.input.get_world_mouse_pos(camera))

    def on_collide(self, other: skittle.physics.PhysicsObject):
        print(f"hit: {other._id} and i am {self.physobj._id}")

if __name__ == "__main__":
    wnd = Test()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()