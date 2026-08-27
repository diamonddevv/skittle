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

def lerp_vec(a: glm.vec2, b: glm.vec2, t: float) -> glm.vec2:
    return glm.vec2(
        lerpf(a.x, b.x, t),
        lerpf(a.y, b.y, t)
    )

def radf_to_vec(radians: float) -> glm.vec2:
    radians += glm.half_pi()
    return glm.vec2(glm.cos(radians), glm.sin(radians))

def aprx_rangef(start: float, stop: float, step: float) -> list[float]:

    values = [start]
    point = start
    while point < stop:
        point += step
        values.append(point)

    return values

def cubic_bezier_points(a: glm.vec2, b: glm.vec2, c: glm.vec2, d: glm.vec2, tesselation: float = 0.1) -> list[glm.vec2]:
    points = []

    for t in aprx_rangef(0.0, 1.0, tesselation):

        e = lerp_vec(a, b, t)
        f = lerp_vec(b, c, t)
        g = lerp_vec(c, d, t)

        h = lerp_vec(e, f, t)
        i = lerp_vec(f, g, t)

        points.append(lerp_vec(h, i, t))

    return points

def n_gon_vertices(origin: glm.vec2, n: int, r: float, offset: float = 0.0) -> list[glm.vec2]:
    return [glm.vec2(
            origin.x + r * glm.cos((glm.two_pi() * i) / n + offset),
            origin.y + r * glm.sin((glm.two_pi() * i) / n + offset)
        ) for i in range(n)]

class Rect():
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def pos(self) -> glm.vec2:
        return glm.vec2(self.x, self.y)
    
    def size(self) -> glm.vec2:
        return glm.vec2(self.w, self.h)

    def collides_point(self, vec: glm.vec2) -> bool:
        return vec.x >= self.x and vec.y >= self.y and vec.x < self.x + self.w and vec.y < self.y + self.h

    def collides_rect(self, other: Rect) -> bool:
        return not (
            self.x + self.w <= other.x or
            self.x >= other.x + other.w or
            self.y + self.h <= other.y or
            self.y >= other.y + other.h
        )
    
    def calc_overlap(self, other: Rect) -> glm.vec2:
        self_br = glm.vec2(self.x + self.w, self.y + self.h)
        other_br = glm.vec2(other.x + other.w, other.y + other.h)

        overlap_x = min(self_br.x, other_br.x) - max(self.x, other.x)
        overlap_y = min(self_br.y, other_br.y) - max(self.y, other.y)

        return glm.vec2(overlap_x, overlap_y)

    def __str__(self) -> str:
        return ("Rect(".ljust(5) + 
                f"{self.x},".ljust(8) +
                f"{self.y},".ljust(8) +
                f"{self.w},".ljust(8) +
                f"{self.h}".ljust(8) +
                ")"
                )
    
    @staticmethod
    def merge_rects(rects: list[Rect]) -> list[Rect]:
        """
        orthogonal polygon decomposition
        """
        return rects