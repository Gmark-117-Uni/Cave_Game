import pygame
import random as rand
from Assets import next_cell_coords
from Graph import Graph

class Drone():
    def __init__(self, game, id, start_pos, color, icon, cave):
        self.game         = game
        self.settings     = game.sim_settings
        self.cave         = cave
        self.id           = id
        self.radius       = 39   # TO BE CALCULATED BASED ON MAP DIMENSION
        self.step         = int(self.radius) + 1
        self.pos          = start_pos
        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        self.node_history = []
        self.floor_surf   = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        self.graph        = Graph(*start_pos, cave)

    # Calculate the next position of the drone
    def move(self, node_id):
        # Record id of current position to the history
        self.node_history.append(self.graph.pos.index(self.pos))

        if not self.find_new_node(node_id):
            raise ValueError('Cul de sac!')
            #self.climb_tree()
    
    def find_new_node(self, node_id):
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

            # Add the target to the graph
            self.graph.add_node(node_id, *targets[i])

            # If the target is a white pixel:
            if self.graph.is_free(self.floor_surf):
                # Remove it from the graph and keep it among the possible directions
                self.graph.remove_node(-1)
            else:
                # Otherwise add the direction to the blacklist
                dir_blacklist.append(i)

        # Filter the directions through the blacklist
        dirs = [dir for dir in all_dirs if dir not in dir_blacklist]

        # If there is at least one dir left to be explored
        if dirs:
            # Choose a random valid direction and add the target to the graph
            chosen_dir = rand.choice(dirs)
            self.graph.add_node(node_id, *targets[chosen_dir])
            self.graph.add_edge(node_id, node_id-1)
            self.pos = *targets[chosen_dir],

            # If it's the last direction mark the node as explored
            if not dirs:
                self.graph.explored(node_id)

            return True
            
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        return False
    
    def climb_tree(self):
        pygame.event.wait(10)
    
    def mission_completed(self):
        # THIS METHOD WILL BE MOVED TO THE MANAGERS
        # Check all nodes for white pixels around them
        # If there are none, MISSION COMPLETED
        pass
    
    def get_pos_history(self):
        pos_hist = []
        for i in self.node_history:
            pos_hist.append(self.graph.pos[i])
        return pos_hist

    def update_explored_map(self):
        pass


#  ____   ____      _    __        __ ___  _   _   ____ 
# |  _ \ |  _ \    / \   \ \      / /|_ _|| \ | | / ___|
# | | | || |_) |  / _ \   \ \ /\ / /  | | |  \| || |  _
# | |_| ||  _ <  / ___ \   \ V  V /   | | | |\  || |_| |
# |____/ |_| \_\/_/   \_\   \_/\_/   |___||_| \_| \____|

    # Draw the explored area of the drone
    def draw_path(self):
        # Draw a circle on every position in history
        for i in self.node_history:
            pygame.draw.circle(self.floor_surf, (*self.color, int(2*self.alpha/3)), self.graph.pos[i], self.radius)
        # Draw a node on every position in history
        for i in self.node_history:
            if self.graph.is_free(self.floor_surf):
                pygame.draw.circle(self.floor_surf, (*self.color, 255), self.graph.pos[i], 5)
                if i>0 and not self.graph.cross_obs(*(self.graph.pos[i]), *(self.graph.pos[i-1])):
                    pygame.draw.line(self.floor_surf, (*self.color, 255), self.graph.pos[i], self.graph.pos[i-1], 2)

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
    