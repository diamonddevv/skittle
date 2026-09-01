import pygame
import os
import skittle
import moderngl
import io
import requests

from skittle.resource.spritesheet import *
from skittle.resource.tilemap import *


def image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()

def spritesheet(path: str, sprite_w: int = 16, sprite_h: int = 16, sep_x: int = 0, sep_y: int = 0) -> Spritesheet:
    return Spritesheet(image(path), sprite_w, sprite_h, sep_x, sep_y)

def tilemap(ctx: moderngl.Context, path: str) -> skittle.resource.Tilemap:
    return skittle.resource.Tilemap.from_json(ctx, path)

def postprocessor(ctx: moderngl.Context, path: str) -> skittle.render.PostProcessEffect:
    return skittle.render.PostProcessEffect.from_json(ctx, path)

def program(ctx: moderngl.Context, frag_path: str = "shader/blit.frag", vert_path: str = "shader/blit.vert") -> moderngl.Program:
    return ctx.program(vertex_shader=_txtfile(vert_path), fragment_shader=_txtfile(frag_path))

def image_from_url(url: str, user_agent_author_contact_label: str) -> pygame.Surface:
    bytes = requests.get(url, headers={'User-Agent': f'skittle engine-based app ({user_agent_author_contact_label})' }).content
    data = io.BytesIO(bytes)
    return pygame.image.load(data)




def _txtfile(path: str) -> str:
    f = open(path, "r")
    s = f.read()
    f.close()
    return s

# # # #

class _ResourceData():
    _PROGRAM_DEV_DIRECTORY: str = ""
    _PROGRAM_APP_DIRECTORY: str = ""

def set_program_directories(dev: str, app: str):
    skittle.resource._ResourceData._PROGRAM_DEV_DIRECTORY = dev
    skittle.resource._ResourceData._PROGRAM_APP_DIRECTORY = app

def get_program_path(plus: str = "") -> str:
    if skittle.resource._ResourceData._PROGRAM_DEV_DIRECTORY == "" or skittle.resource._ResourceData._PROGRAM_APP_DIRECTORY == "":
        raise ValueError("attempted to access program path when program dev directory or app directory names have not been set! (you may have forgotten to call set_program_directories)")

    path = pygame.system.get_pref_path(org=skittle.resource._ResourceData._PROGRAM_DEV_DIRECTORY, app=skittle.resource._ResourceData._PROGRAM_APP_DIRECTORY)
    if path == "":
        return path
    else:
        path = path + plus
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path