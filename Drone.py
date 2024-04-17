import pygame
import random as rand
import time
import math
from Assets import next_cell_coords
from Graph import Graph
from AStar import AStar

class Drone():
    def __init__(self, game, manager, id, start_pos, color, icon, cave):
        self.game         = game
        self.settings     = game.sim_settings
        self.cave         = cave
        self.manager      = manager

        self.id           = id
        self.radius       = 39   # TO BE CALCULATED BASED ON MAP DIMENSION
        self.step         = 10

        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        self.floor_surf   = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        self.delay        = self.manager.delay

        self.show_path    = True
        
        self.border       = []
        self.pos          = start_pos
        self.graph        = Graph(*start_pos, cave)
        self.astar        = AStar(self.floor_surf, cave, self.color)

    # Calculate the next position of the drone
    def move(self):
        node_found = False
        while not node_found:
            try:
                # Find all valid directions
                valid_dirs, valid_targets = self.find_new_node()
            except AssertionError:
                # Update borders
                self.update_borders()
                # If there are no valid directions, find the closest border
                self.reach_border()
                # End step
                node_found = True
            else:
                # Otherwise move in one of the valid directions
                node_found = self.explore(valid_dirs, valid_targets)
                # Clean screen after showing the retracing steps
                self.manager.draw_cave()
    
    def find_new_node(self):
        # Calculate next position and record unexplored directions for current position
        all_dirs = list(range(360))    # How many directions can it take
        targets  = []
        dir_res  = int(360/len(all_dirs))

        for i in range(len(all_dirs)):
            targets.append([0,0])

        dir_blacklist = []
        for i in all_dirs:
            # Find the target pixel in that direction
            targets[i][0], targets[i][1] = next_cell_coords(*self.pos, self.radius + 1, i*dir_res)

            # If the target is a white pixel:
            if not self.graph.is_valid(self.floor_surf, self.pos, (*targets[i],)):
                # Add the direction to the blacklist
                dir_blacklist.append(i)

        # Filter the directions through the blacklist
        valid_dirs    = [dir for dir in all_dirs if dir not in dir_blacklist]
        valid_targets = [(*targets[valid_dir],) for valid_dir in valid_dirs]
        
        # If there is at least one dir left to be explored
        assert valid_dirs

        return valid_dirs, valid_targets

    def explore(self, valid_dirs, valid_targets):
        # Choose a random valid direction
        chosen_dir = rand.choice(valid_dirs)
        target = next_cell_coords(*self.pos, self.step, chosen_dir)

        # Add the target to the graph
        self.graph.add_node(target)

        # Update position
        self.pos = target

        # Remove explored direction
        valid_dirs.remove(chosen_dir)

        # Add unexplored pixels to the border list (ONLY ONE TIME EACH)
        self.border.extend(valid_targets)
        self.border = list(set(self.border))
        
        return True
    
    def reach_border(self):
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        # use the A* algorithm to reach the closest border pixel
        
        # Find the closest border
        goal = min(self.border, key=self.get_distance)

        # Find the optimal path through the A* algorithm
        path = self.astar.find_path(self.pos, goal)

        # Move the drone
        for node in path:
            self.pos = node
            # Update graph
            self.graph.add_node(node)
            # Display the step
            self.draw_retracing()
    
    def update_borders(self):
        # If a border pixel has been explored (is colored) remove it from the border
        for i in self.border:
            if pygame.Surface.get_at(self.floor_surf, i)[:3] != (0,0,0):
                self.border.remove(i)
    
    def mission_completed(self):
        # Check if the border pixels list is empty
        # If it is: MISSION COMPLETED!
        return bool(self.border)
    
    def get_distance(self, target):
        # Find the distance between the actual position and the given target position
        return math.dist(self.pos, target)

    def update_explored_map(self):
        pass


#  ____   ____      _  __        __ ___  _   _   ____ 
# |  _ \ |  _ \    / \ \ \      / /|_ _|| \ | | / ___|
# | | | || |_) |  / _ \ \ \ /\ / /  | | |  \| || |  _
# | |_| ||  _ <  / ___ \ \ V  V /   | | | |\  || |_| |
# |____/ |_| \_\/_/   \_\ \_/\_/   |___||_| \_| \____|

    # Draw the explored area of the drone
    def draw_path(self):
        # Draw a circle on every position in history
        for i in self.graph.pos:
            pygame.draw.circle(self.floor_surf, (*self.color, int(2*self.alpha/3)), i, self.radius)
        if self.show_path:
            # Draw a node on every position in history
            for i in range(len(self.graph.pos)):
                if i>0:
                    pygame.draw.line(self.floor_surf, (*self.color, 255),
                                     self.graph.pos[i],
                                     self.graph.pos[i-1], 2)

        # Blit the color surface onto the target surface
        self.game.window.blit(self.floor_surf, (0,0))

    # Draw the area the sensors on the drone can see
    def draw_vision(self):
        # Create a surface to draw the circle (                  dimensions, activate transprancy)
        self.circle_surface = pygame.Surface((self.radius*2, self.radius*2),      pygame.SRCALPHA)
        
        # Draw the circle (            surface,              color, center of the circle on the surface,      radius)
        pygame.draw.circle(self.circle_surface, (*self.color, 200),           (self.radius,self.radius), self.radius)

        # Blit the circle at the initial point
        self.game.window.blit(self.circle_surface, self.center_drawing(self.radius*2,self.radius*2))

    # Draw the drone icon
    def draw_icon(self):
        # Blit the drone at the initial point
        self.game.window.blit(self.icon, self.center_drawing(self.icon.get_width(), self.icon.get_height()))
    
    # Calculate the topleft based on the object dimensions so that the drawing is centered
    def center_drawing(self, width, height):
        return (self.pos[0] - width/2, self.pos[1] - height/2)
    
    def draw_retracing(self):
        self.manager.draw_cave()
        self.manager.draw()
        pygame.display.update()
        time.sleep(self.delay)