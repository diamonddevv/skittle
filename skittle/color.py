import skittle
import pygame
import moderngl

class Color():
    """
    represent colors
    """

    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.r = skittle.math.clamp(r, 0, 255)
        self.g = skittle.math.clamp(g, 0, 255)
        self.b = skittle.math.clamp(b, 0, 255)
        self.a = skittle.math.clamp(a, 0, 255)

    @staticmethod
    def from_pygame(color: pygame.Color) -> Color:
        return Color(color.r, color.g, color.b, color.a)

    @staticmethod
    def from_hex(hex: str) -> Color:
        return Color.from_pygame(pygame.Color.from_hex(hex))

    @staticmethod
    def from_int(hex: int) -> Color:
        return Color.from_pygame(pygame.color.Color(hex))

    @staticmethod
    def from_normalised(normalised: tuple[float, float, float, float]) -> Color:
        return Color.from_pygame(pygame.Color.from_normalized(normalised))

    def normalised(self) -> tuple[float, float, float, float]:
        return pygame.Color(self.r, self.g, self.b, self.a).normalize()

    def darken(self, factor: float) -> Color:
        return Color(
            round(self.r * (1 - factor)),
            round(self.g * (1 - factor)),
            round(self.b * (1 - factor)),
            self.a
        )


    def clear_context(self, ctx: moderngl.Context):
        ctx.clear(*self.normalised())

EMPTY =     Color(000,  000,  000, 000)
WHITE =     Color(255,  255,  255)
BLACK =     Color(000,  000,  000)
RED =       Color(255,  000,  000)
GREEN =     Color(000,  255,  000)
BLUE =      Color(000,  000,  255)
CYAN =      Color(000,  255,  255)
MAGENTA =   Color(255,  000,  255)
YELLOW =    Color(255,  255,  000)