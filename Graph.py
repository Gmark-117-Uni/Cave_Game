import pygame
from Assets import sqr

class Graph():
    def __init__(self, surface, x_start, y_start, explorer):
        self.surface  = surface
        self.explorer = explorer
        self.x = []
        self.y = []
        self.parent = []
        self.is_explored = []

        self.x.append(x_start)
        self.y.append(y_start)
        self.parent.append(0)
    
    def draw(self, color):
        pass
    
    def add_node(self, id, x, y):
        self.x.insert(id, x)
        self.y.insert(id, y)

    def remove_node(self, id):
        self.x.pop(id)
        self.y.pop(id)

    def add_edge(self, id_child, id_parent):
        self.parent.insert(id_child, id_parent)

    def remove_edge(self, id_child):
        self.parent.pop(id_child)
    
    def num_of_nodes(self):
        return len(self.x)
    
    def distance(self, n1, n2):
        dx = sqr((float(self.x[n1]) - float(self.x[n2])))
        dy = sqr((float(self.y[n1]) - float(self.y[n2])))

        return (dx + dy)**0.5
    
    def is_free(self, surface):
        if (pygame.Surface.get_at(surface, (self.x[-1], self.y[-1]))[:3]==(0,0,0)
            and not self.cross_obs(self.x[-2], self.y[-2], self.x[-1], self.y[-1])):
                return True
        self.remove_node(-1)
        return False
    
    def cross_obs(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        sx = 1 if x1<x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1<y2 else -1

        error = dx + dy

        while True:
            if self.explorer.wall_hit((x1, y1)):
                return True

            if x1==x2 and y1==y2: return False
            err2 = 2*error
            if err2 >= dy:
                if x1==x2: return False
                error += dy
                x1 += sx
            if err2 <= dx:
                if y1==y2: return False
                error += dx
                y1 += sy
    
    def connect(self, n1, n2):
        x1, y1 = self.x[n1], self.y[n1]
        x2, y2 = self.x[n2], self.y[n2]
        if self.cross_obs(self.surface, x1, y1, x2, y2):
            self.remove_node(n2)
            return False
        else:
            self.add_node(n2)
            return True