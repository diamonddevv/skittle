import moderngl
import skittle
import pygame
import json
import numpy
from pyglm import glm



class Tilemap():
    def __init__(self, ctx: moderngl.Context, layout: numpy.ndarray, layout_alpha: numpy.ndarray, width: int, height: int, stitched_tileset: skittle.resource.Spritesheet, tiles: dict[str, tuple[int, int, int]]) -> None:
        self._ctx = ctx

        self.layout = layout
        self.layout_alpha = layout_alpha
        self.width = width
        self.height = height
        self.stitched_tileset = stitched_tileset
        self.tiles = tiles

        self.mesh = skittle.render.instance_spritesheet(ctx, self.stitched_tileset)

    
    def bake(self):
        instances: list[skittle.render.RenderInstance] = []

        for x in range(self.width):
            for y in range(self.height):
                if not self.is_empty(x, y):
                    data = self.get_tile(x, y)
                    if data == None:
                        continue

                    w = self.stitched_tileset.sprite_w
                    h = self.stitched_tileset.sprite_h
                    stitch, cx, cy = data
                    instances.append(skittle.render.RenderInstance(
                        glm.vec2(x * w, y * h),
                        (cx, cy),
                        stitch=stitch
                    ))


        self.mesh.bake_instances(instances)

    def render(self, camera: skittle.camera.Camera, 
                    position: glm.vec2, 
                    scale: glm.vec2 = glm.vec2(1.0), 
                    color: skittle.color.Color = skittle.color.WHITE, 
                    rotation: float = 0.0, 
                    layer: int = 0,
                    overlay: bool = False):
        self.mesh.render(camera, position, scale, color, rotation, layer, overlay)
    
    def is_empty(self, x: int, y: int) -> bool:
        return self.layout_alpha[x, y] == 0x00
    
    def get_tile(self, x: int, y: int) -> tuple[int, int, int] | None:
        key = self._get_px_layout_key(x, y)
        if key in self.tiles:
            return self.tiles[key]
        else:
            skittle.err(f"found undefined tile '{key}' in layout at ({x}, {y})")
            return None


    def _get_px_layout_key(self, x: int, y: int) -> str:
        (r, g, b) = self.layout[x, y]
        a = self.layout_alpha[x, y]

        r = int(r) # we want python numbers, not np numbers.
        g = int(g)
        b = int(b)
        a = int(a)
        
        n = r << 24
        n+= g << 16
        n+= b << 8
        n+= a

        return f"{n:08x}".lower()

    @staticmethod
    def from_json(ctx: moderngl.Context, path: str) -> Tilemap:
        f = open(path, "r")
        data = json.load(f)
        f.close()

        layout_path: str = data["layout"]
        tileset_paths: list[str] = data["tilesets"]
        tiles: dict[str, tuple[int, int, int]] = data["tiles"]

        layout = pygame.transform.flip(skittle.resource.image(layout_path), False, True)
        tilesets = [ skittle.resource.spritesheet(path) for path in tileset_paths ]
        lowered_tiles = { key.lower(): tiles[key] for key in tiles }

        return Tilemap(
            ctx,
            pygame.surfarray.pixels3d(layout),
            pygame.surfarray.pixels_alpha(layout),
            layout.width,
            layout.height,
            skittle.resource.Spritesheet.stitch(*tilesets),
            lowered_tiles
        )