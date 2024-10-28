import random as rand
import pygame
import time
import sys
import math
import threading
import Assets
from ControlCenter import ControlCenter
from Drone import Drone
from Rover import Rover

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[2])

        self.game         = game
        self.settings     = game.sim_settings
        self.cartographer = game.cartographer
        self.map_matrix   = self.cartographer.bin_map
        self.cave_png     = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()
        
        self.delay = 1/15

        # Black mask for borders
        self.cave_walls_png = pygame.image.load(Assets.Images['CAVE_WALLS'].value).convert_alpha()

        # Mission settings
        # Exploration is 0 / Search&Rescue is 1
        self.mission   = self.settings[0]
        self.completed = False

        # Initialise control center for displaying mission status
        self.control_center = ControlCenter(game, self.settings[3])

        # Maximise the game window
        self.game.display = self.game.to_maximised()
        
        # Find a suitable start position
        self.start_point = None
        self.set_start_point()

        # Build the drones and the rovers
        self.build_drones()
        self.build_rovers()

        # Print them on the map
        self.draw()

        # Show the map and the robots at step 0 for 1 second
        pygame.display.update()
        time.sleep(1)

        # Create an event to stop the threads when the mission is complete
        self.mission_event = threading.Event()

        # Start mission
        self.start_mission()

#  __  __  ___  ____   ____   ___   ___   _   _      ____   ___   _   _  _____  ____    ___   _     
# |  \/  ||_ _|/ ___| / ___| |_ _| / _ \ | \ | |    / ___| / _ \ | \ | ||_   _||  _ \  / _ \ | |
# | |\/| | | | \___ \ \___ \  | | | | | ||  \| |   | |    | | | ||  \| |  | |  | |_) || | | || |
# | |  | | | |  ___) | ___) | | | | |_| || |\  |   | |___ | |_| || |\  |  | |  |  _ < | |_| || |___
# |_|  |_||___||____/ |____/ |___| \___/ |_| \_|    \____| \___/ |_| \_|  |_|  |_| \_\ \___/ |_____|

    def start_mission(self):
        # Start timer
        tic = time.perf_counter()

        # Create and start a thread for each drone's movement
        threads = []
        for i in range(self.num_drones):
            t = threading.Thread(target=self.drone_thread, args=(i,))
            threads.append(t)
            t.start()

        # Keep moving the drones until the mission is completed
        while not self.completed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Set the mission event to signal all threads to stop
                    self.mission_event.set()
                    # Quit and close the program
                    pygame.quit()
                    sys.exit()

            # Check if mission is over
            self.completed = self.is_mission_over()

            # Redraw the cave and the drones at each frame
            self.draw()
            pygame.display.update()

        # Set the mission event to signal all threads to stop
        self.mission_event.set()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check timer
        toc = time.perf_counter()
        print(f"Mission completed in {toc-tic} seconds")
        
    # Among the starting positions of the worms, find one that is viable
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

#  ____   ____    ___   _   _  _____ 
# |  _ \ |  _ \  / _ \ | \ | || ____|
# | | | || |_) || | | ||  \| ||  _|
# | |_| ||  _ < | |_| || |\  || |___
# |____/ |_| \_\ \___/ |_| \_||_____|

    # Thread function for each drone's movement
    def drone_thread(self, drone_id):
        while not self.mission_event.is_set() and not self.drones[drone_id].mission_completed():
            self.drones[drone_id].move()  # Move the drone

            # Control the speed of movement
            time.sleep(self.delay)

    # Instantiate the swarm of drones as a list
    def build_drones(self):
        # Get the required number of drones from the settings
        self.num_drones = self.settings[3]

        # Set drone icon
        icon_size       = self.get_drone_icon_dim()
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, icon_size)

        # List to store drone colors
        self.drone_colors = list(Assets.DroneColors)

        # Populate the swarm
        self.drones = []
        for i in range(self.num_drones):
            self.drones.append(Drone(self.game,
                                     self,
                                     i,
                                     self.start_point,
                                     self.drone_colors.pop(0).value,
                                     self.drone_icon,
                                     self.map_matrix))

    # Return the dimension of the drone icon given the map dimension
    def get_drone_icon_dim(self):
        match self.settings[1]:
            case 'SMALL' : return Assets.drone_icon_options[0]
            case 'MEDIUM': return Assets.drone_icon_options[1]
            case 'BIG'   : return Assets.drone_icon_options[2]

    def pool_information(self):
        for i in range(self.drones):
            self.drones[i].get_pos_history()

        for i in range(self.drones):
            self.drones[i].update_explored_map()

#  ____    ___  __     __ _____  ____  
# |  _ \  / _ \ \ \   / /| ____||  _ \
# | |_) || | | | \ \ / / |  _|  | |_) |
# |  _ < | |_| |  \ V /  | |___ |  _ <
# |_| \_\ \___/    \_/   |_____||_| \_\

    # Instantiate the fleet of rovers as a list
    def build_rovers(self):
        # Get the number of rovers depending on the number of drones
        self.num_rovers = math.ceil(self.settings[3]/4)

        # Set rover icon
        icon_size       = self.get_rover_icon_dim()
        self.rover_icon = pygame.image.load(Assets.Images['ROVER'].value)
        self.rover_icon = pygame.transform.scale(self.rover_icon, icon_size)

        # List to store rover colors (Deprecated: Rovers don't need colors)
        self.rover_colors = list(Assets.RoverColors)

        # Populate the swarm
        self.rovers = []
        for i in range(self.num_rovers):
            self.rovers.append(Rover(self.game, self, i, self.start_point, self.choose_rover_color(), self.rover_icon, self.map_matrix))
    
    # Function to get a random color for each drone
    def choose_rover_color(self):     
        # Choose a random color from the list, then remove it
        random_color = rand.choice(self.rover_colors)
        self.rover_colors.remove(random_color)
        return random_color.value

    # Return the dimension of the drone icon given the map dimension
    def get_rover_icon_dim(self):
        match self.settings[1]:
            case 'SMALL' : return Assets.rover_icon_options[0]
            case 'MEDIUM': return Assets.rover_icon_options[1]
            case 'BIG'   : return Assets.rover_icon_options[2]

#  ____   ____      _  __        __ ___  _   _   ____ 
# |  _ \ |  _ \    / \ \ \      / /|_ _|| \ | | / ___|
# | | | || |_) |  / _ \ \ \ /\ / /  | | |  \| || |  _
# | |_| ||  _ <  / ___ \ \ V  V /   | | | |\  || |_| |
# |____/ |_| \_\/_/   \_\ \_/\_/   |___||_| \_| \____|

    # Remove the icons drawn in the last positions
    def draw_cave(self):
        # Draw the CAVE_MAP image onto the game window
        self.game.window.blit(self.cave_png, (0, 0))

    # Blit the cave walls
    def draw_walls(self):
        # The walls cover everything but the drone icon
        self.game.window.blit(self.cave_walls_png, (0, 0))

    # Draw everything in layers: (Lowest layer) 0 -> 3 (Highest layer)
    def draw(self):
        self.draw_cave()

        for i in range(4):
            for j in range(self.num_drones):
                match i:
                    case 0: self.drones[j].draw_vision()
                    case 1: self.drones[j].draw_path()
                    case 2:
                        if j==0:
                            self.draw_walls()
                    case 3:
                        self.drones[j].draw_icon()
                        if j < len(self.rovers):
                            self.rovers[j].draw_icon()
        
        self.control_center.draw_control_center()