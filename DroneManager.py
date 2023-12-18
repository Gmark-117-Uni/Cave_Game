import pygame
import sys
import random as rand
import numpy as np
import MapGenerator as MapGenerator
import Assets
from ModeExploration import ModeExploration

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
        self.black_cave_png = Assets.Images['BLACK_CAVE_MAP'].value
        # Set drone icone
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone = pygame.transform.scale(self.drone_icon, (70,70))
        # Save the number of drones
        self.num_drones = self.settings[3]
        # Get mode
        self.mode = self.settings[0]
        # List to store drone colors
        self.drone_colors = []
        # Radius of the circle
        self.radius = 40
        
        # Exit the simulation if the input is given
        while self.game.playing:
            self.game.check_events()
            if self.game.BACK_KEY or self.game.START_KEY:
                self.game.playing = False
                self.game.curr_menu.run_display = True
                self.game.to_windowed()
           
    # Generate a new drone rect for each drone
    def set_start_point(self):
        # Create/reset the list to store the start point 
        self.start_point = []
        # Create/reset the list to store the rectangles for each drone
        self.drone_rects = []
        
        # if it's the first time start point = list of initial points
        if not hasattr(self, 'next_point'):
            for _ in range(self.num_drones):  
                self.start_point.append(self.initial_point) 
        # If not my current initial point correspont to the last next point       
        else:
            self.start_point = self.next_point
        if not hasattr(self, 'next_point'):
            for drone_index in range(self.num_drones):
                # Create a new drone rect for each drone
                drone_rect_start = self.drone.get_rect()
                # Set the center of the drone_rect to the initial point
                drone_rect_start.center = self.start_point[drone_index]
                # Add the new drone_rect to the list
                self.drone_rects.append(drone_rect_start)
        else:
            for drone_index in range(self.num_drones):
                # Create a new drone rect for each drone
                drone_rect_next = self.drone.get_rect()
                # Set the center of the drone_rect to the initial point
                drone_rect_next.center = self.next_point[drone_index]
                # Add the new drone_rect to the list
                self.drone_rects.append(drone_rect_next)   
                 
        # Set the next point if is not the first time and draw the drones
        if not hasattr(self, 'next_point'):
            self.draw_drones()   
        else:
            self.set_next_point()
            self.draw_drones()  
  
  
    # Get the next point                
    def set_next_point(self):
       # Reset/ initialize the list for the next points
       self.next_point = []
       # If the mode is exploration
       if self.mode == 0:
        # Create the drones 
        self.exploration = ModeExploration(self.start_point, self.num_drones)
        self.next_point = self.exploration.next_point()
        self.exploration_end = self.exploration.finish_exploration()
        print('is finished?',self.exploration_end)

    # Draw the drones and the colored area
    def draw_drones(self):  
        for drone_index,drone_rect in enumerate(self.drone_rects): 
            # Create the circle
            self.set_circle_color(drone_index)
            
            # If it's the first time
            if not hasattr(self, 'next_point'):
                # Blit the circle at the initial point
                self.game.window.blit(self.circle_surface, (drone_rect[0]-5,drone_rect[1]-5)) 
                # Blit the drone at the initial point
                self.game.window.blit(self.drone, (drone_rect[0],drone_rect[1])) 
        
        # Outside the for loop if it's not the first time
        if hasattr(self, 'next_point'):  
            # Clear the old drone  
            self.clear_previous_drones()
    
        for drone_index,drone_rect in enumerate(self.drone_rects):
            if hasattr(self, 'next_point'):   
                
                self.set_circle_color(drone_index)
                    # Draw the path 
                #self.draw_path(drone_index,drone_rect)
                # Add the black mask
                # Save it on the map
               # pygame.image.save(self.game.window,Assets.Images['CAVE_MAP'].value)
                black_cave_map = pygame.image.load(self.black_cave_png).convert_alpha()
                self.game.window.blit(black_cave_map, (0, 0))  
                
                self.update_drone_position(drone_index,drone_rect)
                        
        pygame.display.flip()   
               
        if not hasattr(self, 'next_point'):
            # Initialize the next point
            self.next_point =[]
            self.next_point = self.start_point
        
        
    # Function to get a random color with semi-transparency
    def get_random_color(self,available_colors):     
        # Choose a random color from the list
        random_color = rand.choice(available_colors)
        rgb_value = (random_color.value)   
        # Remove the chosen color from the list
        available_colors.remove(random_color)
        return rgb_value 
    
    def set_circle_color(self,drone_index):
        available_colors = list(Assets.DroneColors)
        # If is the first time assign a color
        if not hasattr(self, 'next_point'):
            color = self.get_random_color(available_colors)
            self.drone_colors.append(color)
            print(self.drone_colors)
        # If not take the corresponding one
        else:
            color = self.drone_colors[drone_index]
            print(color)
            print(drone_index)
            
        # Create a surface to draw the circle (dimensions,channel for transprancy)
        self.circle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # (surface, color, center of the circle on the surface, radius)
        pygame.draw.circle(self.circle_surface, (*color, 130),(self.radius,self.radius), self.radius)   
        
    def update_drone_position(self, drone_index,drone_rect):
        
        # If it's the first time 
        if hasattr(self, 'next_point'):
           print (self.next_point[drone_index])
           self.tmp_next_point = self.next_point[drone_index]
        
           # Update the center of the existing drone_rect
           self.drone_rects[drone_index].center = self.tmp_next_point
           # Blit the circle at the initial point
           self.game.window.blit(self.circle_surface, (drone_rect[0]-5,drone_rect[1]-5)) 
           # Blit the drone at the initial point
           self.game.window.blit(self.drone, (drone_rect[0],drone_rect[1]))
           
    def draw_path (self, drone_index, drone_rect):  
        
        # If is first there is no step
        if not hasattr(self, 'next_point'):
            # Blit the circle surface onto the game window
            self.game.window.blit(self.circle_surface, (drone_rect.centerx - self.radius, drone_rect.centery - self.radius))
        # If not take a step
        else:
            start_point_tmp = self.start_point[drone_index]
            end_point_tmp = self.next_point[drone_index]
            color = self.drone_colors[drone_index]
            pygame.draw.line(self.circle_surface, (*color, 130), start_point_tmp, end_point_tmp, 2*self.radius)
            # Blit the color surface onto the target surface
            self.game.window.blit(self.circle_surface, [start_point_tmp[0]-self.radius,start_point_tmp[1]-self.radius])
        
    def clear_previous_drones(self):
        # Load the CAVE_MAP image
        cave_map = pygame.image.load(self.cave_png).convert_alpha()
        # Draw the CAVE_MAP image onto the game window
        self.game.window.blit(cave_map, (0, 0))  

        
