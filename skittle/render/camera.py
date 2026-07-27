from pyglm import glm

class Camera():
    def __init__(self, width: int, height: int, zoom: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.zoom = zoom
        self.rotation = 0.0

        self.position = glm.vec2(0)

    def projection(self, overlay: bool):
        half_w = self.width / 2 / (self.zoom if not overlay else 1)
        half_h = self.height / 2 / (self.zoom if not overlay else 1)

        return glm.ortho(
            -half_w, half_w,
            -half_h, half_h,
            -1, 0
        )
    
    def view_matrix(self, overlay: bool):
        view = glm.mat4(1.0)
        if not overlay:
            if self.rotation != 0.0:
                view = glm.rotate(view, -glm.radians(self.rotation), glm.vec3(0,0,1))
            view = glm.translate(view, glm.vec3(-self.position.x, -self.position.y, 0.0))
        else:
            view = glm.translate(view, glm.vec3(
                -self.width / 2, 
                self.height / 2, 
                0.0))
        return view
    
    def proj_view_mat(self, overlay: bool = False):
        return self.projection(overlay) * self.view_matrix(overlay)


    def set_position(self, x: float, y: float):
        self.position = glm.vec2(x, y)

    def move(self, x: float, y: float):
        self.position -= glm.vec2(x, -y)

    def set_zoom(self, zoom: float = 1.0):
        self.zoom = zoom

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height