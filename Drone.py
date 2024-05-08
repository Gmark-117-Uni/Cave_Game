import pygame
import random as rand
import time
import math
from Assets import next_cell_coords, check_pixel_color, Colors
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
        self.dir          = rand.randint(0,359)

        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        self.floor_surf   = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        self.floor_surf.fill((*Colors.WHITE.value, 0))
        self.delay        = self.manager.delay

        self.show_path    = True
        
        self.border       = []
        self.start_pos    = start_pos
        self.pos          = start_pos
        self.dir_log      = []
        self.graph        = Graph(*start_pos, cave)
        self.astar        = AStar(self.floor_surf, cave, self.color, self.game)

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
                # If there are no valid directions, find the closest border and end step
                node_found = self.reach_border()
                # Clean screen after showing the retracing steps
                #self.manager.draw_cave()
            else:
                # Otherwise move in one of the valid directions
                node_found = self.explore(valid_dirs, valid_targets)
    
    def find_new_node(self):
        # Model a 360° RADAR scan or a 120° LIDAR scan
        directions = 360 if self.settings[4] == 0 else 120

        # Calculate next position and record unexplored directions for current position
        all_dirs = list(range(directions))    # How many directions can it take
        targets  = []
        dir_res  = int(360/len(all_dirs))

        for _ in range(len(all_dirs)):
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
        
        ####################################################################################################################
        # TO DO NEXT
        # radar and lidar are atually one function
        # next_cell_coords needs to be followed by cross_obs with pixel logging to draw the lines
        ####################################################################################################################

    def explore(self, valid_dirs, valid_targets):
        # Choose a random valid direction
        self.dir = rand.choice(valid_dirs)
        target = next_cell_coords(*self.pos, self.step, self.dir)
        
        # Log the direction chosen
        self.dir_log.append(self.dir)

        # Add the target to the graph
        self.graph.add_node(target)

        # Update position
        self.pos = target

        # Remove explored direction
        valid_dirs.remove(self.dir)

        # Add unexplored pixels to the border list (ONLY ONE TIME EACH)
        self.border.extend(valid_targets)
        self.border = list(set(self.border))
        
        return True
    
    def reach_border(self):
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        # use the A* algorithm to reach the closest border pixel

        # Sort the border pixels by distance from current position
        self.border.sort(key=self.get_distance)

        # Find the optimal path through the A* algorithm
        path = self.astar.find_path(self.pos, self.border)

        # Move the drone
        for node in path:
            self.pos = node
            # Update graph
            self.graph.add_node(node)
            # Display the step
            self.draw_astar()
        
        return True
    
    def update_borders(self):
        # If a border pixel has been explored (is colored) or is surrounded by explored pixels, remove it
        self.border = [pixel for pixel in self.border if check_pixel_color(self.floor_surf, pixel, self.color, is_not=True)]

    def mission_completed(self):
        # Check if the border pixels list is empty
        # If it is: MISSION COMPLETED!
        return bool(self.border)
    
    def get_distance(self, target):
        # Find the distance between the actual position and the given target position
        dist = math.dist(self.pos, target)

        # Discard targets within the current vision circle
        return self.game.width if dist <= self.radius else dist

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
        # Draw the starting point
        self.start_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.start_surf, (*Colors.BLUE.value, 255), (6,6), 6)

        # Blit the color surface onto the target surface
        self.game.window.blit(self.floor_surf, (0,0))
        # Blit the circle at the starting position
        self.game.window.blit(self.start_surf, (self.start_pos[0] - 6, self.start_pos[1] - 6))

    # Draw the area the sensors on the drone can see
    def draw_vision(self):
        # Create a surface to draw the circle (                  dimensions, activate transprancy)
        self.circle_surface = pygame.Surface((self.radius*2, self.radius*2),      pygame.SRCALPHA)
        
        # Draw the circle (            surface,                              color, center of the circle on the surface,      radius)
        pygame.draw.circle(self.circle_surface, (*self.color, int(2*self.alpha/3)),           (self.radius,self.radius), self.radius)

        # Blit the circle at the current position
        self.game.window.blit(self.circle_surface, self.center_drawing(self.radius*2,self.radius*2))

    # Draw the drone icon
    def draw_icon(self):
        # Blit the drone at the initial point
        self.game.window.blit(self.icon, self.center_drawing(self.icon.get_width(), self.icon.get_height()))
    
    # Calculate the topleft based on the object dimensions so that the drawing is centered
    def center_drawing(self, width, height):
        return (self.pos[0] - width/2, self.pos[1] - height/2)
    
    # Manage drawings during the A* algrithm phase
    def draw_astar(self):
        self.manager.draw_cave()
        self.manager.draw()
        pygame.display.update()
        time.sleep(self.delay)