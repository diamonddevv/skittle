from pyglm import glm
import random
import skittle

class ParticleEmitter():
    

    def __init__(self,
                 emission_point: glm.vec2,
                 size: float,
                 color: skittle.Color,
                 speed: float,
                 direction_rad: float,
                 ttl: float,
                 acceleration: float,
                 mesh: skittle.render.MultiInstanceSpritesheetQuad,
                 sprite_cell: tuple[int, int]
                 ) -> None:
        self.emission_point = emission_point
        self.size = size
        self.color = color
        self.speed = speed
        self.direction_rad = direction_rad
        self.ttl = ttl
        self.acceleration = acceleration

        self.mesh = mesh
        self.sprite_cell = sprite_cell

        self._particles: list[ParticleInstance] = []
        self.max_particles = 256

    def draw(self, camera: skittle.render.Camera):
        self.mesh.color = self.color
        self.mesh.scale = self.size

        idata = [particle.to_instance_data() for particle in self._particles]
        self.mesh.bake_instances(idata)
        self.mesh.render(camera)

    def update(self, dt: float):
        rm = []
        for particle in self._particles:
            particle.ttl -= dt

            if particle.ttl <= 0:
                rm.append(particle)
                continue

            particle.pos += glm.vec2(
                glm.cos(particle.direction_rad), 
                glm.sin(particle.direction_rad)
                ) * particle.speed * dt

            particle.speed += particle.acceleration * dt

        for p in rm:
            self._particles.remove(p)
            

    def emit(self, variance: float = 0.05, n: int = 1):
        for i in range(n):
            if len(self._particles) >= self.max_particles:
                continue
            self._particles.append(
                ParticleInstance(
                    self.emission_point,
                    self.sprite_cell[0], self.sprite_cell[1],
                    self.size + random.random() * variance * 2 - variance,
                    self.color,
                    self.speed + random.random() * variance * 2 - variance, 
                    self.direction_rad + random.random() * variance * 2 - variance,
                    self.ttl,
                    self.acceleration + random.random() * variance * 2 - variance
                )
            )


class ParticleInstance():
    def __init__(self, pos: glm.vec2, cx: int, cy: int,
                 size: float,
                 color: skittle.Color,
                 speed: float,
                 direction_rad: float,
                 ttl: float,
                 acceleration: float) -> None:
        self.pos = glm.vec2(pos.x, pos.y)
        self.cx = cx
        self.cy = cy

        self.size = size
        self.color = color
        self.speed = speed
        self.direction_rad = direction_rad
        self.ttl = ttl
        self.acceleration = acceleration

    def to_instance_data(self) -> skittle.render.MultiInstanceSpritesheetQuad._InstanceData:
        return (self.pos.x, self.pos.y, self.cx, self.cy)