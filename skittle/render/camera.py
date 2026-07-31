from pyglm import glm
import moderngl
import typing
import skittle

class Camera():
    type _PaintersAlgorithmRender = typing.Callable[[Camera, bool, int], typing.Any]

    def __init__(self, width: int, height: int, zoom: float = 1.0) -> None:
        self.width = width
        self.height = height
        self.zoom = zoom
        self.rotation = 0.0

        self.position = glm.vec2(0)

        self._overlay_layer_reserve = 500

        self._painters_algorithm_layers: dict[int, list[tuple[Camera._PaintersAlgorithmRender, bool, int]]] = {}

    def projection(self, overlay: bool):
        half_w = self.width / 2 / (self.zoom if not overlay else 1)
        half_h = self.height / 2 / (self.zoom if not overlay else 1)

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
                -self.width / 2, 
                self.height / 2, 
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

    def await_completion(self, function: _PaintersAlgorithmRender, overlay: bool, mode: int = moderngl.TRIANGLES, layer: int = 0):
        """
        queues an item on a layer for the painters algorithm
        """
        l = self._painters_algorithm_layers.get(layer, [])
        l.append((function, overlay, mode))
        self._painters_algorithm_layers[layer] = l

    def finish(self):
        """
        complete painter's algorithm, easier way of doing depth
        """
        for layer in sorted(self._painters_algorithm_layers):
            for func, overlay, mode in self._painters_algorithm_layers[layer]:
                func(self, overlay, mode)
        self._painters_algorithm_layers.clear()


    def set_position(self, x: float, y: float):
        self.position = glm.vec2(x, y)

    def move(self, x: float, y: float):
        self.position -= glm.vec2(x, -y)

    def set_zoom(self, zoom: float = 1.0):
        self.zoom = zoom

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height