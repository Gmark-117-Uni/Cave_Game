import random as rand
import pygame
import time
import sys
import math
import threading
import Assets
from Drone import Drone
#from Rover import Rover

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[2])

        self.game         = game
        self.settings     = game.sim_settings 
        self.cartographer = game.cartographer
        self.map_matrix   = self.cartographer.bin_map # Get the binary map representation
        self.cave_png     = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha() # Load cave map image
        
        self.delay = 1/15 # Set a delay for frame updates

        # Load cave wall images
        self.cave_walls_png = pygame.image.load(Assets.Images['CAVE_WALLS'].value).convert_alpha()

        # Initialize mission settings (0 for exploration, 1 for search & rescue)
        self.mission   = self.settings[0]
        self.completed = False # Track whether the mission is completed

        # Maximise the game window
        self.game.display = self.game.to_maximised()
        
        # Set the starting position for drones
        self.start_point = None
        self.set_start_point()

        # DRONE INITIALISATION
        self.num_drones = self.settings[3] # Get the number of drones from settings
        # Set drone icon and resize it based on the icon dimensions
        icon_size = self.get_icon_dim()
        self.drone_icon = pygame.image.load(Assets.Images['DRONE'].value)
        self.drone_icon = pygame.transform.scale(self.drone_icon, icon_size)

        # ROVER INITIALISATION
        self.num_rovers = math.ceil(self.settings[3]/3) # Calculate the number of rovers based on drones
        # Set rover icon and resize it based on the icon dimensions
        self.rover_icon = pygame.image.load(Assets.Images['ROVER'].value)
        self.rover_icon = pygame.transform.scale(self.rover_icon, (50,50))
        
        # List to store available drone and rover colors
        self.colors = list(Assets.DroneColors)

        # Initialize the drones and draw the map and drones at the initial step
        self.build_drones()
        self.draw_cave()
        self.draw()
        
        # Update the display to show the initial map and robots for 1 second
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

        # Record the start time for mission duration tracking
        tic = time.perf_counter()

        # Create and start a thread for each drone's movement
        threads = [] # List to keep track of all threads
        for i in range(self.num_drones):
            t = threading.Thread(target=self.drone_thread, args=(i,))
            threads.append(t)
            t.start()

        # Main loop to keep moving drones until the mission is completed
        while not self.completed:
            for event in pygame.event.get():
                # If the window is closed
                if event.type == pygame.QUIT:
                    # Set the mission event to signal all threads to stop
                    self.mission_event.set()
                    # Quit and close the program
                    pygame.quit()
                    sys.exit()

            # Check if mission is over
            self.completed = self.is_mission_over()

            # Redraw the cave and the drones for each frame
            self.draw_cave()
            self.draw()

            pygame.display.update()
            time.sleep(self.delay)

        # Signal all threads to stop when the mission is complete
        self.mission_event.set()

        # Wait for all threads to finish executing
        for t in threads:
            t.join()

        # Check the elapsed time for the mission
        toc = time.perf_counter()
        print(f"Mission completed in {toc-tic} seconds")
        
    # Among the starting positions of the worms, find one that is viable
    def set_start_point(self):
         # Continuously search for a valid starting point until one is found
        while self.start_point is None or Assets.wall_hit(self.map_matrix, self.start_point):
            # Randomly select one of the initial points of the worms
            i = rand.randint(0,3)
            self.start_point = (self.cartographer.worm_x[i],self.cartographer.worm_y[i])
    
    # Check if the mission is completed
    def is_mission_over(self):
        # Check if all drones have completed their missions
        for drone in self.drones:
            if not drone.mission_completed():
                return False
        return True # All drones are completed, mission is over
    
    #  _____  _____   ____  _   _ ______  
    # |  __ \|  __ \ / __ \| \ | |  ____|
    # | |  | | |__) | |  | |  \| | |__  
    # | |  | |  _  /| |  | | . ` |  __|  
    # | |__| | | \ \| |__| | |\  | |____ 
    # |_____/|_|  \_\\____/|_| \_|______|

    # Thread function for each drone's movement
    def drone_thread(self, drone_id):
        # Continue moving the drone until mission event is set or the drone completes its mission
        while not self.mission_event.is_set() and not self.drones[drone_id].mission_completed():
            self.drones[drone_id].move()  #Move the specified drone
            time.sleep(self.delay) # Control the speed of movement

    # Instantiate the swarm of drones as a list
    def build_drones(self):
        # Populate the swarm
        self.drones = []
        for i in range(self.num_drones):
            # Instantiate a Drone object and append it to the drones list
            self.drones.append(Drone(self.game, self, i, self.start_point, self.choose_color(), self.drone_icon, self.map_matrix))

    # Function to get a random color for each drone
    def choose_color(self):     
        # Randomly select a color from the available colors and remove it from the list
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
        # Blit the cave map image onto the game window at (0, 0) position
        self.game.window.blit(self.cave_png, (0, 0))

    # Blit the cave walls
    def draw_walls(self, first_time=True):
        if first_time:
            # Draw the cave walls over the entire window
            self.game.window.blit(self.cave_walls_png, (0, 0))

    # Draw all game elements in layers: (Lowest layer) 0 -> 3 (Highest layer)
    def draw(self):
        for i in range(4):
            for j in range(self.num_drones):
                match i:
                    case 0: self.drones[j].draw_vision()
                    case 1: self.drones[j].draw_path()
                    # Draw cave walls, but only for the first drone to avoid redundancy
                    case 2: self.draw_walls() if j==0 else self.draw_walls(False)
                    case 3: self.drones[j].draw_icon()

    # Pool information from all drones
    def pool_information(self):
        # Collect position history from each drone
        for i in range(self.drones):
            self.drones[i].get_pos_history()
            
        # Update the explored map for each drone
        for i in range(self.drones):
            self.drones[i].update_explored_map()

    #  _____   ______      ________ _____  
    # |  __ \ / __ \ \    / /  ____|  __ \ 
    # | |__) | |  | \ \  / /| |__  | |__) |
    # |  _  /| |  | |\ \/ / |  __| |  _  / 
    # | | \ \| |__| | \  /  | |____| | \ \ 
    # |_|  \_\\____/   \/   |______|_|  \_\
        
        
        
        