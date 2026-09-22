import moderngl
import pygame

from skittle.render import gl
from skittle.render import mesh

from skittle.render.mesh import RenderInstance
from skittle.render.pixelfont import *
from skittle.render.particle import *
from skittle.render.postprocess import *


def texture(ctx: moderngl.Context, surface: pygame.Surface, force_size: tuple[int, int] | None = None) -> skittle.render.mesh.TextureMesh:
    return skittle.render.mesh.TextureMesh(ctx, surface, force_size[0] if force_size != None else surface.width, force_size[1] if force_size != None else surface.height)

def spritesheet(ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, sprite: tuple[int, int] = (0, 0)) -> skittle.render.mesh.SpritesheetMesh:
    return skittle.render.mesh.SpritesheetMesh(ctx, spritesheet, frame=sprite)

def instance_spritesheet(ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet) -> skittle.render.mesh.InstancedSpritesheetMesh:
    return skittle.render.mesh.InstancedSpritesheetMesh(ctx, spritesheet)

def text(id: str, camera: skittle.camera.Camera, text: str, pos: glm.vec2, scale: float = 1, color: skittle.color.Color = skittle.color.WHITE, orientation: skittle.render.TextRenderOrientation = 'left_to_right', overlay: bool = False):
    """
    quick-renders text using a font from pixelfont cache (see `skittle.resource.pixelfont`)
    """
    skittle.resource.cached_pixelfont(id).render(camera, text, pos, scale, color, orientation, overlay)