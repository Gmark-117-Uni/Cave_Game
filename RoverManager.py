import pygame
import math
import Assets

class RoverManager():
    def __init__(self, game, point, explorer):
        self.game     = game
        self.settings = game.sim_settings
        self.explorer = explorer

        # Get the initial point
        self.init_point = point

        # Import the map
        self.cartographer = self.game.cartographer
        self.map_matrix   = self.cartographer.bin_map
        self.cave_png     = Assets.Images['CAVE_MAP'].value

        # Black mask for borders
        self.cave_walls_png = Assets.Images['CAVE_WALLS'].value
        
        # Set drone icone
        self.rover_icon = pygame.image.load(Assets.Images['ROVER'].value)
        self.rover_icon = pygame.transform.scale(self.rover_icon, (50,50))

        # Extract settings
        self.num_rovers = math.ceil(self.settings[3]/4)

        # List to store drone colors
        self.colors = [Assets.Colors['GREY'].value, Assets.Colors['RED'].value]
