import pygame
import Assets
from ModeExploration import ModeExploration
from ModeSearchNRescue import ModeSearchNRescue

class Drone():
    def __init__(self, game, id, start_pos, color, icon, explorer):
        self.game         = game
        self.settings     = game.sim_settings
        self.explorer     = explorer
        self.id           = id
        self.radius       = 40   # TO BE CALCULATED BASED ON MAP DIMENSION
        self.step         = int(self.radius/8)
        self.pos          = start_pos
        self.color        = color
        self.alpha        = 150
        self.icon         = icon
        self.pos_history  = []
        
        # Calculate next position
        self.next_pos, self.unexplored_dirs = self.explorer.next_pos(self.id, self.pos, self.step)

    # Calculate the next position of the drone
    def move(self):
        # Record old positions
        self.pos_history.append(self.pos)
        
        # Update position
        self.pos = self.next_pos

        # Calculate next position and record unexplored directions for current position
        self.next_pos, self.unexplored_dirs = self.explorer.next_pos(self.id, self.pos, self.step)
    
    def get_pos_history(self):
        pass

    def update_explored_map(self):
        pass


#  ____   ____      _    __        __ ___  _   _   ____ 
# |  _ \ |  _ \    / \   \ \      / /|_ _|| \ | | / ___|
# | | | || |_) |  / _ \   \ \ /\ / /  | | |  \| || |  _
# | |_| ||  _ <  / ___ \   \ V  V /   | | | |\  || |_| |
# |____/ |_| \_\/_/   \_\   \_/\_/   |___||_| \_| \____|

    # Draw the explored area of the drone
    def draw_path(self):
        self.floor_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)

        # Draw a circle on every position in history
        for i in range(len(self.pos_history)):
            pygame.draw.circle(self.floor_surf, (*self.color, int(2*self.alpha/3)), self.pos_history[i], self.radius)

        # Blit the color surface onto the target surface
        self.game.window.blit(self.floor_surf, (0,0))

    # Draw the area the sensors on the drone can see
    def draw_vision(self):
        # Create a surface to draw the circle (                  dimensions, activate transprancy)
        self.circle_surface = pygame.Surface((self.radius*2, self.radius*2),      pygame.SRCALPHA)
        
        # Draw the circle (            surface,              color, center of the circle on the surface,      radius)
        pygame.draw.circle(self.circle_surface, (*self.color, 255),           (self.radius,self.radius), self.radius)

        # Blit the circle at the initial point
        self.game.window.blit(self.circle_surface, self.center_drawing(self.radius*2,self.radius*2))

    # Draw the drone icon
    def draw_icon(self):
        # Blit the drone at the initial point
        self.game.window.blit(self.icon, self.center_drawing(self.icon.get_width(), self.icon.get_height()))
    
    # Calculate the topleft based on the object dimensions so that the drawing is centered
    def center_drawing(self, width, height):
        return (self.pos[0] - width/2, self.pos[1] - height/2)
    