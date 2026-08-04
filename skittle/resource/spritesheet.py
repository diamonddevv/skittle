import pygame
import moderngl

class Spritesheet():
    def __init__(self, 
                 surface: pygame.Surface,
                 sprite_w: int = 16,
                 sprite_h: int = 16,
                 seperation_x: int = 0,
                 seperation_y: int = 0
                 ) -> None:
        self.surface = surface
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h
        self.seperation_x = seperation_x
        self.seperation_y = seperation_y


    def uv(self, cell_x: int, cell_y: int) -> tuple[float, float, float, float]:
        sheet_w, sheet_h = self.surface.size
        px_step_x = 1 / sheet_w
        px_step_y = 1 / sheet_h

        px_tl_x = cell_x * (self.sprite_w + self.seperation_x)
        px_tl_y = cell_y * (self.sprite_h + self.seperation_y)

        u0 = px_step_x * px_tl_x
        v0 = px_step_y * px_tl_y
        u1 = u0 + px_step_x * self.sprite_w
        v1 = v0 + px_step_y * self.sprite_h

        return u0, v0, u1, v1
