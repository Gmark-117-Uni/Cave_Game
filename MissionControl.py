import random as rand
from DroneManager import DroneManager
from RoverManager import RoverManager
import pygame
import Assets

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[2])

        self.game = game
        self.settings = game.sim_settings
        self.cave_gen = game.cave_gen
        self.cave_map = self.cave_gen.bin_map
        
        # Find a suitable start position
        self.set_initial_point()
        # Start mission
        self.start_mission()

    def start_mission(self):
        # Create the drones 
        self.drone_manager = DroneManager(self.game, self.initial_point)
        
        # Maximise the game window
        self.game.display = self.game.to_maximised()
        
        # Keep moving the drones
        while True:
            self.drone_manager.step()
            #self.rover_manager.step()

            pygame.display.update()
        
    # Among the starting positions of the worms, find one that is viable
    def set_initial_point(self):
        good_point = False
        while not good_point:  
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.initial_point = (self.cave_gen.worm_x[i],self.cave_gen.worm_y[i])
            # Check if the point is white or black
            if self.cave_map[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True
