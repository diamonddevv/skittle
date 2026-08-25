import typing
import moderngl
import skittle


type SceneSwitch = typing.Callable[[SceneManager, moderngl.Context, skittle.camera.Camera], Scene]

class SceneManager():
    def __init__(self, ctx: moderngl.Context, camera: skittle.camera.Camera, initial_scene: SceneSwitch | None, window: skittle.render.Window) -> None:
        self.ctx = ctx
        self.camera = camera
        self.window = window
        self.active = None

        self._initial_scene = initial_scene

    def start(self):
        self.active = None if self._initial_scene == None else self._initial_scene(self, self.ctx, self.camera)

    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        if self.active != None:
            self.active.draw(ctx, camera)

    def update(self, dt: float, camera: skittle.camera.Camera):
        if self.active != None:
            self.active.update(dt, camera)

    def switch(self, scene: SceneSwitch):
        if self.active != None:
            self.active.close()
        self.active = scene(self, self.ctx, self.camera)


class Scene():
    def __init__(self, scene_manager: SceneManager, ctx: moderngl.Context, camera: skittle.camera.Camera) -> None:
        self.scene_manager = scene_manager
    
    def draw(self, ctx: moderngl.Context, camera: skittle.camera.Camera):
        pass

    def update(self, dt: float, camera: skittle.camera.Camera):
        pass

    def close(self):
        pass

    def switch_scene(self, next: SceneSwitch):
        self.scene_manager.switch(next)