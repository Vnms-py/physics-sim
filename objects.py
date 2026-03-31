import pyglet as pg
from pyglet.math import Vec2, Vec3
from random import randint
from colorsys import hls_to_rgb
from sympy import sign


connections = []
class Spring:
    def __init__(self, main, node1, node2, length:float, strength:float):
        self.main = main
        self.node1 = node1
        self.node2 = node2
        self.length = length
        self.strength = strength 
        color = (Vec3(*self.node1.ball.color[:3])+Vec3(*self.node2.ball.color[:3]))//2
        self.string = pg.shapes.Line(*node1.position, *node2.position, thickness=strength**(1/2), color=color, batch=self.main.batch)       
    
    def pull(self):
        future_rel = (self.node1.position+self.node1.velocity)-(self.node2.position+self.node2.velocity)
        
        ft_rel_dist = future_rel.length()
        
        diff = (self.length-ft_rel_dist)
        
        
    
        force = future_rel.normalize() * diff/self.length * self.strength
        self.node1.velocity += force
        self.node2.velocity -= force
            
        self.string.x, self.string.y, self.string.x2, self.string.y2, = *self.node1.position, *self.node2.position


class Circle(Spring):
    
    def __init__(self, main, x:float, y:float, radius:float, mass:float, vel_x:float, vel_y:float, color):
        self.main = main
        self.ball = pg.shapes.Circle(x, y, radius, color=color, batch = self.main.batch)
        self.position = Vec2(x, y)
        self.velocity = Vec2(vel_x, vel_y)
        self.radius = radius
        self.mass = mass
        self.elasticity = .99
        self.friction = .01
        
        
    def move(self, dt):
        for _ in range(self.main.precision):
            self.collision()
            self.velocity -= Vec2(0, self.main.g)*dt/self.main.precision
            self.position += self.velocity/self.main.precision
            self.ball.position = self.position
            
        
        
    def collision(self):
        if not self.main.height-self.radius >= self.position.y >= self.radius:
            self.velocity = Vec2(self.velocity.x*(1-self.friction), -self.velocity.y*self.elasticity)
        
            if self.position.y < self.radius:
                self.position += Vec2(0, self.radius-self.position.y)+1e-6
            else:
                self.position -= Vec2(0, self.radius-(self.main.height-self.position.y))+1e-6
            
            
        if not self.main.width-self.radius >= self.position.x >= self.radius:
            self.velocity = Vec2(-self.velocity.x*self.elasticity, self.velocity.y*(1-self.friction))
            
            if self.position.x < self.radius:
                self.position += Vec2(self.radius-self.position.x, 0)+1e-6
            else:
                self.position -= Vec2(self.radius-(self.main.width-self.position.x), 0)+1e-6
            
            
        for i, ball in enumerate(self.main.sprites):
            if ball == self or i < self.main.sprites.index(self):
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
                