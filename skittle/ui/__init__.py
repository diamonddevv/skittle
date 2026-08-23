import skittle
import pygame


class Manager():
    def __init__(self) -> None:
        self._elements: list[Element] = []

class Element():
    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        self.rect = skittle.math.Rect(x, y, w, h)
        self.mouse_over = False
        self.collision_layer = 0

    def draw(self, camera: skittle.camera.Camera):
        pass

    def update(self, dt: float, camera: skittle.camera.Camera):
        self._update_collision(camera)

    def click(self):
        pass

    def click_outside(self):
        pass

    def _update_collision(self, camera: skittle.camera.Camera):
        click = pygame.mouse.get_just_pressed()[0]
        self.mouse_over = self.rect.collides_point(skittle.input.get_world_mouse_pos(camera))
        if self.mouse_over and click:
            self.click()
        if not self.mouse_over and click:
            self.click_outside()