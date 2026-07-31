import typing
import moderngl
import skittle


type SceneSwitch = typing.Callable[[SceneManager, moderngl.Context, skittle.render.Camera], Scene]

class SceneManager():
    def __init__(self, ctx: moderngl.Context, camera: skittle.render.Camera, initial_scene: SceneSwitch | None, window: skittle.render.Window) -> None:
        self.ctx = ctx
        self.camera = camera
        self.window = window
        self.active = None if initial_scene == None else initial_scene(self, ctx, camera)
    
    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        if self.active != None:
            self.active.draw(ctx, camera)

    def update(self, dt: float, camera: skittle.render.Camera):
        if self.active != None:
            self.active.update(dt, camera)

    def switch(self, scene: SceneSwitch):
        if self.active != None:
            self.active.close()
        self.active = scene(self, self.ctx, self.camera)


class Scene():
    def __init__(self, scene_manager: SceneManager, ctx: moderngl.Context, camera: skittle.render.Camera) -> None:
        self.scene_manager = scene_manager
    
    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        pass

    def update(self, dt: float, camera: skittle.render.Camera):
        pass

    def close(self):
        pass

    def switch_scene(self, next: SceneSwitch):
        self.scene_manager.switch(next)