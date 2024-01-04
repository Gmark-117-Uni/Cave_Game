import random as rand
import pygame
import time
import Assets
from DroneManager import DroneManager
#from RoverManager import RoverManager
from ModeExploration import ModeExploration
from ModeSearchNRescue import ModeSearchNRescue

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[2])

        self.game = game
        self.settings = game.sim_settings
        self.cartographer = game.cartographer
        self.map_matrix = self.cartographer.bin_map
        self.surface  = game.display
        
        # Find a suitable start position
        self.set_initial_point()

        # Instantiate explorer
        # EXPLORATION is 0 / Search&Rescue is 1
        match self.settings[0]:
            case 0: self.explorer = ModeExploration(self.map_matrix, self.surface)
            case 1: self.explorer = ModeSearchNRescue(self.map_matrix, self.surface)

        # Start mission
        self.start_mission()

    # Mission loop
    def start_mission(self):
        # Maximise the game window
        self.game.display = self.game.to_maximised()

        # Create the drones 
        self.drone_manager = DroneManager(self.game, self.initial_point, self.explorer)
        
        pygame.display.update()
        time.sleep(1)

        # Keep moving the drones until the explorer says otherwise
        while not self.explorer.mission_completed():
            self.drone_manager.step()
            #self.rover_manager.step()

            pygame.display.update()
        
    # Among the starting positions of the worms, find one that is viable
    def set_initial_point(self):
        good_point = False
        while not good_point:  
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.initial_point = (self.cartographer.worm_x[i],self.cartographer.worm_y[i])

            # Check if the point is white or black
            if self.map_matrix[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True
