import pygame
import random as rand
import numpy as np
import MapGenerator as MapGenerator


class DroneManager():
    def __init__(self, game, point, colors):
        self.game = game
        self.initial_point = point
        self.step = 30
        self.next_point = self.next_step()
        print('drones point' + str(self.initial_point))
        
    def next_step(self):
    
       self.next_point = (self.initial_point[0] + self.step, self.initial_point[1])
       return self.next_point
