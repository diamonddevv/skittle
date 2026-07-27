"""
super epic amazing pygame engine that definetely never breaks
"""

import pygame
import colorama

from skittle import render
from skittle import resource

__VERSION__: str = "0.0.0"

__GLSL_MAJOR__: int = 3
__GLSL_MINOR__: int = 3

def log(msg: str):
    print(colorama.Fore.CYAN + "[skittle] " + colorama.Fore.RESET + msg)

def err(msg: str):
    print(colorama.Fore.RED + "[ERROR] " + colorama.Fore.RESET + msg)

def init():
    log(f"initialised (v{__VERSION__})")
    pygame.init()
