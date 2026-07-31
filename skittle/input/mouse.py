from pyglm import glm
import pygame
import skittle

LEFT_MOUSE_BUTTON: int = 1
MIDDLE_MOUSE_BUTTON: int = 2
RIGHT_MOUSE_BUTTON: int = 3
MOUSE_BUTTON_4: int = 4
MOUSE_BUTTON_5: int = 5

type _ButtonsPoll = tuple[bool, bool, bool, bool, bool]

def buttons_down() -> _ButtonsPoll:
    return pygame.mouse.get_pressed(5)

def buttons_click() -> _ButtonsPoll:
    return pygame.mouse.get_just_pressed()

def buttons_released() -> _ButtonsPoll:
    return pygame.mouse.get_just_released()

def get_world_mouse_pos(cam: skittle.render.Camera, overlay: bool = False) -> glm.vec2:
    pg = pygame.mouse.get_pos()

    return glm.vec2(
        ((pg[0] - cam.width / 2) / (cam.zoom if not overlay else 1)) + cam.position.x, 
        ((pg[1] - cam.height / 2) / (cam.zoom if not overlay else 1)) - cam.position.y
        )