import pygame
from operator import attrgetter
from Assets import wall_hit

class Node():
    def __init__(self, pos, parent=None):
        self.pos     = pos
        self.parent = parent

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

class AStar():
    def __init__(self, surface, cave_matrix, color):
        self.surface = surface
        self.cave    = cave_matrix
        self.color   = color

        self.open   = []
        self.closed = []

    def clear(self):
        # When a path is found reset the variables
        self.open.clear()
        self.closed.clear()

        self.start_node = None
        self.goal_node  = None
    
    def find_path(self, start, goal):
        # Define Start and End nodes
        self.start_node = Node(start)
        self.goal_node  = Node(goal)

        # Add the Start node to the open list
        self.open.append(self.start_node)

        # Loop until you find the End node
        while self.open:
            # Let the current node be the one with the minimum value of F
            # Remove it from the open list and add it to the closed list
            curr_node = min(self.open, key=attrgetter('f'))
            self.open.remove(curr_node)
            self.closed.append(curr_node)

            # If the currrent node is the goal, backtrack to find the optimal path
            if curr_node == self.goal_node:
                # Reset the algorithm
                self.clear()

                return self.backtrack(curr_node)
            
            # Let the nodes adjacent to the current one be its children
            self.find_children(curr_node)
    
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

        # Surrounding pixels
        pos_modifiers = [(-1,-1), (0,-1), (1,-1),
                         (-1, 0),         (1, 0),
                         (-1, 1), (0, 1), (1, 1),]

        for i in pos_modifiers:
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
            child.g = curr_node.g + 1
            child.h = ((child.pos[0] - self.goal_node.pos[0]) ** 2) + ((child.pos[1] - self.goal_node.pos[1]) ** 2)
            child.f = child.g + child.h

            for open_node in self.open:
                # If the child is already in the open list with a lower G
                if child == open_node and child.g > open_node.g:
                    # Skip it
                    continue
            
            # Add the child to the open list
            self.open.append(child)
    
    # Check if the child is valid (explored) and is not a wall
    def is_valid(self, pos):
        if (pygame.Surface.get_at(self.surface, pos)[:3] == self.color
            and not wall_hit(self.cave, pos)):
                return True
        return False