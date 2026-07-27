"""
## skittle
super epic amazing pygame engine that definitely never breaks

[source on github](https://github.com/diamonddevv/skittle/)
"""

import pygame
import colorama
import typing

from skittle import math
from skittle import render
from skittle import resource

__VERSION__: str = "0.0.0"

__GLSL_MAJOR__: int = 3
__GLSL_MINOR__: int = 3

_PROGRAM_DEV_DIRECTORY: str = ""
_PROGRAM_APP_DIRECTORY: str = ""

type _PygameEventHandler = typing.Callable[[pygame.Event], typing.Any]
_PYGAME_EVENT_HANDLERS: dict[int, list[_PygameEventHandler]] = {}


def log(msg: str):
    print(colorama.Fore.CYAN + "[skittle] " + colorama.Fore.RESET + msg)

def err(msg: str):
    print(colorama.Fore.RED + "[error] " + colorama.Fore.RESET + msg)

def bind_pygame_event_handler(handler: _PygameEventHandler, *event_type: int):
    for e in event_type:
        set = _PYGAME_EVENT_HANDLERS.get(e, [])
        set.append(handler)
        _PYGAME_EVENT_HANDLERS[e] = set

def init():
    log(f"initialised (v{__VERSION__})")
    pygame.init()
