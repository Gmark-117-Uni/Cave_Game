import os
import time
import configparser
import pygame
import Assets
from Menu import Menu

class ControlCenter(Menu):
    def __init__(self, game, num_drones):
        super().__init__(game)
        # Get number of deployed drones
        self.num_drones = num_drones

        # Calculate surface origin
        self.origin_x = Assets.FULLSCREEN_W - Assets.LEGEND_WIDTH
        self.origin_y = 0
        self.origin   = (self.origin_x,self.origin_y)

        # Calculate surface mid points
        self.mid_x = self.origin_x + (Assets.LEGEND_WIDTH / 2)
        self.mid_y = Assets.FULLSCREEN_H / 2

        # Define surface
        #self.control_surf = pygame.Surface((Assets.LEGEND_WIDTH, Assets.FULLSCREEN_H), pygame.SRCALPHA)

        # Create dictionaries
        self.drone_dict()
        self.rover_dict()

    # Create drone dictionary
    def drone_dict(self):
        self.drones = {
            'Blinky': {
                'id': 0,
                'color': Assets.DroneColors.RED.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Pinky': {
                'id': 1,
                'color': Assets.DroneColors.PINK.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Inky': {
                'id': 2,
                'color': Assets.DroneColors.L_BLUE.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Clyde': {
                'id': 3,
                'color': Assets.DroneColors.ORANGE.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Sue': {
                'id': 4,
                'color': Assets.DroneColors.PURPLE.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Tim': {
                'id': 5,
                'color': Assets.DroneColors.BROWN.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Funky': {
                'id': 6,
                'color': Assets.DroneColors.GREEN.value,
                'battery': 100,
                'status': 'Ready'
            },
            'Kinky': {
                'id': 7,
                'color': Assets.DroneColors.GOLD.value,
                'battery': 100,
                'status': 'Ready'
            }
        }

    # Create rover dictionary
    def rover_dict(self):
        self.rovers = {
            'Huey' : {
                'id': 0,
                'color': Assets.RoverColors.RED.value,
                'battery': 2400,
                'status': 'Ready'
            },
            'Dewey' : {
                'id': 1,
                'color': Assets.RoverColors.BLUE.value,
                'battery': 2400,
                'status': 'Ready'
            },
            'Louie' : {
                'id': 2,
                'color': Assets.RoverColors.GREEN.value,
                'battery': 2400,
                'status': 'Ready'
            }
        }

    # Blit the control center on the map
    def draw_control_center(self):
        # Draw title
        self.draw_text('Control Center', 25,
                       self.mid_x,
                       self.mid_y,
                       Assets.Fonts['BIG'].value,
                       Assets.Colors['WHITE'].value,
                       Assets.RectHandle['CENTER'].value)

        for drone in self.drones:
            if self.drones[drone]['id'] < self.num_drones:
                pass
                # Draw status
            else:
                pass
                # Draw 'N/A'
        