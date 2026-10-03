from pyglm import glm
import pygame
import skittle

LEFT_MOUSE_BUTTON: int = 0
MIDDLE_MOUSE_BUTTON: int = 1
RIGHT_MOUSE_BUTTON: int = 2
MOUSE_BUTTON_4: int = 3
MOUSE_BUTTON_5: int = 4

type _ButtonsPoll = tuple[bool, bool, bool, bool, bool]

def buttons_down() -> _ButtonsPoll:
    return pygame.mouse.get_pressed(5)

def buttons_click() -> _ButtonsPoll:
    return pygame.mouse.get_just_pressed()

def buttons_released() -> _ButtonsPoll:
    return pygame.mouse.get_just_released()

def get_world_mouse_pos(ctx: skittle.Context, overlay: bool = False) -> glm.vec2:
    rx, ry = pygame.mouse.get_pos()

    px = (rx - ctx.camera.frame_offset_x) * (ctx.camera.frame_width / ctx.camera.window_width)
    py = (ry - ctx.camera.frame_offset_y) * (ctx.camera.frame_height / ctx.camera.window_height)

    return glm.vec2(
        ((px - (ctx.camera.frame_width / 2 if not overlay else 0)) / (ctx.camera.zoom if not overlay else 1)) + (ctx.camera.position.x if not overlay else 0), 
        ((py - (ctx.camera.frame_height / 2 if not overlay else 0)) / (ctx.camera.zoom if not overlay else 1)) - (ctx.camera.position.y if not overlay else 0)
        )