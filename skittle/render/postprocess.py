import moderngl
import time
import json
import skittle
from pyglm import glm


class PostProcessor():
    def __init__(self, ctx: moderngl.Context, width: int, height: int) -> None:
        self.ctx = ctx
        self.width = width
        self.height = height

        self._effects: list[PostProcessEffect] = []

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

        for i, effect in enumerate(self._effects):
            is_last = i == (len(self._effects) - 1)
            target = self.ctx.screen if is_last else buffers[i % 2]
            effect.render(src_tex, target, self.width, self.height)
            if not is_last:
                src_tex = textures[i % 2]

    def add(self, postproc: PostProcessEffect):
        self._effects.append(postproc)

    def release(self, all: bool = True):
        for fbo, tex in [
            (self.scene_fbo, self.scene_tex), 
            (self.ping_fbo, self.ping_tex), 
            (self.pong_fbo, self.pong_tex)
            ]:
            fbo.release()
            tex.release()

        if all:
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

    def __init__(self, ctx: moderngl.Context, fragment_shader: str, vertex_shader: str = VERTEX):
        self.ctx = ctx
        self._program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        vertices, indices = skittle.render.Mesh.uv_quad(2, 2)
        self._vbo = ctx.buffer(glm.array.from_numbers(glm.float32, *vertices).to_bytes())
        self._ibo = ctx.buffer(glm.array.from_numbers(glm.int32, *indices).to_bytes()) if indices != None else None
        self._vao = ctx.vertex_array(self._program, [(self._vbo, '2f 2f', 'in_pos', 'in_uv')], index_buffer=self._ibo)

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
        self._vao.render(moderngl.TRIANGLES)


    @staticmethod
    def from_json(ctx: moderngl.Context, filepath: str) -> PostProcessEffect:
        with open(filepath, 'rb') as f:
            data = json.load(f)

        with open(data["vertex_shader"], 'r') as f:
            vertex = f.read()

        effect = PostProcessEffect(
            ctx,
            vertex
        )
        return effect