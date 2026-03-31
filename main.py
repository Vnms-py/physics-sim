import pyglet as pg
from pyglet.math import Vec2, Vec3
from random import randint
from colorsys import hls_to_rgb
from objects import Circle, Spring
from time import sleep


class Main:
    def __init__(self):
        self.screen = pg.display.get_display().get_default_screen()
        self.width, self.height = self.screen.width, self.screen.height
        self.window = pg.window.Window(self.width, self.height, fullscreen = True)
        self.batch = pg.graphics.Batch()
        self.precision = 4
        self.g = 40
        self.sprites=[]
        self.connections = []
        main = self
        

        self.window.push_handlers(self)
        
        
        # x, y, radius, mass, vel_x, vel_y, color
        grid = 7
        for i in range(1, grid+1):
            for j in range(1, grid+1):
                hls =  hls_to_rgb((i-1)/5, .5, .5)
                col = tuple(int(255*c) for c in hls)
                
                # self.sprites += [Circle(main, randint(0, self.width), randint(0, self.height), 20, 1, i**3, i**3, col)]
                self.sprites += [Circle(main, 160*j, 160*i, 20, 1, (j-1), 0, col)]

        # 1, 2, 3
        # 4, 5, 6
        # 7, 8, 9
        
        for k in range(len(self.sprites)):
            for l in range(len(self.sprites)):
                if  k >= l:
                    continue
                
                node1, node2 = self.sprites[k], self.sprites[l]
                length = ((node2.ball.x-node1.ball.x)**2+(node2.ball.y-node1.ball.y)**2)**(1/2)
                if length >= 320:
                    continue
                
                self.connections += [Spring(main, node1, node2, length, 64)]
                # self.connections += [Spring(main, self.sprites[1], self.sprites[2], 400, 1)]
        
    def sim(self, dt):
        for sprite in self.sprites:
            sprite.move(dt)
            
        for group in self.connections:
            group.pull()
    
    
    def on_draw(self):
        self.window.clear()
        self.batch.draw()
        
        
    

main=Main()
fps = 30


pg.clock.schedule_interval(main.sim, 1/fps)
pg.app.run()