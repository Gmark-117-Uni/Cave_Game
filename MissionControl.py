import random as rand
import pygame
import time
import sys
import numpy as np
import threading
import Assets
import MapGenerator as MapGenerator
from Drone import Drone
# from Rover import Rover

class MissionControl():
    
    def __init__(self, game):
        
        self.game         = game
        self.settings     = game.sim_settings
        
        # To use the prefab map
        self.cartographer = game.cartographer
        self.map_matrix   = self.cartographer.bin_map 
        
        # Map
        self.cave_png     = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()

        # Black mask for borders
        self.cave_walls_png = pygame.image.load(Assets.Images['CAVE_WALLS'].value).convert_alpha()
        
        # Delay
        self.delay = 1/15
        
        # Maximise the game window
        self.game.display = self.game.to_maximised()

        # MISSION SETTINGS
        self.mission    = self.settings[0] # Exploration is 0 / Search&Rescue is 1
        self.num_drones = self.settings[3] # Number of drones
        rand.seed(game.sim_settings[2])    # Get the seed from the settings
        
        self.completed = False

        # Find a suitable start position
        self.start_point = None
        self.set_start_point()
        
        # Set DRONE icon
        icon_size = self.get_icon_dim()
        
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, icon_size)
        
        # List to store drone colors
        self.colors = list(Assets.DroneColors)
        
        # Build the drones and show them and the map at step 0
        self.build_drones()
        self.draw_cave()
        self.draw()
        
        # Show the map and the robots at step 0 for 1 second
        pygame.display.update()
        time.sleep(1)
        
        # Create an event to stop the threads when the mission is complete
        self.mission_event = threading.Event()
        
        # Start mission
        self.start_mission()

    #  __  __ _____  _____ _____ _____ ____  _   _    _____ ____  _   _ _______ _____   ____  _      
    # |  \/  |_   _|/ ____/ ____|_   _/ __ \| \ | |  / ____/ __ \| \ | |__   __|  __ \ / __ \| |     
    # | \  / | | | | (___| (___   | || |  | |  \| | | |   | |  | |  \| |  | |  | |__) | |  | | |     
    # | |\/| | | |  \___ \\___ \  | || |  | | . ` | | |   | |  | | . ` |  | |  |  _  /| |  | | |     
    # | |  | |_| |_ ____) |___) |_| || |__| | |\  | | |___| |__| | |\  |  | |  | | \ \| |__| | |____ 
    # |_|  |_|_____|_____/_____/|_____\____/|_| \_|  \_____\____/|_| \_|  |_|  |_|  \_\\____/|______|
    
    
    def start_mission(self):
        # Start timer
        tic = time.perf_counter()

        # Create and start a thread for each drone's movement
        threads = []
        for i in range(self.num_drones):
            t = threading.Thread(target=self.drone_thread, args=(i,))
            threads.append(t)
            t.start()

        # Main pygame loop runs in the main thread
        while not self.completed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Set the mission event to signal all threads to stop
                    self.mission_event.set()
                    pygame.quit()
                    sys.exit()

            # Check if the mission is over
            self.completed = self.is_mission_over()

            # Redraw the cave and the drones at each frame
            self.draw_cave()
            self.draw()
            pygame.display.update()
            time.sleep(self.delay)

        # Set the mission event to signal all threads to stop
        self.mission_event.set()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        toc = time.perf_counter()
        print(f"Mission completed in {toc - tic} seconds")
             
    def set_start_point(self):
        # While point is BLACK or not initialised
        while self.start_point is None or Assets.wall_hit(self.map_matrix, self.start_point):
            # Take one of the initial points of the worms as initial point for the drone
            i = rand.randint(0,3)
            self.start_point = (self.cartographer.worm_x[i],self.cartographer.worm_y[i])
    
    def is_mission_over(self):
        for drone in self.drones:
            if not drone.mission_completed():
                return False
        return True
    
    #  _____  _____   ____  _   _ ______  
    # |  __ \|  __ \ / __ \| \ | |  ____|
    # | |  | | |__) | |  | |  \| | |__  
    # | |  | |  _  /| |  | | . ` |  __|  
    # | |__| | | \ \| |__| | |\  | |____ 
    # |_____/|_|  \_\\____/|_| \_|______|
    
    # Thread function for each drone's movement
    def drone_thread(self, drone_id):
        while not self.mission_event.is_set() and not self.drones[drone_id].mission_completed():
            self.drones[drone_id].move()  # Move the drone
            time.sleep(self.delay)  # Control the speed of movement
                                                   
    # Instantiate the swarm of drones as a list
    def build_drones(self):
        # Populate the swarm
        self.drones = []
        for i in range(self.num_drones):
            self.drones.append(Drone(self.game, self, i, self.start_point, self.choose_color(), self.drone_icon, self.map_matrix))

    # Function to get a random color for each drone
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
            
    # Move and display the drones
    def drone_step(self):
        # Move all drones by one step
        for i in range(self.num_drones):
            self.drones[i].move()
        # Remove the drones drawn in the last positions
        self.draw_cave()
        # Update the map
        self.draw()
        
    #  _____   ______      ________ _____  
    # |  __ \ / __ \ \    / /  ____|  __ \ 
    # | |__) | |  | \ \  / /| |__  | |__) |
    # |  _  /| |  | |\ \/ / |  __| |  _  / 
    # | | \ \| |__| | \  /  | |____| | \ \ 
    # |_|  \_\\____/   \/   |______|_|  \_\
   
   