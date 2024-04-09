import pygame
import sys
import time
import random as rand
import numpy as np
import MapGenerator as MapGenerator
import Assets
from Drone import Drone

class DroneManager():
    def __init__(self, game, start_point):
        self.game     = game
        self.settings = game.sim_settings
        self.mission  = self.settings[0]

        # Get the initial point
        self.start_point = start_point

        # Import the map
        self.cartographer = self.game.cartographer
        self.map_matrix   = self.cartographer.bin_map
        self.cave_png     = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()

        # Black mask for borders
        self.cave_walls_png = pygame.image.load(Assets.Images['CAVE_WALLS'].value).convert_alpha()
        
        # Set drone icon
        icon_size = self.get_icon_dim()
        
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, icon_size)

        # Extract settings
        self.num_drones = 1#self.settings[3]

        # List to store drone colors
        self.colors = list(Assets.DroneColors)

        # Set node id counter
        self.node_id = 0

        # Build the drones and show them and the map at step 0
        self.build_drones()
        self.draw_cave()
        self.draw()
    
    # Instantiate the swarm of drones as a list
    def build_drones(self):
        # Populate the swarm
        self.drones = []
        for i in range(self.num_drones):
            self.drones.append(Drone(self.game, self, i, self.start_point, self.choose_color(), self.drone_icon, self.map_matrix))

    # Move and display the drones
    def step(self):
        # Remove the drones drawn in the last positions
        self.draw_cave()

        # Update node id
        self.node_id += 1

        # Move all drones by one step
        for i in range(self.num_drones):
            self.drones[i].move(self.node_id)
        
        # Update the map
        self.draw()

    # Function to get a random color with semi-transparency
    def choose_color(self):     
        # Choose a random color from the list, then remove it
        random_color = rand.choice(self.colors)
        self.colors.remove(random_color)

        return random_color.value
    
    # Return the dimension of the drone icon given the map dimension
    def get_icon_dim(self):
        match self.settings[1]:
            case 'SMALL' : return Assets.drone_icon_options[0]
            case 'MEDIUM': return Assets.drone_icon_options[1]
            case 'BIG'   : return Assets.drone_icon_options[2]
    
    # Remove the drones drawn in the last positions
    def draw_cave(self):
        # Draw the CAVE_MAP image onto the game window
        self.game.window.blit(self.cave_png, (0, 0))
    
    # Blit the cave walls
    def draw_walls(self, first_time=True):
        if first_time:
            # The walls cover everything but the drone icon
            self.game.window.blit(self.cave_walls_png, (0, 0))

    # Draw everything in layers: (Lowest layer) 0 -> 3 (Highest layer)
    def draw(self):
        for i in range(4):
            for j in range(self.num_drones):
                match i:
                    case 0: self.drones[j].draw_vision()
                    case 1: self.drones[j].draw_path()
                    case 2: self.draw_walls() if j==0 else self.draw_walls(False)
                    case 3: self.drones[j].draw_icon()
    
    def pool_information(self):
        for i in range(self.drones):
            self.drones[i].get_pos_history()
        
        for i in range(self.drones):
            self.drones[i].update_explored_map()
