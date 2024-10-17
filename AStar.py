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

        self.f = 0
        self.g = 0
        self.h = 0
    
    def __eq__(self, other):
        # Overwrite the == operator to confront positions when called on two nodes
        return self.pos == other.pos
    
    def __hash__(self):
        # Allows Node to be in a set
        return hash(self.pos)
    
    # Nuovo metodo __lt__ per confrontare due nodi in base a f
    def __lt__(self, other):
        return self.f < other.f

class AStar():
    def __init__(self, surface, cave_matrix, color, game):
        self.game     = game
        self.surface  = surface
        self.cave     = cave_matrix
        self.color    = color
        self.deadline = 5
        
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)

        self.open   = []
        self.open_dict = {}  # Dictionary for optimizing the research
        self.closed = set()

        # Surrounding pixels
        self.pos_modifiers = [(-1,-1), (0,-1), (1,-1),
                              (-1, 0),         (1, 0),
                              (-1, 1), (0, 1), (1, 1)]

    def clear(self):
        # When a path is found reset the variables
        self.open.clear()
        self.open_dict.clear()  
        self.closed.clear()

        self.start_node = None
        self.goal_node  = None
        
        self.astar_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
    
    def find_path(self, start, border):
        # Define Start and End nodes
        self.start_node = Node(start)

        # Add the Start node to the priority queue
        heapq.heappush(self.open, (self.start_node.f, self.start_node))
        # And to te dictionary
        self.open_dict[self.start_node.pos] = self.start_node  

        # Loop until you run out of time (5 sec), then change goal
       
        # Choose the next closest one
        goal = border[0]
        self.goal_node  = Node(goal)

        # Loop until you find the End node
        while self.open:
            # Remove the node with the lowest cost from the open list
            curr_node = heapq.heappop(self.open)[1]
            
            # Remove curr_node from open_dict if present
            if curr_node.pos in self.open_dict:
                del self.open_dict[curr_node.pos]
            else:
                print(f"Error: {curr_node.pos} not found in open_dict!")
            
            # Add the current node to the closed list
            self.closed.add(curr_node)

            # Check if you have reached the goal
            if curr_node == self.goal_node:
                # Backtracking 
                return self.backtrack(curr_node)

            # Generate the children of the current node
            self.find_children(curr_node)

            # Show the process (slower, only for debugging)
            # self.draw_process(curr_node)
                
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
            D1 = 1  # Horizontal or vertical distance
            D2 = math.sqrt(2)  # Diagonal distance
            dx = abs(child.pos[0] - self.goal_node.pos[0])
            dy = abs(child.pos[1] - self.goal_node.pos[1])
            
            # H is the heuristic (estimated) distance from the current node to the end node
            child.h = D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy) 
            # G is the distance between the current node and the start node
            child.g = curr_node.g + 1
            # F is the total cost of the node 
            child.f = child.g + child.h  

            # If the node is already open with a better cost, ignore it
            if child.pos in self.open_dict:
                existing_node = self.open_dict[child.pos]
                if child.g >= existing_node.g:
                    continue  # Ignore the new node if it has a cost greater than or equal

                # Update the existing node without removing it from the open list
                existing_node.g = child.g
                existing_node.f = child.f
                existing_node.parent = curr_node  # Update the parent
                
            else:
                # Add the node to open and open_dict
                heapq.heappush(self.open, (child.f, child))
                self.open_dict[child.pos] = child
                # print(f"Aggiunto nodo: {child.pos} con g: {child.g}")
    
    # Check if the child is valid (explored) and is not a wall
    def is_valid(self, pos):
        # Check if the pixel at 'pos' is either white or the same color as the drone
        is_pixel_white = check_pixel_color(self.surface, pos, Colors.WHITE.value, is_not=True)
        is_pixel_drone_color = check_pixel_color(self.surface, pos, self.color, is_not=True)

        # A pixel is valid if it's either not white and not a wall or is the drone's color
        return (is_pixel_white or is_pixel_drone_color) and not wall_hit(self.cave, pos)
    
    
    def draw_process(self, curr_node):
        px_array = pygame.PixelArray(self.astar_surf)
        for _, node in self.open:
            px_array[node.pos[0], node.pos[1]] = Colors.RED.value
        for node in self.closed:
            px_array[node.pos[0], node.pos[1]] = Colors.YELLOW.value
        del px_array 

        pygame.draw.circle(self.astar_surf, (*Colors.BLUE.value, 255), curr_node.pos, 1)
        pygame.draw.circle(self.astar_surf, (*Colors.GREEN.value, 255), self.goal_node.pos, 5, 1)
        pygame.draw.circle(self.astar_surf, (*Colors.GREEN.value, 255), self.goal_node.pos, 1)

        self.game.window.blit(self.astar_surf, (0,0))