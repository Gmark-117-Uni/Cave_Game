import pygame
from Assets import sqr, wall_hit, check_pixel_color, Colors

class Graph():
    def __init__(self, x_start, y_start, cave_mat):
        self.cave_mat = cave_mat
        # Initialise positions list
        self.pos = []
        # Set start point
        self.pos.append((x_start,y_start))
    
    # Add the next node to the positions lists
    def add_node(self, pos):
        self.pos.append(pos)
    
    # Check if the last added node is valid (WHITE) and
    # if the connection with the second to last node crosses the cave walls
    def is_valid(self, surface, curr_pos, candidate_pos):
        if (check_pixel_color(surface, candidate_pos, Colors.WHITE.value)
            and not self.cross_obs(*curr_pos, *candidate_pos)):
                return True
        return False
    
    # Check if the connection with the second to last node crosses the cave walls
    # using the Bresenham's line algorithm
    def cross_obs(self, x1, y1, x2, y2):
        # Initialise deltas and directions
        dx = abs(x2 - x1)
        sx = 1 if x1<x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1<y2 else -1
        # Define error
        error = dx + dy

        while True:
            # Check for collision
            if wall_hit(self.cave_mat, (x1, y1)):
                return True

            # Check if the second node has been reached (No collisions)
            if x1==x2 and y1==y2: return False

            # Move to next pixel
            err2 = 2*error
            if err2 >= dy:
                if x1==x2: return False
                error += dy
                x1 += sx
            if err2 <= dx:
                if y1==y2: return False
                error += dx
                y1 += sy