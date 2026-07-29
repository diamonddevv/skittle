import moderngl
from pyglm import glm
import skittle

class Particle():
    

    def __init__(self,
                 emission_point: glm.vec2,
                 size: float,
                 color: skittle.Color,
                 speed: float,
                 direction_rad: float,
                 ttl: float,
                 acceleration: float,
                 mesh: ParticleMesh
                 ) -> None:
        self.emission_point = emission_point
        self.size = size
        self.color = color
        self.speed = speed
        self.direction_rad = direction_rad
        self.ttl = ttl
        self.acceleration = acceleration

        self.mesh = mesh

    def draw(self, camera: skittle.render.Camera):
        self.mesh.color = self.color
        self.mesh.scale = self.size




class ParticleMesh(skittle.render.Mesh):
    def __init__(self, 
                 ctx: moderngl.Context,
                 vertex: str, fragment: str,
                 per_instance_data_format: str,
                 per_instance_data_names: tuple[str, ...],
                 per_instance_data_size: int,
                 instances: int = 256
                 ) -> None:
        vertices, indices = skittle.render.Mesh.uv_quad(1, 1)
        super().__init__(ctx, vertices, "", [], indices, vertex, fragment, build_vao=False)

        self.per_instance_data_format = per_instance_data_format
        self.per_instance_data_names = per_instance_data_names
        self.per_instance_data_size = per_instance_data_size

        self.build_vao_vbo(instances)

    def build_vao_vbo(self, reserve: int = 500):

        self.instance_vbo = self._ctx.buffer(reserve=self.per_instance_data_size * reserve, dynamic=True)
        self._instances = 0

        self._vao = self._ctx.vertex_array(self._program, [
            (self._vbo, "2f 2f", 'in_vertex_pos', 'in_uv'),
            (self.instance_vbo, self.per_instance_data_format + " /i", *self.per_instance_data_names)
        ], index_buffer=self._ibo)

    def bake_instances(self, instances: list[tuple]):
        data = []

        for i, instance in enumerate(instances):
            if i > self._instances:
                break
            data.extend(instance)
        
        self.instance_vbo.write(glm.array.from_numbers(glm.float32, *data).to_bytes())

    def render(self, camera: skittle.render.Camera, overlay: bool = False, mode: int = moderngl.TRIANGLES):
        if self._instances > 0:
            return super().render(camera, overlay, mode)