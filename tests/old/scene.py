import _ctx

from pyglm import glm
import moderngl
import skittle
import pygame
from skittle.render.camera import Camera
from skittle.render.oldmesh import Camera
from skittle.render.pixelfont import TextRenderer


class AbsTestScene(skittle.scene.Scene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, text_renderer: skittle.render.TextRenderer, key: str, next: skittle.scene.SceneSwitch, ctx: moderngl.Context, camera: Camera) -> None:
        super().__init__(scene_manager, ctx, camera)

        self.text_renderer = text_renderer
        self.key = key
        self.next = next

    def draw(self, ctx: moderngl.Context, camera: Camera):
        self.text_renderer.render(camera, skittle.i18n.tr("scene.template", skittle.i18n.tr(self.key)), glm.vec2(0, 0), 1, overlay=True)

    def update(self, dt: float, camera: skittle.render.Camera):
        press = pygame.key.get_just_pressed()
        if press[pygame.K_SPACE]:
            self.switch_scene(self.next)

        if press[pygame.K_e]: skittle.i18n.set_lang_key("en")
        if press[pygame.K_f]: skittle.i18n.set_lang_key("fi")
        if press[pygame.K_d]: skittle.i18n.set_lang_key("de")
            

class TestSceneA(AbsTestScene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, text_renderer: TextRenderer, ctx: moderngl.Context, camera: Camera) -> None:
        super().__init__(scene_manager, text_renderer, "scene.1", lambda manager, ctx, cam: TestSceneB(manager, self.text_renderer, ctx, cam), ctx, camera)

class TestSceneB(AbsTestScene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, text_renderer: TextRenderer, ctx: moderngl.Context, camera: Camera) -> None:
        super().__init__(scene_manager, text_renderer, "scene.2", lambda manager, ctx, cam: TestSceneC(manager, self.text_renderer, ctx, cam), ctx, camera)

class TestSceneC(AbsTestScene):
    def __init__(self, scene_manager: skittle.scene.SceneManager, text_renderer: TextRenderer, ctx: moderngl.Context, camera: Camera) -> None:
        super().__init__(scene_manager, text_renderer, "scene.3", lambda manager, ctx, cam: TestSceneA(manager, self.text_renderer, ctx, cam), ctx, camera)

class test_Scenes(skittle.render.Window):
    def __init__(self) -> None:
        super().__init__(None, "scene", 500, 500, fps_in_title=True)

        self.text_renderer = skittle.render.TextRenderer.from_json(self.ctx, "tests/asset/glyphxel_definition.json")
        self.switch_scene(lambda manager, ctx, cam: TestSceneA(manager, self.text_renderer, ctx, cam))
        

if __name__ == "__main__":
    skittle.i18n.load_i18ns("tests/asset/i18ns", "en")
    wnd = test_Scenes()

    wnd.run()