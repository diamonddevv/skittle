from pyglm import glm
import moderngl
import typing
import skittle

class Camera():
    type _RenderSubmission = typing.Callable[..., typing.Any]

    def __init__(self, frame_width: int, frame_height: int, zoom: float = 1.0) -> None:
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.position = glm.vec2(0)
        self.zoom = zoom
        self.rotation = 0.0

        self._overlay_layer_reserve = 500

        self._submissions: dict[int, list[Camera._RenderSubmission]] = {}

    def projection(self, overlay: bool):
        # the projection controls frame zooming, or in other words, what is in the frame

        half_w = self.frame_width / 2 / (self.zoom if not overlay else 1)
        half_h = self.frame_height / 2 / (self.zoom if not overlay else 1)

        return glm.ortho(
            -half_w, half_w,
            -half_h, half_h,
            -1, 1 # we do depth via the painters algorithm. its slower, sure, but its easier.
        )
    
    def view_matrix(self, overlay: bool):

        # rotation -> scaling -> translation. has to be that order

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
    
    def begin_frame(self):
        pass

    def submit(self, submission: _RenderSubmission, layer: int = 0):
        layr = self._submissions.get(layer, [])
        layr.append(submission)
        self._submissions[layer] = layr

    def flush(self):
        """
        complete painter's algorithm, easier way of doing depth
        """
        for layer in sorted(self._submissions):
            for submission in self._submissions[layer]:
                submission(self)
        self._submissions.clear()

    def move(self, x: float, y: float):
        self.position += glm.vec2(-x, y)

    def set_position(self, x: float, y: float):
        self.position = glm.vec2(x, y)

    def set_zoom(self, zoom: float = 1.0):
        self.zoom = zoom

    def resize(self, frame_width: int, frame_height: int):
        self.frame_width = frame_width
        self.frame_height = frame_height