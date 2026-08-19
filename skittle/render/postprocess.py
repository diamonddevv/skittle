import moderngl
import time
import json
import typing
import skittle
import pygame
import numpy as np
from pyglm import glm


class PostProcessor():
    def __init__(self, ctx: moderngl.Context, width: int, height: int) -> None:
        self.ctx = ctx
        self.width = width
        self.height = height
        self.aspect = width / height

        self._effects: dict[str, PostProcessEffect] = {}

        self.scene_fbo: moderngl.Framebuffer
        self.ping_fbo: moderngl.Framebuffer
        self.pong_fbo: moderngl.Framebuffer

        self.scene_tex: moderngl.Texture
        self.ping_tex: moderngl.Texture
        self.pong_tex: moderngl.Texture

        self.window_size = (width, height)
        self.vp_size = (width, height)
        self.viewport = self._compute_viewport(*self.window_size)

        self._make_buffers()
        self._make_presentation_prog()

    def _compute_viewport(self, win_w: int, win_h: int) -> tuple[int, int, int, int]:
        win_aspect = win_w / win_h
        if win_aspect > self.aspect:
            vp_h = win_h
            vp_w = int(vp_h * self.aspect)
        else:
            vp_w = win_w
            vp_h = int(vp_w / self.aspect)
        vp_x = (win_w - vp_w) // 2
        vp_y = (win_h - vp_h) // 2
        return (vp_x, vp_y, vp_w, vp_h)

    def resize_viewport(self, width: int, height: int):
        """updates viewport"""
        self.window_size = (width, height)
        self.viewport = self._compute_viewport(width, height)
        self.vp_size = (self.viewport[2], self.viewport[3])
        self.release(all=False)
        self._make_buffers()

    def _make_presentation_prog(self):
        vertices = np.array(
            [-1, -1, 0, 0,
              1, -1, 1, 0,
             -1,  1, 0, 1,
              1,  1, 1, 1], dtype='f4'
        )
        self._presentation_prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_pos;
                in vec2 in_uv;
                out vec2 uv;
                void main() {
                    uv = in_uv;
                    gl_Position = vec4(in_pos, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D tex;
                in vec2 uv;
                out vec4 f_color;
                void main() { f_color = texture(tex, uv); }
            """,
        )
        vbo = self.ctx.buffer(vertices.tobytes())
        self._presentation_vao = self.ctx.vertex_array(
            self._presentation_prog, [(vbo, '2f 2f', 'in_pos', 'in_uv')]
        )

    def _present(self, texture: moderngl.Texture):
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *self.window_size)
        self.ctx.clear()

        self.ctx.viewport = self.viewport
        texture.use(location=0)
        self._presentation_prog['tex'] = 0
        self._presentation_vao.render(moderngl.TRIANGLE_STRIP)

    def reframe(self, width: int, height: int):
        """
        change aspect ratio
        """
        self.width = width
        self.height = height
        self.aspect = width / height
        self.release(all=False)
        self._make_buffers()

    def _make_fbo(self) -> tuple[moderngl.Framebuffer, moderngl.Texture]:
        tex = self.ctx.texture(self.vp_size, 4)
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        depth = self.ctx.depth_renderbuffer(self.vp_size)
        fbo = self.ctx.framebuffer(color_attachments=[tex], depth_attachment=depth)
        return fbo, tex

    def _make_buffers(self):
        self.scene_fbo, self.scene_tex = self._make_fbo()
        self.ping_fbo, self.ping_tex = self._make_fbo()
        self.pong_fbo, self.pong_tex = self._make_fbo()

    def begin_frame(self):
        self.scene_fbo.use()
        self.scene_fbo.clear()

    def flush(self):
        if len(self._effects) == 0:
            self._present(self.scene_tex)
            return

        src_tex = self.scene_tex
        buffers = [self.ping_fbo, self.pong_fbo]
        textures = [self.ping_tex, self.pong_tex]

        for i, uid in enumerate(self._effects):
            target = buffers[i % 2]
            self._effects[uid].render(src_tex, target, *self.vp_size)
            src_tex = textures[i % 2]

        self._present(src_tex)

    def add(self, postproc: PostProcessEffect):
        self._effects[postproc.uid] = postproc

    def modify_param(self, id: str, param: str, value: float | tuple[float, ...]):
        self._effects[id]._params[param] = value

    def release(self, all: bool = True):
        for fbo, tex in [
            (self.scene_fbo, self.scene_tex), 
            (self.ping_fbo, self.ping_tex), 
            (self.pong_fbo, self.pong_tex)
            ]:
            fbo.release()
            tex.release()
        
        if all:
            for uid in self._effects:
                self._effects[uid].release()
                
            self.scene_fbo.release()
            self.scene_tex.release()
        

class PostProcessEffect():
    VERTEX = """
#version 330

in vec2 in_pos;
in vec2 in_uv;

uniform float u_time;

out vec2 v_uv;

void main() {
    v_uv = vec2(in_uv.x, -in_uv.y);
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

    def __init__(self, ctx: moderngl.Context, uid: str, fragment_shader: str, vertex_shader: str = VERTEX, params: dict[str, typing.Any] = {}, sampler_paths: list[str] = []):
        self.ctx = ctx
        self.uid = uid
        self._program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        self._params = params

        self._samplers: list[moderngl.Texture] = []
        self._build_use_sampler_textures(sampler_paths)

        vertices, indices = skittle.render.gl.uv_quad(2, 2)
        self._vbo = ctx.buffer(vertices)
        self._ibo = ctx.buffer(indices)
        self._vao = ctx.vertex_array(self._program, [(self._vbo, '2f 2f', 'in_pos', 'in_uv')], index_buffer=self._ibo)

    def _build_use_sampler_textures(self, sampler_paths: list[str]):
        for i, path in enumerate(sampler_paths):
            img = skittle.resource.image(path)
            texture = self.ctx.texture(img.size, 4, pygame.image.tobytes(img, "RGBA"))
            texture.use(i + 1) # 0 is reserved for the screen texture

    def uniform(self, key: str, value):
        if key in self._program:
            if type(value) == bytes:
                self._program[key].write(value) # type: ignore
            else:
                self._program[key].value = value # type: ignore

    def render(self, src_framebuf_tex: moderngl.Texture, target_framebuf: moderngl.Framebuffer, width: int, height: int):
        target_framebuf.use()
        src_framebuf_tex.use(0)
        self.uniform("u_screen_texture", 0)
        self.uniform("u_resolution", (width, height))
        self.uniform("u_time", time.perf_counter())
        
        for param in self._params:
            self.uniform(param, self._params[param])

        self._vao.render(moderngl.TRIANGLES)

    def release(self):
        for sampler in self._samplers:
            sampler.release()
        self._vbo.release()
        self._ibo.release()
        self._vao.release()

    @staticmethod
    def from_json(ctx: moderngl.Context, filepath: str) -> PostProcessEffect:
        with open(filepath, 'rb') as f:
            data = json.load(f)

        with open(data["vertex_shader"], 'r') as f:
            vertex = f.read()

        effect = PostProcessEffect(
            ctx,
            data["effect_uid"],
            vertex,
            params=data.get("uniform_param_defaults", {}),
            sampler_paths=data.get("samplers", [])
        )
        return effect