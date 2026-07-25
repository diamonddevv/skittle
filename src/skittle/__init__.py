import pygame
import colorama

from src.skittle import window

__VERSION__: str = "0.0.0"

def log(msg: str):
    print(colorama.Fore.CYAN + "[skittle] " + colorama.Fore.RESET + msg)

def init():
    log(f"initialised (v{__VERSION__})")
    pygame.init()
