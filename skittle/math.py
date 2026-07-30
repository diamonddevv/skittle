from pyglm import glm

def clamp(x: int, low: int, high: int) -> int:
    if x > high:
        return high
    if x < low:
        return low
    return x 

def clampf(x: float, low: float, high: float) -> float:
    if x > high:
        return high
    if x < low:
        return low
    return x 

def lerpf(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def radf_to_vec(radians: float) -> glm.vec2:
    radians += glm.half_pi()
    return glm.vec2(glm.cos(radians), glm.sin(radians))