import random as rand
from DroneManager import DroneManager
from RoverManager import RoverManager
import pygame
import Assets

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[1])
        self.game = game
        self.settings = game.sim_settings
        self.cave_gen = self.game.cave_gen
        self.cave_map = self.cave_gen.bin_map
        self.surface = game.display
        self.cave_png = Assets.Images['CAVE_MAP'].value
        
        # Save the borders of the cave
        self.save_black_mask()
        self.black_cave_png = Assets.Images['BLACK_CAVE_MAP'].value
        
        # Find a suitable start position
        self.set_initial_point()
        # Start mission
        self.start_mission()
          
                            
    def start_mission(self):
        # Create the drones 
        self.drone_manager = DroneManager(self.game, self.initial_point)
        # Keep moving the drones
        while True:
            self.drone_manager.set_start_point()
           
            
    def save_black_mask (self):
        # Load the CAVE_MAP image
        cave_map = pygame.image.load(self.cave_png).convert_alpha()
        # Create a new surface with per-pixel alpha
        modified_cave_map = pygame.Surface(cave_map.get_size(), pygame.SRCALPHA)
        # Iterate through each pixel and clear black pixels
        for y in range(cave_map.get_height()):
            for x in range(cave_map.get_width()):
                # Get the color of the current pixel
                pixel_color = cave_map.get_at((x, y))
                if  pixel_color == (255, 255, 255, 255):  
                    pixel_color = (0, 0, 0, 0)  
                # Set the pixel color in the modified surface
                modified_cave_map.set_at((x, y), pixel_color)
        # Save the modified map
        pygame.image.save(modified_cave_map,Assets.Images['BLACK_CAVE_MAP'].value)
        
        
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
                
   
