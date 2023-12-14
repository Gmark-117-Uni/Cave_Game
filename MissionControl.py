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
        self.surface= game.display
        
        self.original_drone = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone = pygame.transform.scale(self.original_drone, (10,10))
        
        # Initialise the Managers (and the robots)
        #self.drone_manager = DroneManager(game, self.settings[2])
        #self.rover_manager = RoverManager(game)
        
        # Create a list to store the rectangles for each drone
        self.drone_rects = []
        
        # Find a suitable start position
        self.set_start_pos()
        
        # Create the drones
        self.drone_gen()

    # Among the starting positions of the worms, find one that is viable
    def set_start_pos(self):
        good_point = False
        while not good_point:
            
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.initial_point = (self.cave_gen.worm_x[i],self.cave_gen.worm_y[i])
            
            # Check if the point is white or black
            if self.cave_map[self.initial_point[1]][self.initial_point[0]] == 0:  # White
                good_point = True
                
        print("the point is", self.initial_point) 
                
    # Generate a new drone rect for each drone
    def drone_gen(self):
        num_drones = self.settings[2]
        print("the nbr of drones is", num_drones)

        for _ in range(num_drones):
            # Create a new drone rect for each drone
            drone_rect = self.drone.get_rect()

            # Set the center of the drone_rect to the initial point
            drone_rect.center = self.initial_point

            # Add the new drone_rect to the list
            self.drone_rects.append(drone_rect)

        # Draw all drones on the game window
        self.draw_drones()
            
    # Actually draw all the drones
    def draw_drones(self):
        
        self.game.blit_screen()
        
        background_image = pygame.image.load(Assets.Images['CAVE_MAP'].value)
        # Create a temporary surface with the background
        temp_surface = background_image.copy()
        
        self.surface.blit(self.drone, (0, 0))
        
        # Draw all drones on the temporary surface
        for drone_rect in self.drone_rects:
            temp_surface.blit(self.drone, drone_rect.center)  

        # Blit the temporary surface onto the game window
        self.surface.blit(temp_surface, (0, 0))

        # Update the display
        pygame.display.update()
