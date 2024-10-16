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
         
        self.id           = id # unique identifier of the drone
        print(self.id)
        self.map_size     = self.settings[1] # map dimension
        self.radius       = self.calculate_radius() # radius that represent the field of view # 39
        self.step         = 10 # step of the drone
        self.dir          = rand.randint(0,359)

        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        
        # transparent surface used to track the explored path
        self.floor_surf   = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        self.floor_surf.fill((*Colors.WHITE.value, 0))
        self.ray_points = []  # Initialize the list for rays
        self.delay        = self.manager.delay

        self.show_path    = True
        self.target_practice = False
         
        self.border       = []
        self.start_pos    = start_pos
        self.pos          = start_pos
        self.dir_log      = []
        self.graph        = Graph(*start_pos, cave)
        self.astar        = AStar(self.floor_surf, cave, self.color, self.game)

    # Define the radius based on the map size
    def calculate_radius(self):
        print(self.map_size)
        if   self.map_size == 'SMALL':  # Small map
            return 40  
        elif self.map_size == 'MEDIUM':  # Medium map
            return 20  
        elif self.map_size == 'BIG':  # Large map
            return 10  
        else:
            return 20  # Default value in case of unknown size
        
    # Manage the movement of the drone
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
            else:
                # Otherwise move in one of the valid directions
                node_found = self.explore(valid_dirs, valid_targets)
    
    # Find a valid direction around the drone
    def find_new_node(self):
        # Model a 360° RADAR scan (or 3 120° LIDAR scan)
        directions = 360

        # Calculate next position and record unexplored directions for current position
        all_dirs = list(range(directions)) # How many directions can it take
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

    # DA MODIFICARE
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
    
    # no free directions -> use A* 
    def reach_border(self):
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        # use the A* algorithm to reach the closest border pixel
        
        # Clear the state of the A* algorithm
        self.astar.clear()
        
        # Sort the border pixels by distance from current position
        self.border.sort(key=self.get_distance)
       
        self.target_practice = True
        self.draw_astar()

        # Find the optimal path through the A* algorithm
        path = self.astar.find_path(self.pos, self.border)

        # Move the drone
        for node in path:
            self.pos = node
            # Update graph
            self.graph.add_node(node)
            # Display the step
            self.draw_astar()
            self.target_practice = False
        
        return True
    
    def update_borders(self):
        # If a pixel in the border list is still white, keep it
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
        pygame.draw.polygon(self.floor_surf, (*self.color, int(2*self.alpha/3)), self.ray_points)  
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

        # Draw the A* target
        #self.astar_target_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        #pygame.draw.circle(self.astar_target_surf, (*Colors.GREEN.value, 255), (6,6), 6)

        # Blit the color surface onto the target surface
        self.game.window.blit(self.floor_surf, (0,0))
        # Blit the circle at the starting position
        self.game.window.blit(self.start_surf, (self.start_pos[0] - 6, self.start_pos[1] - 6))
        
        # Blit the A* target
        # if self.target_practice:
            # self.game.window.blit(self.astar_target_surf, (self.border[0][0] - 6, self.border[0][1] - 6))
    
            
    def cast_ray(self, start_pos, angle, max_length):
        step_size = 2  # Higher precision reduces the step size
        for length in range(0, max_length, step_size):
            end_x = start_pos[0] + length * math.cos(angle)
            end_y = start_pos[1] + length * math.sin(angle)

            # Ensure the point is within the window bounds
            if 0 <= end_x < self.game.window.get_width() and 0 <= end_y < self.game.window.get_height():
                pixel_color = self.game.window.get_at((int(end_x), int(end_y)))
                # Check for wall color
                if pixel_color == (0, 0, 0, 255):  # Assuming black color in RGBA
                    return (end_x, end_y)

            # Break if out of bounds
            if not (0 <= end_x < self.game.window.get_width() and 0 <= end_y < self.game.window.get_height()):
                break
        return None

    # Draw the area the sensors on the drone can see
    def draw_vision(self):
        num_rays = 100  # Number of rays to cover 360 degrees
        angle_increment = 2 * math.pi / num_rays  # Angular increment in radians
        self.ray_points.clear()  # Clear the points of the existing rays

        for i in range(num_rays):
            angle = i * angle_increment  # Calculate the current angle
            intersection = self.cast_ray(self.pos, angle, self.radius)  # Use the drone's position

            if intersection:
               self.ray_points.append(intersection)  # Add the intersection point
            else:
                # If there are no intersections, add the final point of the ray
                end_x = self.pos[0] + self.radius * math.cos(angle)
                end_y = self.pos[1] + self.radius * math.sin(angle)
                self.ray_points.append((end_x, end_y))  # Add the final point of the ray

        # Draw the colored circle if there are points
        if len(self.ray_points) > 2:  # Make sure there are at least 3 points to form a polygon
            pygame.draw.polygon(self.game.window, (*self.color, int(2*self.alpha/3)), self.ray_points)  
        else:
            # Draw a simple circle or an indication of no vision
            pygame.draw.circle(self.game.window, (*self.color, int(2*self.alpha/3)), (int(self.pos[0]), int(self.pos[1])), self.radius, 1)
      
    # Draw the drone icon
    def draw_icon(self):
        # Blit the drone at the initial point
        self.game.window.blit(self.icon, self.center_drawing(self.icon.get_width(), self.icon.get_height()))
    
    # Calculate the topleft based on the object dimensions so that the drawing is centered
    def center_drawing(self, width, height):
        return (self.pos[0] - width/2, self.pos[1] - height/2)
    
    # Manage drawings during the A* algorithm phase
    def draw_astar(self):
        self.manager.draw_cave()
        self.manager.draw()
        pygame.display.update()
        time.sleep(self.delay)
