from pyglm import glm
import moderngl
import typing
import skittle

class Camera():
    type _Submission = typing.Callable[[], typing.Any]

    def __init__(self, width: int, height: int, window_width: int, window_height: int, zoom: float = 1.0) -> None:
        self.frame_offset_x = 0
        self.frame_offset_y = 0
        self.frame_width = width
        self.frame_height = height
        self.window_width = window_width
        self.window_height = window_height

        self.zoom = zoom
        self.rotation = 0.0

        self.position = glm.vec2(0)

        self._overlay_layer_reserve = 500

        self._submissions: dict[int, list[Camera._Submission]] = {}

    def projection(self, overlay: bool):
        half_w = self.frame_width / 2 / (self.zoom if not overlay else 1)
        half_h = self.frame_height / 2 / (self.zoom if not overlay else 1)

        return glm.ortho(
            -half_w, half_w,
            -half_h, half_h,
            -1, 1
        )
    
    def view_matrix(self, overlay: bool):
        view = glm.mat4(1.0)
        if not overlay:
            if self.rotation != 0.0:
                view = glm.rotate(view, -glm.radians(self.rotation), glm.vec3(0,0,1))
            view = glm.translate(view, glm.vec3(-self.position.x, -self.position.y, 0.0))
        else:
            view = glm.translate(view, glm.vec3(
                -self.frame_width / 2, 
                self.frame_height / 2, 
                0.0))
        return view
    
    def proj_view_mat(self, overlay: bool = False):
        return self.projection(overlay) * self.view_matrix(overlay)
    
    def calc_layer(self, layer: int = 0, overlay: bool = False) -> int:
        if overlay:
            layer += self._overlay_layer_reserve
        else:
            if layer > self._overlay_layer_reserve:
                skittle.err(f"layers over {self._overlay_layer_reserve} are meant for overlay items")
        return layer

    def submit(self, function: _Submission, layer: int = 0):
        """
        queues an item on a layer for the painters algorithm
        """
        l = self._submissions.get(layer, [])
        l.append(function)
        self._submissions[layer] = l

    def begin_frame(self):
        pass

    def flush(self):
        """
        complete painter's algorithm, easier way of doing depth
        """
        for layer in sorted(self._submissions):
            for func in self._submissions[layer]:
                func()
        self._submissions.clear()


    def set_position(self, x: float, y: float):
        self.position = glm.vec2(x, y)

    def move(self, x: float, y: float):
        self.position -= glm.vec2(x, -y)

    def set_zoom(self, zoom: float = 1.0):
        self.zoom = zoom

    def reframe(self, viewport: tuple[int, int, int, int]):
        self.frame_offset_x = viewport[0]
        self.frame_offset_y = viewport[1]
        self.window_width = viewport[2]
        self.window_height = viewport[3]


    def frame_center(self) -> glm.vec2:
        return glm.vec2(self.frame_width / 2, self.frame_height / 2)