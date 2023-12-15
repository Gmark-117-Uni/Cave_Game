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
        self.drone = pygame.transform.scale(self.original_drone, (70,70))
        
        # Initialise the Managers (and the robots)
        #self.drone_manager = DroneManager(game, self.settings[2])
        #self.rover_manager = RoverManager(game)
        
        # Create a list to store the rectangles for each drone
        self.drone_rects = []
        
        # Find a suitable start position
        self.set_start_pos()
        
        # Create the drones
        self.drone_gen()
        
        # Exit the simulation if the input is given
        while self.game.playing:
            pygame.display.flip()
            self.game.check_events()
            if self.game.BACK_KEY or self.game.START_KEY:
                self.game.playing = False
                self.game.curr_menu.run_display = True
                self.game.to_windowed()
                
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
        print("the number of drones is", num_drones)
        step = 30
        for i in range(num_drones):
            # Create a new drone rect for each drone
            drone_rect = self.drone.get_rect()

            # Set the center of the drone_rect to the initial point
            drone_rect.center = (self.initial_point[0]+i*step, self.initial_point[1])

            # Add the new drone_rect to the list
            self.drone_rects.append(drone_rect)

        # Draw all drones on the game window
        self.draw_drones()
            
    # Actually draw all the drones
    def draw_drones(self):
        
        available_colors = list(Assets.DroneColors) 
        
        # Draw all drones on the temporary surface
        for drone_rect in self.drone_rects:
            # Calculate the radius of the circle
            radius = 40
            # Get random color
            color = self.get_random_color(available_colors)
            
           # Create a surface to draw the circle
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*color, 128),(radius,radius), radius)
            
            # Blit the circle surface onto the game window
            self.game.window.blit(circle_surface, (drone_rect.centerx - radius, drone_rect.centery - radius))
    
            # Create drone
            self.game.window.blit(self.drone, (drone_rect.centerx - self.drone.get_width() / 2, drone_rect.centery - self.drone.get_height() / 2))
           
        # Update the display
        pygame.display.update()

    # Function to get a random color with semi-transparency
    def get_random_color(self,available_colors):
        
        # Choose a random color from the list
        random_color = rand.choice(available_colors)
        rgb_value = (random_color.value)
        
        # Remove the chosen color from the list
        available_colors.remove(random_color)
        return rgb_value
