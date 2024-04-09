import pygame
from Assets import sqr, wall_hit

class Graph():
    def __init__(self, x_start, y_start, cave_mat):
        self.cave_mat = cave_mat

        # Initialise lists
        self.x        = []
        self.y        = []
        self.parent   = []
        self.pos      = []
        self.explored = []

        # Set start point
        self.x.append(x_start)
        self.y.append(y_start)
        self.parent.append(0)
        self.pos.append((x_start,y_start))
        self.explored.append(False)
    
    # Add the next node to the position and exploration lists
    def add_node(self, id, x, y):
        self.x.insert(id, x)
        self.y.insert(id, y)
        self.pos.insert(id, (x,y))
        self.explored.insert(id, False)

    # Remove the next node from the position and exploration lists
    def remove_node(self, id):
        self.x.pop(id)
        self.y.pop(id)
        self.pos.pop(id)
        self.explored.pop(id)

    # Add the next node to the parents list with its parent id as value
    def add_edge(self, id_child, id_parent):
        self.parent.insert(id_child, id_parent)

    # Remove the next node from the parents list
    def remove_edge(self, id_child):
        self.parent.pop(id_child)
    
    # Mark the node as fully explored
    # (No white pixels on the circumference of its area)
    def node_explored(self, id):
        self.explored[id] = True
    
    # Return the number of nodes in the graph
    def num_of_nodes(self):
        return len(self.x)
    
    # Return the euclidean distance between two nodes
    def distance(self, n1, n2):
        dx = sqr((float(self.x[n1]) - float(self.x[n2])))
        dy = sqr((float(self.y[n1]) - float(self.y[n2])))

        return (dx + dy)**0.5
    
    # Check if the last added node is valid (WHITE) and
    # if the connection with the second to last node crosses the cave walls
    def is_valid(self, surface, curr_pos, candidate_pos):
        if (pygame.Surface.get_at(surface, candidate_pos)[:3]==(0,0,0)
            and not self.cross_obs(*curr_pos, *candidate_pos)):
                return True
        return False
    
    # Check if the connection with the second to last node crosses the cave walls
    # using the Bresenham's line algorithm
    def cross_obs(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        sx = 1 if x1<x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1<y2 else -1

        error = dx + dy

        while True:
            if wall_hit(self.cave_mat, (x1, y1)):
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