import pygame
import typing
import moderngl

from skittle import render

class Window():

    def __init__(self, 
                 title: str = "skittle engine", 
                 width: int = 1280, height: int = 720,

                 target_fps: int = 60,
                 icon_path: str = ""
                 ) -> None:
        self.title = title
        self.target_fps = target_fps


        self._running = False
        self._window_surface = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.OPENGL)
        self._clock = pygame.Clock()

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        self.mgl_ctx = moderngl.create_context()
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

    def close(self):
        self._running = False