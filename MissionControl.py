import random as rand
import pygame
import time
import sys
import Assets
from DroneManager import DroneManager
from RoverManager import RoverManager

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[2])

        self.game         = game
        self.settings     = game.sim_settings
        self.cartographer = game.cartographer
        self.map_matrix   = self.cartographer.bin_map

        # Mission settings
        # Exploration is 0 / Search&Rescue is 1
        self.mission   = self.settings[0]
        self.completed = False

        # Maximise the game window
        self.game.display = self.game.to_maximised()
        
        # Find a suitable start position
        self.start_point = None
        self.set_start_point()

        # Create the drones and the rovers
        self.drone_manager = DroneManager(self.game, self.start_point)
        #self.rover_manager = RoverManager(self.game, self.start_point)

        # Show the map and the robots at step 0 for 1 second
        pygame.display.update()
        time.sleep(1)

        # Start mission
        self.start_mission()

    # Mission loop
    def start_mission(self):
        # Keep moving the drones until the mission is completed
        while not self.completed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.drone_manager.step()
            #self.rover_manager.step()

            pygame.display.update()
            time.sleep(0.25)
        
    # Among the starting positions of the worms, find one that is viable
    def set_start_point(self):
        # While point is BLACK or not initialised
        while self.start_point is None or Assets.wall_hit(self.map_matrix, self.start_point):
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.start_point = (self.cartographer.worm_x[i],self.cartographer.worm_y[i])