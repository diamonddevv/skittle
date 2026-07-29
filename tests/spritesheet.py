import _ctx

from pyglm import glm
import math
import moderngl
import pygame
import skittle

class test_Spritesheet(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "spritesheet", 500, 500, fps_in_title=True)
        
        self.spritesheet = skittle.resource.spritesheet("tests/asset/spritesheet.png")
        self.quad = skittle.render.SpritesheetQuad(self.ctx, self.spritesheet)

        self.panning = False
        self.last_mouse_pos = glm.vec2()

        self.sprite_idx_x = 0
        self.sprite_idx_y = 0
        self.age = 0.0

    def update(self, dt: float):
        self.age += dt

        just_pressed = pygame.key.get_just_pressed()

        if just_pressed[pygame.K_UP]: self.sprite_idx_y -= 1
        if just_pressed[pygame.K_DOWN]: self.sprite_idx_y += 1
        if just_pressed[pygame.K_LEFT]: self.sprite_idx_x -= 1
        if just_pressed[pygame.K_RIGHT]: self.sprite_idx_x += 1

        if self.sprite_idx_x >= 8:
            self.sprite_idx_x = 0
        elif self.sprite_idx_x < 0:
            self.sprite_idx_x = 7

        if self.sprite_idx_y >= 8:
            self.sprite_idx_y = 0
        elif self.sprite_idx_y < 0:
            self.sprite_idx_y = 7

        self.quad.set_sprite((self.sprite_idx_x, self.sprite_idx_y))
        self.quad.rotation_radians += .75 * math.pi * dt;
        self.quad.scale = math.sin(self.age) * 2 + 5

        

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.ctx.clear(1,1,1)
        self.quad.render(camera)

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
    wnd = test_Spritesheet()

    skittle.bind_pygame_event_handler(wnd.handle_zoom, pygame.MOUSEWHEEL)
    skittle.bind_pygame_event_handler(wnd.handle_pan, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION)

    wnd.run()