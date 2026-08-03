import moderngl
import time
import json
import typing
import skittle
import pygame
from pyglm import glm


class PostProcessor():
    def __init__(self, ctx: moderngl.Context, width: int, height: int) -> None:
        self.ctx = ctx
        self.width = width
        self.height = height

        self._effects: dict[str, PostProcessEffect] = {}

        self.scene_fbo: moderngl.Framebuffer
        self.ping_fbo: moderngl.Framebuffer
        self.pong_fbo: moderngl.Framebuffer

        self.scene_tex: moderngl.Texture
        self.ping_tex: moderngl.Texture
        self.pong_tex: moderngl.Texture

        self._make_buffers()
        

    def resize(self, width: int, height: int):
        self.width = width
        self.height = height

        self.release(all=False)
        self._make_buffers()

    def _make_fbo(self) -> tuple[moderngl.Framebuffer, moderngl.Texture]:
        tex = self.ctx.texture((self.width, self.height), 4)
        tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        depth = self.ctx.depth_renderbuffer((self.width, self.height))
        fbo = self.ctx.framebuffer(color_attachments=[tex], depth_attachment=depth)
        return fbo, tex

    def _make_buffers(self):
        self.scene_fbo, self.scene_tex = self._make_fbo()
        self.ping_fbo, self.ping_tex = self._make_fbo()
        self.pong_fbo, self.pong_tex = self._make_fbo()

    def _begin(self):
        self.scene_fbo.use()
        self.scene_fbo.clear()

    def _finish(self):
        if len(self._effects) == 0: # if nothing just copy and go
            self.ctx.copy_framebuffer(self.ctx.screen, self.scene_fbo)
            return

        src_tex = self.scene_tex
        buffers = [self.ping_fbo, self.pong_fbo]
        textures = [self.ping_tex, self.pong_tex]

        for i, uid in enumerate(self._effects):
            is_last = i == (len(self._effects) - 1)
            target = self.ctx.screen if is_last else buffers[i % 2]
            self._effects[uid].render(src_tex, target, self.width, self.height)
            if not is_last:
                src_tex = textures[i % 2]

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

        vertices, indices = skittle.render.OldMesh.uv_quad(2, 2)
        self._vbo = ctx.buffer(glm.array.from_numbers(glm.float32, *vertices).to_bytes())
        self._ibo = ctx.buffer(glm.array.from_numbers(glm.int32, *indices).to_bytes())
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