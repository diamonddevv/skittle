import pygame
import typing
import moderngl

import skittle

class Window():

    def __init__(self, 
                 initial_scene: skittle.scene.SceneSwitch | None,
                 title: str = "skittle engine", 
                 width: int = 1280, height: int = 720,

                 target_fps: int = 60,
                 icon_path: str = "",
                 fps_in_title: bool = False
                 ) -> None:
        self.title = title
        self.target_fps = target_fps


        self._running = False
        self._fps_in_title = fps_in_title
        self._window_surface = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF)
        self._clock = pygame.Clock()

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, skittle.__GLSL_MAJOR__)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, skittle.__GLSL_MINOR__)
        


        self.camera = skittle.render.Camera(width, height)
        self.scene_manager = skittle.scene.SceneManager(self.ctx, self.camera, initial_scene, self)

        if icon_path != "":
            image = pygame.image.load(icon_path).convert_alpha()
            pygame.display.set_icon(image)

    def run(self):
        dt = 0.0
        self._running = True

        while self._running:
            self.event_handle()
            self.update(dt)

            self.ctx.screen.depth_mask = True
            self.ctx.clear()
            self.ctx.screen.depth_mask = False
            self.draw(self.ctx, self.camera)
            self.camera.finish()
            pygame.display.flip()

            if self._fps_in_title:
                pygame.display.set_caption(f"{self.title} | FPS: {self._clock.get_fps():.0f}")    
            else:
                pygame.display.set_caption(self.title)
            dt = self._clock.tick(self.target_fps) / 1000

    def update(self, dt: float):
        self.scene_manager.update(dt)

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        self.scene_manager.draw(ctx, camera)

    def event_handle(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.close()
            if e.type == pygame.VIDEORESIZE:
                self.ctx.viewport = (0, 0, e.w, e.h)
                self.camera.resize(e.w, e.h)

            # event handlers
            if e.type in skittle._EventHandler._PYGAME_EVENT_HANDLERS:
                for callback in skittle._EventHandler._PYGAME_EVENT_HANDLERS[e.type]:
                    callback(e)

    def close(self):
        self._running = False

    def switch_scene(self, scene: skittle.scene.SceneSwitch):
        self.scene_manager.switch(scene)