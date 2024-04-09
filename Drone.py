import pygame
import random as rand
import time
from Assets import next_cell_coords
from Graph import Graph

class Drone():
    def __init__(self, game, manager, id, start_pos, color, icon, cave):
        self.game         = game
        self.settings     = game.sim_settings
        self.cave         = cave
        self.manager      = manager

        self.id           = id
        self.radius       = 39   # TO BE CALCULATED BASED ON MAP DIMENSION
        self.step         = int(self.radius) + 1

        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        self.floor_surf   = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        
        self.node_history = []
        self.pos          = start_pos
        self.graph        = Graph(*start_pos, cave)

        self.steps_back   = 0

    # Calculate the next position of the drone
    def move(self, node_id):
        # Record id of current position to the history
        self.node_history.append(self.graph.pos.index(self.pos))

        node_found = False
        while not node_found:
            try:
                # Find all valid directions
                dirs, targets = self.find_new_node()
            except AssertionError:
                # If there are none, climb the graph
                self.retrace()
                # Show the steps of the retracing process
                self.draw_retracing()
            else:
                # Otherwise move in one of the valid directions
                node_found = self.explore(node_id, dirs, targets)
                self.steps_back = 0
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
            targets[i][0], targets[i][1] = next_cell_coords(*self.pos, self.step, i*dir_res)

            # If the target is a white pixel:
            if not self.graph.is_valid(self.floor_surf, self.pos, (*targets[i],)):
                # Add the direction to the blacklist
                dir_blacklist.append(i)

        # Filter the directions through the blacklist
        valid_dirs = [dir for dir in all_dirs if dir not in dir_blacklist]
        
        # If there is at least one dir left to be explored
        assert valid_dirs

        return valid_dirs, targets

    def explore(self, node_id, dirs, targets):
        # Choose a random valid direction and add the target to the graph
        chosen_dir = rand.choice(dirs)
        self.graph.add_node(node_id, *targets[chosen_dir])
        self.graph.add_edge(node_id, self.node_history[-1])
        self.pos = *targets[chosen_dir],
        dirs.remove(chosen_dir)

        # If it's the last direction mark the node as explored
        if not dirs:
            self.graph.node_explored(node_id)
        
        return True
    
    def retrace(self):
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        # retrace the tree to find the last node with explorable directions
        self.steps_back += 1

        self.pos = self.graph.pos[self.node_history[-self.steps_back*2]]
        self.node_history.append(self.graph.pos.index(self.pos))
    
    def mission_completed(self):
        # THIS METHOD WILL BE MOVED TO THE MANAGERS
        # Check all nodes for white pixels around them
        # If there are none, MISSION COMPLETED
        for explored in self.graph.explored:
            if not explored:
                return False
            
        return True
    
    def get_pos_history(self):
        pos_hist = []
        for i in self.node_history:
            pos_hist.append(self.graph.pos[i])
        return pos_hist

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
        # Draw a node on every position in history
        for i in range(len(self.node_history)):
            pygame.draw.circle(self.floor_surf, (*self.color, 255),
                               self.graph.pos[self.node_history[i]], 5)
            # Draw an edge between positions given the order of visitation
            if i>0:
                pygame.draw.line(self.floor_surf, (*self.color, 255),
                                 self.graph.pos[self.node_history[i]],
                                 self.graph.pos[self.node_history[i-1]], 2)

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
        time.sleep(0.25)