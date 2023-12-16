import pygame
import random as rand
import Assets
from Drone import Drone

class Fleet():
    def __init__(self, game, control, pos):
        self.game = game
        self.control = control
        self.pos = pos
        self.step = 30
        self.colors = list(Assets.DroneColors)
        
        # Set drone icon
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, (70,70))

        self.drones = self.drone_gen()

    # Generate a new drone rect for each drone
    def drone_gen(self):
        num_drones = self.game.sim_settings[2]

        # Create a drone rect and set the center to the start position
        drone_rect = self.drone_icon.get_rect()
        drone_rect.center = self.pos
        
        drones = []
        for _ in range(num_drones):
            drones.append(Drone(self.game, drone_rect, self.choose_color(), self.drone_icon))
        
        return drones
            
    # Actually draw all the drones
    def draw_drones(self):
        for i in range(len(self.drones)):
            self.drones[i].draw_drone()
    
    def move_drones(self):
        for i in range(len(self.drones)):
            self.drones[i].move_drone(self.step)

    # Function to get a random color with semi-transparencys
    def choose_color(self):     
        # Choose and remove a random color from the list
        random_color = rand.choice(self.colors)
        self.colors.remove(random_color)
        
        return random_color.value

