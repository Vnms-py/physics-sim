import pyglet as pg
from pyglet.math import Vec2, Vec3
from random import randint
from colorsys import hls_to_rgb



screen = pg.display.get_display().get_default_screen()
width, height = screen.width, screen.height
window = pg.window.Window(width, height, fullscreen = True)

batch = pg.graphics.Batch()

g: float = 20


connections = []
class Spring:
    def __init__(self, node1, node2, length:float, strength:float):
        self.node1 = node1
        self.node2 = node2
        self.length = length
        self.strength = strength 
        color = (Vec3(*self.node1.ball.color[:3])+Vec3(*self.node2.ball.color[:3]))//2
        self.string = pg.shapes.Line(*node1.position, *node2.position, thickness=2*strength, color=color, batch=batch)       
    
    def pull(self):
        future_rel = (self.node1.position+10*self.node1.velocity)-(self.node2.position+10*self.node2.velocity)
        dist = future_rel.length()
        if dist >= self.length:
            force = future_rel.normalize() * (1-self.length/dist)/2 * self.strength
            self.node1.velocity -= force
            self.node2.velocity += force
            
        self.string.x, self.string.y, self.string.x2, self.string.y2, = *self.node1.position, *self.node2.position


class Circle(Spring):
    def __init__(self, x:float, y:float, radius:float, mass:float, vel_x:float, vel_y:float, color):
        self.ball = pg.shapes.Circle(x, y, radius, color=color, batch = batch)
        self.position = Vec2(x, y)
        self.velocity = Vec2(vel_x, vel_y)
        self.radius = radius
        self.mass = mass
        self.elasticity = .99
        self.friction = .01
        window.push_handlers(self)
        
        
    def move(self, dt):
        for _ in range(precision):
            self.collision()
            self.velocity -= Vec2(0, g)*dt/precision
            self.position += self.velocity/precision
            self.ball.position = self.position
            
        for group in connections:
            group.pull()
        
        
    def collision(self):
        if not height-self.radius >= self.position.y >= self.radius:
            self.velocity = Vec2(self.velocity.x*(1-self.friction), -self.velocity.y*self.elasticity)
        
            if self.position.y < self.radius:
                self.position += Vec2(0, self.radius-self.position.y)+1e-6
            else:
                self.position -= Vec2(0, self.radius-(height-self.position.y))+1e-6
            
            
        if not width-self.radius >= self.position.x >= self.radius:
            self.velocity = Vec2(-self.velocity.x*self.elasticity, self.velocity.y*(1-self.friction))
            
            if self.position.x < self.radius:
                self.position += Vec2(self.radius-self.position.x, 0)+1e-6
            else:
                self.position -= Vec2(self.radius-(width-self.position.x), 0)+1e-6
            
            
        for i, ball in enumerate(balls):
            if ball == self or i < balls.index(self):
                continue
            rel = Vec2(*(self.position-ball.position))
            if rel.length() <= self.radius+ball.radius:
                vec_N = rel.normalize()
                vec_T = Vec2(vec_N.y, -vec_N.x)

                rel_vel = self.velocity-ball.velocity
                rel_vel_N = rel_vel.dot(vec_N)
                rel_vel_T = rel_vel.dot(vec_T)
                
                if rel_vel_N >= 0:
                    continue
                
                vel_N = -(vec_N*rel_vel_N)*(1+self.elasticity)
                
                vel_T = -(vec_T*rel_vel_T)*self.friction
                new_vel = vel_N + vel_T

                masses = self.mass+ball.mass
                self.velocity += new_vel*ball.mass/masses
                ball.velocity -= new_vel*self.mass/masses

                dist = rel.length()

                if dist == 0:
                    return
                vec_N = rel/dist
                overlap = self.radius+ball.radius-dist
                if overlap > 0:
                    correction = vec_N*(overlap/2)
                    self.position += correction
                    ball.position -= correction
                
                
            
    def on_draw(self):
        window.clear()
        batch.draw()

                
# x, y, radius, mass, vel_x, vel_y, color
balls = []
for i in range(1, 6):
    hls =  hls_to_rgb((i-1)/5, .5, .5)
    col = tuple(int(255*c) for c in hls)
    
    # balls += [Circle(20*i, 20*i, 20, 1, i, i, col)]
    balls += [Circle(randint(0, width), randint(0, height), 20, 1, 0, 0, col)]

connections += [Spring(balls[0], balls[1], 400, 1)]
connections += [Spring(balls[1], balls[2], 400, 1)]

precision = 4
g = 40
fps = 60

for ball in balls:
    pg.clock.schedule_interval(ball.move, 1/fps)
    

    

pg.app.run()