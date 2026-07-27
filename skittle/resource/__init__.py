import pygame


def image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()