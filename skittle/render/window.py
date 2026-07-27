import pygame
import typing
import moderngl

import skittle

class Window():

    def __init__(self, 
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

        self.mgl_ctx = moderngl.create_context()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, skittle.__GLSL_MAJOR__)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, skittle.__GLSL_MINOR__)
        self.mgl_ctx.enable(moderngl.BLEND)
        self.camera = skittle.render.Camera(width, height)

        if icon_path != "":
            image = pygame.image.load(icon_path).convert_alpha()
            pygame.display.set_icon(image)

    def run(self):
        dt = 0.0
        self._running = True

        while self._running:
            self.event_handle()
            self.update(dt)

            self.mgl_ctx.clear(0,0,0)
            self.draw(self.mgl_ctx, self.camera)
            pygame.display.flip()

            if self._fps_in_title:
                pygame.display.set_caption(f"{self.title} | FPS: {self._clock.get_fps():.0f}")    
            else:
                pygame.display.set_caption(self.title)
            dt = self._clock.tick(self.target_fps) / 1000

    def update(self, dt: float):
        pass

    def draw(self, ctx: moderngl.Context, camera: skittle.render.Camera):
        pass

    def event_handle(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.close()
            if e.type == pygame.VIDEORESIZE:
                self.mgl_ctx.viewport = (0, 0, e.w, e.h)
                self.camera.resize(e.w, e.h)

    def close(self):
        self._running = False