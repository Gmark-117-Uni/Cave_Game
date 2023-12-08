import random as rand
from scipy.spatial import Voronoi, voronoi_plot_2d

class Rover():
    def __init__(self, game):
        self.game = game
        self.cave = self.game.cave_gen
        
        # Get the initial points of the rovers
        self.set_rover_initial_point()
        
    def set_rover_initial_point(self):
        good_point = False
        while not good_point:
            
            # Take one of the initial points of the worms as initial point for the rover
            i = rand.randint(0,3)
            self.initial_point = [self.cave.worm_x[i],self.cave.worm_y[i]]
            
            # Check if the point is white or black
            if self.cave.bin_map[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True
    
    # Draw the drone on the map
    def draw_rover(self, pos):
        pass
