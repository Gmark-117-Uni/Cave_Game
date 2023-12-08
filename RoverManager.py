from Rover import Rover

class RoverManager():
    def __init__(self, game):
        self.game = game
        self.cave = game.cave_gen.bin_map
        self.settings = game.sim_settings
        self.rover_list = self.build_rovers(self.settings[2])

    def build_rovers(self, n_drones):
        pass
