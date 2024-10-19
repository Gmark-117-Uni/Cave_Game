import os
import random as rand
import math
import numpy as np
import cv2
import pygame
import Assets
from Assets import sqr, next_cell_coords
from multiprocessing import Process

class MapGenerator():
    def __init__(self, game, prefab=False):
        # Initialize the MapGenerator with game settings and dimensions
        self.game     = game
        self.settings = game.sim_settings
        self.surface  = game.display
        self.width    = Assets.FULLSCREEN_W
        self.height   = Assets.FULLSCREEN_H
        
        # Set the random seed for reproducibility
        rand.seed(self.settings[2])

        # Initialise worm management settings
        self.worm_inputs  = Assets.WormInputs[self.settings[1]].value # Inputs for worm behavior
        self.proc_num     = 8 # Number of processes (worms) to generate
        self.targets      = list(map(int, np.linspace(0,self.proc_num-1,self.proc_num))) # Targets for each worm
        self.proc_counter = 0 # Counter for completed processes
        self.border_thck  = 50 # Thickness of the borders to control worm movement
        self.set_starts()  # Set the starting positions of the worms

        if not prefab:
            # If not generating from a prefab, create a new map and simulate worm behavior
            self.bin_map = np.ones([self.height,self.width]) # Create a binary map initialized to 1s
            self.dig_map(self.proc_num) # Generate the map using worms

            # Perform image processing on the generated map
            self.process_map()

            # Save and display the processed map
            self.save_map()
            self.extract_cave_walls()
            self.extract_cave_floor()
        else:
            # If generating from a prefab, load the cave matrix from a file
            self.bin_map = np.loadtxt(Assets.Images['CAVE_MATRIX'].value)
    

    #  ____   ___   ____   ____  ___  _   _   ____ 
    # |  _ \ |_ _| / ___| / ___||_ _|| \ | | / ___|
    # | | | | | | | |  _ | |  _  | | |  \| || |  _ 
    # | |_| | | | | |_| || |_| | | | | |\  || |_| |
    # |____/ |___| \____| \____||___||_| \_| \____|

    # Create multiple worms and let them eat away the map simultaneously
    # while displaying the loading screen
    def dig_map(self, proc_num):
        proc_list = []  # List to hold process references
        
        # Display loading screen
        self.game.curr_menu.loading_screen(self.proc_counter)

        # Start multiple processes for worms
        for i in range(proc_num):
            proc_list.append(Process(target=self.worm(self.worm_x[i], self.worm_y[i], *(self.worm_inputs), i)))  # Create a worm process
            proc_list[i].start() # Start the worm process
        
        # Wait for all processes to complete
        for i in range(proc_num):
            proc_list[i].join()

    # Model a worm that randomly eats away at the map
    def worm(self, x, y, step, stren, life, id):
        while life: # Continue while the worm has life
            # Calculate the borders for the worm's eating area
            x1 = max(x - int(0.5 * stren), 0) # Adjust for legend
            y1 = max(y - int(0.5 * stren), 0)
            x2 = min(x + int(0.5 * stren), self.width-1)
            y2 = min(y + int(0.5 * stren), self.height-1)

            # Eat the surrounding pixels within the calculated area
            for i in range(x1, x2+1):
                for j in range(y1, y2+1):
                    if self.bin_map[j][i]==1 and self.choose_brush(x, y, i, j, stren): # Check if the pixel can be eaten
                        self.bin_map[j][i] = 0 # Mark the pixel as eaten
            
            self.border_control(x1, x2, y1, y2, stren) # Manage borders to keep worms in bounds
            
            # Move to the next cell based on the current direction
            x, y = next_cell_coords(x, y, step, self.dir)
            life -= 1 # Decrease life of the worm

        # Connect rooms after worm finishes eating
        self.connect_rooms(x, y, step, stren, id)
        
        # Update the loading screen with the current process count
        self.proc_counter += 1
        self.game.curr_menu.loading_screen(self.proc_counter)


    #  _____   ___    ___   _      ____  
    # |_   _| / _ \  / _ \ | |    / ___| 
    #   | |  | | | || | | || |    \___ \ 
    #   | |  | |_| || |_| || |___  ___) |
    #   |_|   \___/  \___/ |_____||____/ 

    # Set starting positions for the worms
    def set_starts(self):
        self.worm_x = list(map(int, [self.width/4,              # Top Left
                                     3*self.width/4,            # Top Right
                                     3*self.width/4,            # Bottom Right
                                     self.width/4,              # Bottom Left
                                     self.width/2,              # Center
                                     rand.randint(10,1190),     # Random
                                     rand.randint(10,1190),     # Random
                                     rand.randint(10,1190)]))   # Random
        
        self.worm_y = list(map(int, [self.height/4,             # Top Left
                                     self.height/4,             # Top Right
                                     3*self.height/4,           # Bottom Right
                                     3*self.height/4,           # Bottom Left
                                     self.height/2,             # Center
                                     rand.randint(10,740),      # Random
                                     rand.randint(10,740),      # Random
                                     rand.randint(10,740)]))    # Random

    # Avoid collision with the window borders
    def border_control(self, x1, x2, y1, y2, stren, new_dir=True):
        # Right Border Control
        if x2+(0.5*stren)>self.width-self.border_thck:
            self.dir = rand.randint(180, 360) # Change direction to avoid right border
            return
        
        # Left Border Control
        if x1-(0.5*stren)<self.border_thck: 
            self.dir = rand.randint(0, 180) # Change direction to avoid left border
            return
        
        # Bottom Border Control
        if y2+(0.5*stren)>self.height-self.border_thck:
            if rand.randint(0,1):
                self.dir = rand.randint(0, 90) # Go upwards
                return
            else:
                self.dir = rand.randint(270, 360) # Go downwards
                return
        
        # Top Border Control
        if y1-(0.5*stren)<self.border_thck:
            self.dir = rand.randint(90, 270) # Go downwards
            return
        
        # Otherwise choose a random direction
        if new_dir:
            self.dir = rand.randint(0,360)

    # Choose the shape of the eaten part
    def choose_brush(self, x1, y1, x2, y2, stren):
        # Choose randomly between different brush shapes
        mode = Assets.Brush(rand.randint(0,4)).name
        
        # Based on the brush shape, determine if the pixel is eaten
        match mode:
            case 'CIRCLE':
                dist = math.sqrt(sqr(x2-x1) + sqr(y2-y1))
                return True if dist<(0.5*stren) else False
            case 'ELLIPSE':
                dist = sqr(x2-x1) + 6*sqr(y2-y1)
                return True if dist<sqr(0.5*stren) else False
            case 'DIAMOND':
                dist = abs(x2-x1) + abs(y2-y1)
                return True if dist<(0.5*stren) else False
            case 'OCTAGON':
                dist = abs(x2-x1) + abs(y2-y1)
                return True if dist<(0.75*stren) else False
            case 'CHAOTIC':
                dist = math.sqrt(sqr(x2-x1) + sqr(y2-y1))
                return True if dist<(rand.uniform(0.2,0.4)*stren) else False
            case 'RECTANGULAR':
                return True

    #  _____  ___  _   _  ___  ____   _   _  ___  _   _   ____ 
    # |  ___||_ _|| \ | ||_ _|/ ___| | | | ||_ _|| \ | | / ___|
    # | |_    | | |  \| | | | \___ \ | |_| | | | |  \| || |  _
    # |  _|   | | | |\  | | |  ___) ||  _  | | | | |\  || |_| |
    # |_|    |___||_| \_||___||____/ |_| |_||___||_| \_| \____|

    # Ensure there are no inacessible rooms
    def connect_rooms(self, x, y, step, stren, id):
        # Get the target coordinates and the boundaries for room connection
        x_min, x_max, y_min, y_max, target = self.assign_target(step, id)
        life = 100 # Counter to limit iterations

        # Continue connecting rooms while within bounds and iterations remain
        while (x<x_min or x>x_max or y<y_min or y>y_max or life>=0):
            self.dir = self.homing_sys(x, y, target) # Determine direction towards target

            # Define the border limits for "eating" surrounding pixels
            x1 = max(x - stren, 0) 
            y1 = max(y - stren, 0)
            x2 = min(x + stren, self.width-1)
            y2 = min(y + stren, self.height-1)

            # "Eat" the surrounding pixels for a given strength
            for i in range(x1, x2+1):
                for j in range(y1, y2+1):
                    # Increase brush strength to ensure survival through median filter
                    if self.bin_map[j][i]==1 and self.choose_brush(x, y, i, j, 1.5*stren):
                        self.bin_map[j][i] = 0
            
            # Control the borders after eating
            self.border_control(x1, x2, y1, y2, stren, new_dir=False)
            
            # Update coordinates for the next cell based on direction
            x, y = next_cell_coords(x, y, step, self.dir)
            life -= 1 # Decrease the life counter

    # Set the course for the starting point of the closest worm
    def homing_sys(self, x, y, target):
        # Calculate the direction to get to the target
        rad_dir    = math.atan2((y - self.worm_y[target]), (x - self.worm_x[target])) # Calculate angle
        deg_dir    = (rad_dir if rad_dir >= 0 else (2*math.pi + rad_dir)) * 180 / math.pi # Convert to degrees
        target_dir = int(deg_dir - 90 if deg_dir>=90 else deg_dir + 270) # Adjust direction

        # Randomly change direction to add realism (50% chance)
        if not rand.randint(0,1):
            target_dir = (target_dir + rand.randint(-90,90)) % 360

        # Check if direction is valid 
        if (target_dir<360 and target_dir>=0):
            return target_dir
        else:
            print('Direction: ', target_dir)
            raise ValueError('Direction is unacceptable')

    # Assign the target where the worm goes to die
    def assign_target(self, step, id):
        # Shuffle the targets list to randomize selection
        shuffled = False
        while not shuffled:
            rand.shuffle(self.targets)

            # Ensure worms do not target themselves
            for i in range(len(self.targets)):
                shuffled = False if i == self.targets[i] else True # Set shuffled if valid
        
        target = self.targets[id] # Get the selected target
        
        # Set boundaries based on target's position
        x_min = self.worm_x[target] - 2*step
        x_max = self.worm_x[target] + 2*step
        y_min = self.worm_y[target] - 2*step
        y_max = self.worm_y[target] + 2*step

        # Return boundaries and target
        return x_min, x_max, y_min, y_max, target


    #   ____  _      _____     _     _   _  ___  _   _   ____ 
    #  / ___|| |    | ____|   / \   | \ | ||_ _|| \ | | / ___|
    # | |    | |    |  _|    / _ \  |  \| | | | |  \| || |  _
    # | |___ | |___ | |___  / ___ \ | |\  | | | | |\  || |_| |
    #  \____||_____||_____|/_/   \_\|_| \_||___||_| \_| \____|

    # Remove isolated caves
    def remove_hermit_caves(self,image):
        # Create a binary mask by inverting the image
        inverted_image = np.where(image == 0, 1, 0).astype('uint8')
        # Find connected components with statistics in the inverted image
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted_image, connectivity=8)

        # If no isolated caves, return the original image
        if num_labels <= 1:
            print("There are no isolated caves. No need to remove anything.")
            return image

         # Identify the index of the largest connected region
        biggest_blob_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
        
        # Create a mask to keep only the biggest blob
        mask_to_keep = np.ones_like(labels, dtype=bool)
        mask_to_keep[labels != biggest_blob_index] = False
        
        # Apply the mask to the original image
        cleaned_image = np.where(mask_to_keep, image, 1) # Keep the largest region, clear others

        return cleaned_image


    #  ____    ___   ____   _____         ____   ____    ___    ____  _____  ____   ____   ___  _   _   ____ 
    # |  _ \  / _ \ / ___| |_   _|       |  _ \ |  _ \  / _ \  / ___|| ____|/ ___| / ___| |_ _|| \ | | / ___|
    # | |_) || | | |\___ \   | |   _____ | |_) || |_) || | | || |    |  _|  \___ \ \___ \  | | |  \| || |  _
    # |  __/ | |_| | ___) |  | |  |_____||  __/ |  _ < | |_| || |___ | |___  ___) | ___) | | | | |\  || |_| |
    # |_|     \___/ |____/   |_|         |_|    |_| \_\ \___/  \____||_____||____/ |____/ |___||_| \_| \____|

    # Perform image processing of the raw map
    def process_map(self):
        self.game.curr_menu.blit_loading(['Breeding bats...']) # Display loading message

        # Define the kernel dimensions for image processing
        kernel_dim = self.worm_inputs[1] - 1
        input_map  = self.bin_map.astype("uint8") # Convert binary map to unsigned 8-bit integer
        
        # Apply a median blur filter to smooth out borders
        processed_map = cv2.medianBlur(input_map, kernel_dim)

        # Remove isolated caves from the processed map
        clean_map = self.remove_hermit_caves(processed_map)
        
        # Add stalactites to the smoothed cave by combining maps
        stalac_map = cv2.bitwise_or(input_map, clean_map)
        
        # Apply a smaller median blur to avoid creating single pixel stalactites
        kernel_dim = 5
        self.bin_map = cv2.medianBlur(stalac_map, kernel_dim)  # Update the binary map

    def extract_cave_walls(self):
        # Load the cave map image
        cave_map = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()
        # Create a new surface to hold modified cave map with per-pixel alpha
        modified_cave_map = pygame.Surface(cave_map.get_size(), pygame.SRCALPHA)
        
        # Iterate through each pixel to clear black pixels (walls)
        for y in range(cave_map.get_height()):
            for x in range(cave_map.get_width()):
                # Get the color of the current pixel
                pixel_color = cave_map.get_at((x, y))
                if  pixel_color == (255, 255, 255, 255): # If the pixel is white  
                    pixel_color = (0, 0, 0, 0) # Make it transparent
                    
                # Set the pixel color in the modified surface
                modified_cave_map.set_at((x, y), pixel_color)
        # Save the modified map as cave walls
        pygame.image.save(modified_cave_map, Assets.Images['CAVE_WALLS'].value)

    def extract_cave_floor(self):
        # Load the cave map image
        cave_map = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()
        # Create a new surface to hold modified cave map with per-pixel alpha
        modified_cave_map = pygame.Surface(cave_map.get_size(), pygame.SRCALPHA)
        
        # Iterate through each pixel to clear black pixels (floor)
        for y in range(cave_map.get_height()):
            for x in range(cave_map.get_width()):
                # Get the color of the current pixel
                pixel_color = cave_map.get_at((x, y))
                if  pixel_color == (0, 0, 0, 255): # If the pixel is black   
                    pixel_color = (0, 0, 0, 0) # Make it transparent  
                    
                # Set the pixel color in the modified surface
                modified_cave_map.set_at((x, y), pixel_color)
        # Save the modified map as cave floor
        pygame.image.save(modified_cave_map, Assets.Images['CAVE_FLOOR'].value)


    #  _   _  _____  ___  _      ___  _____  ___  _____  ____  
    # | | | ||_   _||_ _|| |    |_ _||_   _||_ _|| ____|/ ___|
    # | | | |  | |   | | | |     | |   | |   | | |  _|  \___ \
    # | |_| |  | |   | | | |___  | |   | |   | | | |___  ___) |
    #  \___/   |_|  |___||_____||___|  |_|  |___||_____||____/

    # Save the generated map
    def save_map(self):
        # Ensure the output folder exists, create if it does not
        if not os.path.exists(os.path.join('Assets', 'Map')):
            os.makedirs(os.path.join('Assets', 'Map'))

        # Change the current directory to the map directory
        directory = os.path.join(Assets.GAME_DIR, 'Assets', 'Map')
        os.chdir(directory)

        # Convert binary map values from [0,1] to [0,255] for image representation
        byte_map = np.where(self.bin_map==1, 0, 255)

        # Save the map as a PNG image
        cv2.imwrite('map.png', byte_map)

        # Save the map matrix as a text file 
        np.savetxt('map_matrix.txt', self.bin_map)

        # Change the directory back to the game directory
        os.chdir(Assets.GAME_DIR)
