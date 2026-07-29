import math


def clamp(x: int, low: int, high: int) -> int:
    return min(max(x, low), high)

def clampf(x: float, low: float, high: float) -> float:
    return min(max(x, low), high)

def lerpf(a: float, b: float, t: float) -> float:
    return a + (b - a) * t