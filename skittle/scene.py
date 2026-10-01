import typing
import moderngl
import skittle


type SceneSwitch = typing.Callable[[SceneManager, skittle.context.Context], Scene]

class SceneManager():
    def __init__(self, ctx: skittle.context.Context, initial_scene: SceneSwitch | None, window: skittle.window.Window) -> None:
        self.ctx = ctx
        self.window = window
        self.active = None

        self._initial_scene = initial_scene

    def start(self):
        self.active = None if self._initial_scene == None else self._initial_scene(self, self.ctx)

    def draw(self, ctx: skittle.context.Context):
        if self.active != None:
            self.active.draw(ctx)

    def update(self, dt: float, ctx: skittle.context.Context):
        if self.active != None:
            self.active.update(dt, ctx)

    def switch(self, scene: SceneSwitch):
        if self.active != None:
            self.active.close()
        self.active = scene(self, self.ctx)


class Scene():
    def __init__(self, scene_manager: SceneManager, ctx: skittle.context.Context) -> None:
        self.scene_manager = scene_manager
    
    def draw(self, ctx: skittle.context.Context):
        pass

    def update(self, dt: float, ctx: skittle.context.Context):
        pass

    def close(self):
        pass

    def switch_scene(self, next: SceneSwitch):
        self.scene_manager.switch(next)