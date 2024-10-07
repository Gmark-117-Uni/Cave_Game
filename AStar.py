from operator import attrgetter
import time
import math
import pygame
from Assets import Colors, wall_hit, check_pixel_color, zoom

class Node():
    def __init__(self, pos, parent=None):
        self.pos     = pos
        self.parent  = parent

        # F is the total cost of the node
        # G is the distance between the current node and the start node
        # H is the heuristic (estimated) distance from the current node to the end node
        # F = G + H
        self.f = 0
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        # Overwrite the == operator to confront positions when called on two nodes
        return self.pos == other.pos
    
    def __hash__(self):
        # Allows Node to be in a set
        return hash(self.pos)

class AStar():
    def __init__(self, surface, cave_matrix, color, game):
        self.game     = game
        self.surface  = surface
        self.cave     = cave_matrix
        self.color    = color
        self.deadline = 5
        
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)

        self.open   = []
        self.closed = set()

        # Surrounding pixels
        self.pos_modifiers = [(-1,-1), (0,-1), (1,-1),
                              (-1, 0),         (1, 0),
                              (-1, 1), (0, 1), (1, 1),]

    def clear(self):
        # When a path is found reset the variables
        self.open.clear()
        self.closed.clear()

        self.start_node = None
        self.goal_node  = None
        
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
    
    def find_path(self, start, border):
        # Define Start and End nodes
        self.start_node = Node(start)

        # Add the Start node to the open list
        self.open.append(self.start_node)

        # Loop until you run out of time (5 sec), then change goal
        iteration = -1
        while True:
            # If last border pixel was not reached in time
            iteration += 1
            # Choose the next closest one
            goal = border[iteration]
            self.goal_node  = Node(goal)

            # Start timer
            #tic = time.perf_counter()

            # Loop until you find the End node
            while self.open:
                # Let the current node be the one with the minimum value of F
                # Remove it from the open list and add it to the closed list
                curr_node = min(self.open, key=attrgetter('f'))
                self.open.remove(curr_node)
                self.closed.add(curr_node)

                # If the currrent node is the goal...
                if curr_node == self.goal_node:
                    # ... reset the algorithm
                    self.clear()
                    # ... backtrack to find the optimal path
                    return self.backtrack(curr_node)
                
                # Let the nodes adjacent to the current one be its children
                self.find_children(curr_node)

                # Show the A* algorithm at work
                self.draw_process(curr_node)

                '''
                # Check timer
                toc = time.perf_counter()
                if toc - tic > self.deadline:
                    break
                '''
    
    def backtrack(self, curr_node):
        path = []
        current = curr_node

        # Reach the Start node through parenthood and record positions
        # (Start node has no parent)
        while current is not None:
            path.append(current.pos)
            current = current.parent
        
        # Return reversed path
        return path[::-1]

    def find_children(self, curr_node):
        children = []

        for i in self.pos_modifiers:
            # Calculate the child position
            child_pos = (curr_node.pos[0] + i[0], curr_node.pos[1] + i[1])

            # If the child is not walkable:
            if not self.is_valid(child_pos):
                # Skip it
                continue

            # Make the child a node
            children.append(Node(child_pos, curr_node))

        for child in children:
            # If the child has been already closed
            if child in self.closed:
                # Skip it
                continue

            # Calculate values for G, H, F
            D = 1
            D2 = 1
            dx = abs((child.pos[0] - self.goal_node.pos[0]))
            dy = abs((child.pos[1] - self.goal_node.pos[1]))
            child.g = curr_node.g + 1

            # HEURISTIC
            # Diagonal Distance
            child.h = D*(dx + dy) + (D2 - 2*D)*min(dx,dy)


            child.f = child.g + child.h

            # If the child is already in the open list with a lower G
            if len([open_node for open_node in self.open if child.pos == open_node.pos and child.g > open_node.g]) > 0:
                # Skip it
                continue
            
            # Add the child to the open list
            self.open.append(child)
    
    # Check if the child is valid (explored) and is not a wall
    def is_valid(self, pos):
        if ((check_pixel_color(self.surface, pos, Colors.WHITE.value, is_not=True)
             or self.in_white_border(pos))
             and not wall_hit(self.cave, pos)):
                return True
        
        return False
    
    def in_white_border(self, pos):
        # Allow A* to explore white pixels n steps beyond the colored area
        n = 100
        return True if math.dist(pos, self.goal_node.pos) <= n else False
    
    def draw_process(self, curr_node):
        for node in self.open:
            pygame.Surface.set_at(self.astar_surf, node.pos, (*Colors.RED.value, 255))
        for node in self.closed:
            pygame.Surface.set_at(self.astar_surf, node.pos, (*Colors.YELLOW.value, 255))

        pygame.draw.circle(self.astar_surf, (*Colors.BLACK.value, 255), curr_node.pos, 1)
        pygame.draw.circle(self.astar_surf, (*Colors.GREEN.value, 255), self.goal_node.pos, 5, 1)
        pygame.draw.circle(self.astar_surf, (*Colors.GREEN.value, 255), self.goal_node.pos, 1)

        self.game.window.blit(self.astar_surf, (0,0))
        #zoom(self.game.window, curr_node.pos, 10)