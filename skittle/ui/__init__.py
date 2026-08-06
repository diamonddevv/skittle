import skittle
import pygame


class Manager():
    def __init__(self) -> None:
        self._elements: list[Element] = []

class Element():
    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        self.rect = pygame.Rect(x, y, w, h)
        self.mouse_over = False
        self.collision_layer = 0

    def draw(self, camera: skittle.camera.Camera):
        pass

    def update(self, dt: float, camera: skittle.camera.Camera):
        self._update_collision()

    def click(self):
        pass

    def click_outside(self):
        pass

    def _update_collision(self):
        click = pygame.mouse.get_just_pressed()[0]
        self.mouse_over = skittle.input.get_mouse_over(self.rect, self.collision_layer)
        if self.mouse_over and click:
            self.click()
        if not self.mouse_over and click:
            self.click_outside()