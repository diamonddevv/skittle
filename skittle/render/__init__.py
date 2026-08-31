import moderngl
import pygame

from skittle.render import gl
from skittle.render import mesh

from skittle.render.mesh import RenderInstance
from skittle.render.pixelfont import *
from skittle.render.particle import *
from skittle.render.postprocess import *


def texture(ctx: moderngl.Context, surface: pygame.Surface) -> skittle.render.mesh.TextureMesh:
    return skittle.render.mesh.TextureMesh(ctx, surface, surface.width, surface.height)

def spritesheet(ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet, sprite: tuple[int, int] = (0, 0)) -> skittle.render.mesh.SpritesheetMesh:
    return skittle.render.mesh.SpritesheetMesh(ctx, spritesheet, frame=sprite)

def instance_spritesheet(ctx: moderngl.Context, spritesheet: skittle.resource.Spritesheet) -> skittle.render.mesh.InstancedSpritesheetMesh:
    return skittle.render.mesh.InstancedSpritesheetMesh(ctx, spritesheet)