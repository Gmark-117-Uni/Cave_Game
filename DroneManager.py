import pygame
import sys
import random as rand
import numpy as np
import MapGenerator as MapGenerator
import Assets
from Drone import Drone

class DroneManager():
    def __init__(self, game, point):
        self.game = game
        self.settings = game.sim_settings

        # Get the initial point
        self.initial_point = point

        # Import the map
        self.cave_gen = self.game.cave_gen
        self.cave_map = self.cave_gen.bin_map
        self.cave_png = Assets.Images['CAVE_MAP'].value

        # Black mask for borders
        self.cave_walls_png = Assets.Images['CAVE_WALLS'].value
        
        # Set drone icone
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, (70,70))

        # Extract settings
        self.num_drones = self.settings[3]
        self.mode = self.settings[0]

        # List to store drone colors
        self.colors = list(Assets.DroneColors)

        self.build_drones()
    
    def build_drones(self):
        # Create a drone rect and set the center to the start position
        drone_rect = self.drone_icon.get_rect()
        drone_rect.center = self.initial_point
        
        self.drones = []
        for i in range(self.num_drones):
            self.drones.append(Drone(self.game, i, drone_rect, self.choose_color(), self.drone_icon))

    def step(self):
        for i in range(self.num_drones):
            self.drones[i].move()
            self.drones[i].draw()

    # Function to get a random color with semi-transparency
    def choose_color(self):     
        # Choose a random color from the list
        random_color = rand.choice(self.colors)

        # Remove the chosen color from the list
        self.colors.remove(random_color)

        return random_color.value
