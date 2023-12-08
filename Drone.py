import random as rand
from scipy.spatial import Voronoi, voronoi_plot_2d

class Drone():
    def __init__(self, game):
        self.game = game
        self.cave = self.game.cave_gen
    
    # Draw the drone on the map
    def draw_drone(self, pos):
        pass
