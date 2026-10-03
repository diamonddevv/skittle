import moderngl
import pygame

from skittle.render import gl
from skittle.render import mesh

from skittle.render.mesh import RenderInstance
from skittle.render.text import *
from skittle.render.particle import *
from skittle.render.postprocess import *


def texture(ctx: skittle.Context, surface: pygame.Surface, force_size: tuple[int, int] | None = None) -> skittle.render.mesh.TextureMesh:
    return skittle.render.mesh.TextureMesh(ctx.mgl_ctx, surface, force_size[0] if force_size != None else surface.width, force_size[1] if force_size != None else surface.height)

def spritesheet(ctx: skittle.Context, spritesheet: skittle.resource.Spritesheet, sprite: tuple[int, int] = (0, 0)) -> skittle.render.mesh.SpritesheetMesh:
    return skittle.render.mesh.SpritesheetMesh(ctx.mgl_ctx, spritesheet, frame=sprite)

def instance_spritesheet(ctx: skittle.Context, spritesheet: skittle.resource.Spritesheet) -> skittle.render.mesh.InstancedSpritesheetMesh:
    return skittle.render.mesh.InstancedSpritesheetMesh(ctx.mgl_ctx, spritesheet)

def text(id: str, ctx: skittle.Context, text: str, pos: glm.vec2, scale: float = 1, color: skittle.color.Color = skittle.color.WHITE, orientation: skittle.render.TextRenderOrientation = 'left_to_right', overlay: bool = False):
    """
    quick-renders text using a font from pixelfont cache (see `skittle.resource.pixelfont`)
    """
    skittle.resource.cached_pixelfont(id).render(ctx, text, pos, scale, color, orientation, overlay)