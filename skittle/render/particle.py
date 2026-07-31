from pyglm import glm
import random
import skittle

class ParticleEmitter():
    

    def __init__(self,
                 emission_point: glm.vec2, 
                 emission_radius: float, 
                 colors: list[skittle.color.Color], 
                 size_low: float, size_high: float, 
                 speed_low: float, speed_high: float, 
                 direction_low: float, direction_high: float, 
                 ttl_low: float, ttl_high: float,
                 
                 mesh: skittle.render.MultiInstanceSpritesheetQuad,
                 sprite_cells: list[tuple[int, int]],

                 acceleration_low: float = 0, acceleration_high: float = 0,
                 min_distance: float = 0.0,
                 scale_rate: float = 1,
                 max_particles: int = 256
                 ) -> None:
        
        self.emission_point = emission_point
        self.emission_radius = emission_radius
        self.colors = colors
        self.scale_low = size_low
        self.scale_high = size_high
        self.speed_low = speed_low
        self.speed_high = speed_high
        self.direction_low = direction_low
        self.direction_high = direction_high
        self.ttl_low = ttl_low
        self.ttl_high = ttl_high

        self.acceleration_low = acceleration_low
        self.acceleration_high = acceleration_high
        self.min_distance = min_distance
        self.scale_rate = scale_rate

        self.mesh = mesh
        self.sprite_cells = sprite_cells
        self.max_particles = max_particles

        self._particles: list[ParticleInstance] = []

    def draw(self, camera: skittle.render.Camera):
        idata = [particle.to_instance_data() for particle in self._particles]
        self.mesh.bake_instances(idata)
        self.mesh.render(camera)

    def update(self, dt: float):
        dead = []
        for particle in self._particles:
            particle.ttl -= dt

            if particle.ttl <= 0:
                dead.append(particle)
                continue
            

            particle.pos += glm.vec2(
                glm.cos(particle.direction_rad), 
                glm.sin(particle.direction_rad)
                ) * particle.speed * dt

            particle.speed += particle.acceleration * dt
        
        for death in dead:
            self._particles.remove(death)

    def emit(self, n: int = 1):
        for i in range(n):
            if len(self._particles) >= self.max_particles:
                continue

            position = self.emission_point + skittle.math.radf_to_vec(random.uniform(0, glm.two_pi())) * random.uniform(self.min_distance, self.emission_radius)
            scale = random.uniform(self.scale_low, self.scale_high)
            color = random.choice(self.colors)
            speed = random.uniform(self.speed_low, self.speed_high)
            direction = random.uniform(self.direction_low, self.direction_high)
            ttl = random.uniform(self.ttl_low, self.ttl_high)
            acceleration = random.uniform(self.acceleration_low, self.acceleration_high)
            sprite = random.choice(self.sprite_cells)

            self._particles.append(
                ParticleInstance(
                    position,
                    sprite[0], sprite[1],
                    glm.vec2(scale),
                    color,
                    speed, 
                    direction,
                    ttl,
                    acceleration
                )
            )


class ParticleInstance():
    def __init__(self, pos: glm.vec2, cx: int, cy: int,
                 scale: glm.vec2,
                 color: skittle.color.Color,
                 speed: float,
                 direction_rad: float,
                 ttl: float,
                 acceleration: float) -> None:
        self.pos = glm.vec2(pos.x, pos.y)
        self.cx = cx
        self.cy = cy

        self.scale = scale
        self.color = color
        self.speed = speed
        self.direction_rad = direction_rad
        self.ttl = ttl
        self.acceleration = acceleration

    def to_instance_data(self) -> skittle.render.MultiInstanceSpritesheetQuad._InstanceData:
        return (self.pos.x, self.pos.y, self.cx, self.cy, self.color, 0, self.scale.x, self.scale.y)