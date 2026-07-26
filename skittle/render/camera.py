import numpy

class Camera():
    def __init__(self, width: int, height: int, zoom: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.zoom = zoom

        self.position = numpy.array([0.0, 0.0], dtype='f4')  # world-space center

    def projection(self):
        halfw = self.width / 2 / self.zoom
        halfh = self.height / 2/ self.zoom

        left = -halfw
        right = halfw
        bottom = -halfh
        top = halfh
        near = -1.0
        far = 1.0

        proj = numpy.identity(4, dtype='f4')
        proj[0,0] = 2 / (right - left)
        proj[1,1] = 2 / (top - bottom)
        proj[2,2] = -2 / (far - near)
        proj[3,0] = -(right + left) / (right - left)
        proj[3,1] = -(top + bottom) / (top - bottom)
        proj[3,2] = -(far + near) / (far - near)

        return proj
    
    def view_matrix(self):
        view = numpy.identity(4, dtype='f4')
        view[3, 0] = -self.position[0]
        view[3, 1] = -self.position[1]
        return view
    
    def get_projection_view_matrix(self):
        return self.view_matrix() @ self.projection()