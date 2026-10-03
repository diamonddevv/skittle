import pygame
import skittle
import moderngl
from pyglm import glm

class _Meshes():

    _line: skittle.render.mesh.LineMesh
    _texture: skittle.render.mesh.TextureMesh

    @staticmethod
    def _init(mgl_ctx: moderngl.Context):
        _Meshes._line = skittle.render.mesh.LineMesh(mgl_ctx)
        _Meshes._texture = skittle.render.mesh.TextureMesh(mgl_ctx, None)


def line(ctx: skittle.Context, points: list[glm.vec2], line_color: skittle.color.Color, closed: bool = False, fill: skittle.color.Color | None = None, layer: int = 0, thickness: float = 1.0, consistent_thickness: bool = False, overlay: bool = False):
    def _submission():
        ctx.mgl_ctx.line_width = thickness * (ctx.camera.zoom if consistent_thickness else 1)
        _Meshes._line.bake(points, closed)
        _Meshes._line._render_now(ctx.camera, line_color, overlay, fill)

    ctx.camera.submit(_submission, ctx.camera.calc_layer(layer, overlay))


def circle(ctx: skittle.Context, origin: glm.vec2, radius: float, color: skittle.color.Color, outline_col: skittle.color.Color | None = None, outline_width: float = 1.0, consistent_outline_width: bool = False, layer: int = 0, overlay: bool = False):
    """actually just a dodecagon but close enough right"""
    line(ctx, skittle.math.n_gon_vertices(origin, 12, radius), 
         color if outline_col == None else outline_col, 
         True, 
         color, 
         layer, outline_width, consistent_outline_width, overlay
         )

def rect(ctx: skittle.Context, rect: skittle.math.Rect, color: skittle.color.Color, outline_col: skittle.color.Color | None = None, outline_width: float = 1.0, consistent_outline_width: bool = False, layer: int = 0, overlay: bool = False):
    points = [
        glm.vec2(rect.x, rect.y),
        glm.vec2(rect.x + rect.w, rect.y),
        glm.vec2(rect.x + rect.w, rect.y + rect.h),
        glm.vec2(rect.x, rect.y + rect.h),
    ]

    line(ctx, points, 
         color if outline_col == None else outline_col, 
         True, 
         color, 
         layer, outline_width, consistent_outline_width, overlay
         )