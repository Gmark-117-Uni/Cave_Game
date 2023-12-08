import random as rand
from DroneManager import DroneManager
from RoverManager import RoverManager

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[1])

        self.game = game
        self.settings = game.sim_settings

        # Initialise the Managers (and the robots)
        self.drone_manager = DroneManager(game, self.settings[2])
        self.rover_manager = RoverManager(game)

        # Find a suitable start position
        self.set_start_pos()
        

    # Among the starting positions of the worms, find one that is viable
    def set_start_pos(self):
        good_point = False
        while not good_point:
            
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.initial_point = [self.cave.worm_x[i],self.cave.worm_y[i]]
            
            # Check if the point is white or black
            if self.cave.bin_map[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True