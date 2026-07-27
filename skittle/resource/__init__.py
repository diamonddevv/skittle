import pygame

from skittle.resource.spritesheet import *

def image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()

def spritesheet(path: str, sprite_w: int = 16, sprite_h: int = 16, sep_x: int = 0, sep_y: int = 0) -> Spritesheet:
    return Spritesheet(image(path), sprite_w, sprite_h, sep_x, sep_y)