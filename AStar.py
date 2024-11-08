from operator import attrgetter
import time
import math
import pygame
import heapq
from Assets import Colors, wall_hit, check_pixel_color

class Node():
    def __init__(self, pos, parent=None):
        self.pos     = pos
        self.parent  = parent
        
        # f: total cost, g: cost from start, h: heuristic
        self.f = 0
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        # Overwrite the == operator to compare node positions
        return self.pos == other.pos
    
    def __hash__(self):
        # Allows Node to be used in a set or as a dictionary key
        return hash(self.pos)
    
    def __lt__(self, other):
        # method to compare two nodes based on their 'f' attribute
        # (used in priority queue)
        return self.f < other.f

class AStar():
    def __init__(self, surface, cave_matrix, color, game):
        self.game     = game
        self.surface  = surface
        self.cave     = cave_matrix
        self.color    = color
        
        # Create a transparent surface for A* visualization
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)

        # Initialize lists and sets for open and closed nodes
        self.open   = []
        self.open_dict = {}  # Dictionary for optimizing the research
        self.closed = set()

        # Surrounding pixels (8 possible directions)
        self.pos_modifiers = [(-1,-1), (0,-1), (1,-1),
                              (-1, 0),         (1, 0),
                              (-1, 1), (0, 1), (1, 1)]

    def clear(self):
        # Reset variables when a new pathfinding operation begins
        self.open.clear()
        self.open_dict.clear()  
        self.closed.clear()
        # Reset the start and goal nodes
        self.start_node = None
        self.goal_node  = None
        # Reinitialize the visualization surface
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
    
    def find_path(self, start, border):
        # Initialize the start node and add it to the priority queue (open list) and open_dict
        self.start_node = Node(start)
        heapq.heappush(self.open, (self.start_node.f, self.start_node))
        self.open_dict[self.start_node.pos] = self.start_node  

        # Set the goal node (assumes first item in border as the goal)
        goal = border[0]
        self.goal_node  = Node(goal)

        # Main A* loop until the goal is found or the open list is empty
        while self.open:
            # Get the node with the lowest cost (f-value) from the priority queue
            curr_node = heapq.heappop(self.open)[1]
            
            # Remove the current node from the dictionary if it's still present
            if curr_node.pos in self.open_dict:
                del self.open_dict[curr_node.pos]
            else:
                print(f"Error: {curr_node.pos} not found in open_dict!")
            
            # Add the current node to the closed set (it has been fully explored)
            self.closed.add(curr_node)

            # Check if the goal has been reached
            if curr_node == self.goal_node:
                # If goal is reached, backtrack to reconstruct the path
                return self.backtrack(curr_node)

            # Generate children (neighboring nodes) of the current node
            self.find_children(curr_node)

            # Optional: visualize the process (useful for debugging)
            # self.draw_process(curr_node)
                
    def backtrack(self, curr_node):
        # Backtrack from the goal node to the start node to reconstruct the path
        path = []
        current = curr_node
        
        # Follow parent links to trace the path back to the start
        while current is not None:
            path.append(current.pos)
            current = current.parent
        # Reverse the path (from start to goal) and return it
        return path[::-1]

    def find_children(self, curr_node):
        # Find and generate valid child nodes for the current node
        children = []
        # Loop through each possible direction (8 neighbors)
        for i in self.pos_modifiers:
            # Calculate the child position
            child_pos = (curr_node.pos[0] + i[0], curr_node.pos[1] + i[1])

            # Check if the child position is walkable (not a wall or out of bounds)
            if not self.is_valid(child_pos):
                # Skip if the position is invalid
                continue

            # Create a new node for the child and link it to the current node (parent)
            children.append(Node(child_pos, curr_node))

        # For each valid child node, evaluate its cost and add it to the open list
        for child in children:
            
            # If the child node is already in the closed set, skip it
            if child in self.closed:
                continue

            # Calculate the g, h, and f values for the child
            D1 = 1  # Cost for moving horizontally/vertically
            D2 = math.sqrt(2)  # Cost for moving diagonally
            dx = abs(child.pos[0] - self.goal_node.pos[0])
            dy = abs(child.pos[1] - self.goal_node.pos[1])
            
            # Calculate heuristic (h) using Manhattan distance with diagonal movements
            child.h = D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy) 
            # g is the cost from the start node to the current node
            child.g = curr_node.g + 1
            # f is the total cost (g + h)
            child.f = child.g + child.h  

            # Check if the child is already in the open list with a lower cost
            if child.pos in self.open_dict:
                existing_node = self.open_dict[child.pos]
                if child.g >= existing_node.g:
                    # Skip if the new path to the node is not better
                    continue    
                
                # Update the existing node's cost and parent
                existing_node.g = child.g
                existing_node.f = child.f
                existing_node.parent = curr_node  
                
            else:
                # Add the new child node to the open list and dictionary
                heapq.heappush(self.open, (child.f, child))
                self.open_dict[child.pos] = child
    
    # Check if a given position is walkable (not a wall or obstacle)
    def is_valid(self, pos):
        # Check if the pixel at 'pos' is either white or the same color as the drone
        is_pixel_white = check_pixel_color(self.surface, pos, Colors.WHITE.value, is_not=True)
        is_pixel_drone_color = check_pixel_color(self.surface, pos, self.color, is_not=True)

        # A pixel is valid if it's either not white and not a wall or is the drone's color
        return (is_pixel_white or is_pixel_drone_color) and not wall_hit(self.cave, pos)