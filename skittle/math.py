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

    def collides_aabb(self, other: Rect) -> bool:

        this_left = self.x
        this_top = self.y
        this_right = self.x + self.w
        this_bottom = self.y + self.h

        other_left = other.x
        other_top = other.y
        other_right = other.x + other.w
        other_bottom = other.y + other.h

        return (
            this_left > other_left or
            this_top < other_top or
            this_right < other_right or
            this_bottom > other_bottom
        )

    def aabb_correction(self, other: Rect):
        """
        moves self to stop colliding with other
        """
        this_left = self.x
        this_top = self.y
        this_right = self.x + self.w
        this_bottom = self.y + self.h

        other_left = other.x
        other_top = other.y
        other_right = other.x + other.w
        other_bottom = other.y + other.h

        if this_left > other_left:
            self.x = other.x
        if this_top < other_top:
            self.y = other.y
        if this_right < other_right:
            self.x = other.x + other.w - self.w
        if this_bottom > other_bottom:
            self.y = other.y + other.h - self.h 

    def __str__(self) -> str:
        return ("Rect(".ljust(5) + 
                f"{self.x},".ljust(8) +
                f"{self.y},".ljust(8) +
                f"{self.w},".ljust(8) +
                f"{self.h}".ljust(8) +
                ")"
                );