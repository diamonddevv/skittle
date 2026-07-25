import pygame
import typing

class Window():
    type _DrawCallback = typing.Callable[[], typing.Any]
    type _UpdateCallback = typing.Callable[[float], typing.Any]

    def __init__(self, 
                 title: str, 
                 width: int, height: int,

                 target_fps: int = 60,
                 icon_path: str = "",
                 draw_callback: Window._DrawCallback = lambda: None,
                 update_callback: Window._UpdateCallback = lambda dt: None,
                 ) -> None:
        self.title = title
        self.target_fps = target_fps
        self.draw_callback = draw_callback
        self.update_callback = update_callback

        self._running = False
        self._window_surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self._clock = pygame.Clock()

        if icon_path != "":
            image = pygame.image.load(icon_path).convert_alpha()
            pygame.display.set_icon(image)

    def run(self):
        dt = 0.0
        self._running = True

        while self._running:
            self.event_handle()
            self.update_callback(dt)

            self.draw_callback()
            pygame.display.flip()

            pygame.display.set_caption(self.title)
            dt = self._clock.tick(self.target_fps) / 1000

    def event_handle(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.close()

    def close(self):
        self._running = False