import pygame
import random as rand
from scipy.spatial import Voronoi, voronoi_plot_2d

class Drone():
    
    def __init__(self, game, n_drones):
        self.game = game
        self.cave = self.game.cave
        self.n_drones = n_drones
        
        # Get the initial points of the drones based on the status of the worms
        self.set_drone_initial_point()

        # List of colors for drones
        self.drone_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        # Run the main loop
        self.run()
        
    def set_drone_initial_point(self):
        good_point = False

        while not good_point:
            
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.initial_point = [self.cave.worm_x[i],self.cave.worm_y[i]]
            
            # Check if the point is white or black
            if self.cave.bin_map[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True

    def run(self):
        # Create n dot in the good position
        pass
