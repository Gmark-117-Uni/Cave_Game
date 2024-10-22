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
        self.game     = game
        self.settings = game.sim_settings
        self.surface  = game.display
        self.width    = Assets.FULLSCREEN_W - 300
        self.height   = Assets.FULLSCREEN_H
        
        # Set the seed
        rand.seed(self.settings[2])

        # Initialise worm management settings
        self.worm_inputs  = Assets.WormInputs[self.settings[1]].value
        self.proc_num     = 8
        self.targets      = list(map(int, np.linspace(0,self.proc_num-1,self.proc_num)))
        self.proc_counter = 0
        self.border_thck  = 50
        self.set_starts()

        if not prefab:
            # Initialise the map and generate worms to eat it simultaneously
            self.bin_map = np.ones([self.height,self.width])
            self.dig_map(self.proc_num)

            # Perform image processing on the result
            self.process_map()

            # Save and display the map
            self.save_map()
            self.extract_cave_walls()
            self.extract_cave_floor()
        else:
            self.bin_map = np.loadtxt(Assets.Images['CAVE_MATRIX'].value)
    

    #  ____   ___   ____   ____  ___  _   _   ____ 
    # |  _ \ |_ _| / ___| / ___||_ _|| \ | | / ___|
    # | | | | | | | |  _ | |  _  | | |  \| || |  _ 
    # | |_| | | | | |_| || |_| | | | | |\  || |_| |
    # |____/ |___| \____| \____||___||_| \_| \____|

    # Create multiple worms and let them eat the map simultaneously
    # while displaying the loading screen
    def dig_map(self, proc_num):
        proc_list = []
        
        self.game.curr_menu.loading_screen(self.proc_counter)

        for i in range(proc_num):
            proc_list.append(Process(target=self.worm(self.worm_x[i], self.worm_y[i], *(self.worm_inputs), i)))
            proc_list[i].start()

        for i in range(proc_num):
            proc_list[i].join()

    # Model a worm that eats away randomically at the map
    def worm(self, x, y, step, stren, life, id):
        while life:
            # Borders
            x1 = max(x - int(0.5 * stren), 0) # Adjust for legend
            y1 = max(y - int(0.5 * stren), 0)
            x2 = min(x + int(0.5 * stren), self.width-1)
            y2 = min(y + int(0.5 * stren), self.height-1)

            # Eat the surrounding pixels for a given stren
            for i in range(x1, x2+1):
                for j in range(y1, y2+1):
                    if self.bin_map[j][i]==1 and self.choose_brush(x, y, i, j, stren):
                        self.bin_map[j][i] = 0
            
            self.border_control(x1, x2, y1, y2, stren)
            
            x, y = next_cell_coords(x, y, step, self.dir)
            life -= 1

        self.connect_rooms(x, y, step, stren, id)
        
        self.proc_counter += 1
        self.game.curr_menu.loading_screen(self.proc_counter)


    #  _____   ___    ___   _      ____  
    # |_   _| / _ \  / _ \ | |    / ___| 
    #   | |  | | | || | | || |    \___ \ 
    #   | |  | |_| || |_| || |___  ___) |
    #   |_|   \___/  \___/ |_____||____/ 

    # Set starting positions for the worms
    def set_starts(self):
        self.worm_x = list(map(int, [self.width/4,      # Top Left
                                     3*self.width/4,    # Top Right
                                     3*self.width/4,    # Bottom Right
                                     self.width/4,      # Bottom Left
                                     self.width/2,      # Center
                                     rand.randint(self.border_thck, self.width - self.border_thck),
                                     rand.randint(self.border_thck, self.width - self.border_thck),
                                     rand.randint(self.border_thck, self.width - self.border_thck)]))
        
        self.worm_y = list(map(int, [self.height/4,     # Top Left
                                     self.height/4,     # Top Right
                                     3*self.height/4,   # Bottom Right
                                     3*self.height/4,   # Bottom Left
                                     self.height/2,     # Center
                                     # Random
                                     rand.randint(self.border_thck, self.height - self.border_thck),
                                     rand.randint(self.border_thck, self.height - self.border_thck),
                                     rand.randint(self.border_thck, self.height - self.border_thck)]))

    # Avoid collision with the window borders
    def border_control(self, x1, x2, y1, y2, stren, new_dir=True):
        # Right Border Control
        if x2+(0.5*stren)>self.width-self.border_thck:
            self.dir = rand.randint(180, 360)
            return
        
        # Left Border Control
        if x1-(0.5*stren)<self.border_thck:
            self.dir = rand.randint(0, 180)
            return
        
        # Bottom Border Control
        if y2+(0.5*stren)>self.height-self.border_thck:
            if rand.randint(0,1):
                self.dir = rand.randint(0, 90)
                return
            else:
                self.dir = rand.randint(270, 360)
                return
        
        # Top Border Control
        if y1-(0.5*stren)<self.border_thck:
            self.dir = rand.randint(90, 270)
            return
        
        # Otherwise choose a random direction
        if new_dir:
            self.dir = rand.randint(0,360)

    # Choose the shape of the eaten part
    def choose_brush(self, x1, y1, x2, y2, stren):
        # Choose randomly between the brushes
        mode = Assets.Brush(rand.randint(0,4)).name
        
        # Given the brush, check if the pixel is eaten or not
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
        x_min, x_max, y_min, y_max, target = self.assign_target(step, id)
        life = 100

        while (x<x_min or x>x_max or y<y_min or y>y_max or life>=0):
            self.dir = self.homing_sys(x, y, target)

            # Borders
            x1 = max(x - stren, 0) # Adjust for legend
            y1 = max(y - stren, 0)
            x2 = min(x + stren, self.width-1)
            y2 = min(y + stren, self.height-1)

            # Eat the surrounding pixels for a given stren
            for i in range(x1, x2+1):
                for j in range(y1, y2+1):
                    # Increase the brush strength to make it survive the Median filter
                    if self.bin_map[j][i]==1 and self.choose_brush(x, y, i, j, 1.5*stren):
                        self.bin_map[j][i] = 0
            
            self.border_control(x1, x2, y1, y2, stren, new_dir=False)
            
            x, y = next_cell_coords(x, y, step, self.dir)
            life -= 1

    # Set the course for the starting point of the closest worm
    def homing_sys(self, x, y, target):
        # Calculate the direction to get to the target
        rad_dir    = math.atan2((y - self.worm_y[target]), (x - self.worm_x[target]))
        deg_dir    = (rad_dir if rad_dir >= 0 else (2*math.pi + rad_dir)) * 180 / math.pi
        target_dir = int(deg_dir - 90 if deg_dir>=90 else deg_dir + 270)

        # Randomically (50% chance) change direction to maintain realism
        if not rand.randint(0,1):
            target_dir = (target_dir + rand.randint(-90,90)) % 360

        # Check if direction is valid because I don't trust myself
        if (target_dir<360 and target_dir>=0):
            return target_dir
        else:
            print('Direction: ', target_dir)
            raise ValueError('Direction is unacceptable')

    # Assign the target where the worm goes to die
    def assign_target(self, step, id):
        # Shuffle the targets list
        shuffled = False
        while not shuffled:
            rand.shuffle(self.targets)

            # Make sure the worms are not targeting themselves
            for i in range(len(self.targets)):
                shuffled = False if i == self.targets[i] else True
        
        target = self.targets[id]
        
        x_min = self.worm_x[target] - 2*step
        x_max = self.worm_x[target] + 2*step
        y_min = self.worm_y[target] - 2*step
        y_max = self.worm_y[target] + 2*step

        return x_min, x_max, y_min, y_max, target


    #   ____  _      _____     _     _   _  ___  _   _   ____ 
    #  / ___|| |    | ____|   / \   | \ | ||_ _|| \ | | / ___|
    # | |    | |    |  _|    / _ \  |  \| | | | |  \| || |  _
    # | |___ | |___ | |___  / ___ \ | |\  | | | | |\  || |_| |
    #  \____||_____||_____|/_/   \_\|_| \_||___||_| \_| \____|

    # Remove isolated caves
    def remove_hermit_caves(self, image):
        # Threshold the image to create a binary mask
        inverted_image = np.where(image == 0, 1, 0).astype('uint8')
        
        # Find connected components with statistics
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted_image, connectivity=8)

        # If no cleaning is required return the passed image
        if num_labels <= 1:
            print("There are no isolated caves. No need to remove anything.")
            return image

        # Find the index of the biggest region 
        biggest_blob_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
        
        # Create a mask and keep only the biggest blob as True
        mask_to_keep = np.ones_like(labels, dtype=bool)
        mask_to_keep[labels != biggest_blob_index] = False
        
        # Apply the mask to the original image
        cleaned_image = np.where(mask_to_keep, image, 1)

        return cleaned_image
    
    # Change the color of all the pixels within a frame of thickness self.border_thck to BLACK
    def add_frame(self, image):
        for i in range(0, self.width):
            for j in range(0, self.height):
                if (image[j][i]==0 and (i < self.border_thck or i > self.width - self.border_thck or
                                        j < self.border_thck or j > self.width - self.border_thck)):
                    image[j][i] = 1

        return self.mask_frame(image)
    
    # Add stalactites randomly along the frame (only in white areas within [0:7] pixels from the border)
    def mask_frame(self, image):
        # Define the random generator
        rng = np.random.default_rng(seed=self.settings[2])

        # Define how far into the map the stalactites are added
        # (Randomly between 0 and 7 changing value every 10 pixels)
        mask_h = np.repeat(rng.choice([0,1,2,3,4,5,6,7], size=math.ceil(self.width/10)), 10)
        mask_v = np.repeat(rng.choice([0,1,2,3,4,5,6,7], size=math.ceil(self.height/10)), 10)

        # Apply the mask
        for i in range(0, self.width):
            for j in range(0, self.height):
                if (image[j][i]==0 and ((i >= self.border_thck and i < self.border_thck + mask_h[i]) or
                                        (i > self.width - self.border_thck - mask_h[i] and i <= self.width - self.border_thck) or
                                        (j >= self.border_thck and j < self.border_thck + mask_v[j]) or
                                        (j > self.height - self.border_thck - mask_v[j] and j <= self.height - self.border_thck))):
                    image[j][i] = rng.choice([0,1], p=[0.4,0.6])
        
        return image


    #  ____    ___   ____   _____         ____   ____    ___    ____  _____  ____   ____   ___  _   _   ____ 
    # |  _ \  / _ \ / ___| |_   _|       |  _ \ |  _ \  / _ \  / ___|| ____|/ ___| / ___| |_ _|| \ | | / ___|
    # | |_) || | | |\___ \   | |   _____ | |_) || |_) || | | || |    |  _|  \___ \ \___ \  | | |  \| || |  _
    # |  __/ | |_| | ___) |  | |  |_____||  __/ |  _ < | |_| || |___ | |___  ___) | ___) | | | | |\  || |_| |
    # |_|     \___/ |____/   |_|         |_|    |_| \_\ \___/  \____||_____||____/ |____/ |___||_| \_| \____|

    # Perform image processing of the raw map
    def process_map(self):
        self.game.curr_menu.blit_loading(['Breeding bats...'])

        # Define the kernel dimensions and prep the map matrix
        kernel_dim = self.worm_inputs[1] - 1
        input_map  = self.bin_map.astype("uint8")
        
        # Apply a median blur filter to smooth borders 
        processed_map = cv2.medianBlur(input_map, kernel_dim)

        # Remove isolated caves
        clean_map = self.remove_hermit_caves(processed_map)
        
        # Add stalactites to the smoothed cave
        stalac_map = cv2.bitwise_or(input_map, clean_map)
        
        # Apply a median blur filter with smaller kernel
        # to avoid single pixel stalactites
        kernel_dim = 5
        self.bin_map = cv2.medianBlur(stalac_map, kernel_dim)

        # Add black frame in case worms were too greedy
        # (Should not happen, but let's keep it)
        #self.bin_map = self.add_frame(self.bin_map)

    def extract_cave_walls(self):
        # Load the CAVE_MAP image
        cave_map = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()
        # Create a new surface with per-pixel alpha
        modified_cave_map = pygame.Surface(cave_map.get_size(), pygame.SRCALPHA)
        # Iterate through each pixel and clear black pixels
        for y in range(cave_map.get_height()):
            for x in range(cave_map.get_width()):
                # Get the color of the current pixel
                pixel_color = cave_map.get_at((x, y))
                if  pixel_color == (255, 255, 255, 255):  
                    pixel_color = (0, 0, 0, 0)  
                # Set the pixel color in the modified surface
                modified_cave_map.set_at((x, y), pixel_color)
        # Save the modified map
        pygame.image.save(modified_cave_map, Assets.Images['CAVE_WALLS'].value)

    def extract_cave_floor(self):
        # Load the CAVE_MAP image
        cave_map = pygame.image.load(Assets.Images['CAVE_MAP'].value).convert_alpha()
        # Create a new surface with per-pixel alpha
        modified_cave_map = pygame.Surface(cave_map.get_size(), pygame.SRCALPHA)
        # Iterate through each pixel and clear black pixels
        for y in range(cave_map.get_height()):
            for x in range(cave_map.get_width()):
                # Get the color of the current pixel
                pixel_color = cave_map.get_at((x, y))
                if  pixel_color == (0, 0, 0, 255):  
                    pixel_color = (0, 0, 0, 0)  
                # Set the pixel color in the modified surface
                modified_cave_map.set_at((x, y), pixel_color)
        # Save the modified map
        pygame.image.save(modified_cave_map, Assets.Images['CAVE_FLOOR'].value)


    #  _   _  _____  ___  _      ___  _____  ___  _____  ____  
    # | | | ||_   _||_ _|| |    |_ _||_   _||_ _|| ____|/ ___|
    # | | | |  | |   | | | |     | |   | |   | | |  _|  \___ \
    # | |_| |  | |   | | | |___  | |   | |   | | | |___  ___) |
    #  \___/   |_|  |___||_____||___|  |_|  |___||_____||____/

    # Save the generated map
    def save_map(self):
        # Ensure the folder exists, otherwise create it
        if not os.path.exists(os.path.join('Assets', 'Map')):
            os.makedirs(os.path.join('Assets', 'Map'))

        # Change the current directory
        directory = os.path.join(Assets.GAME_DIR, 'Assets', 'Map')
        os.chdir(directory)

        # Extend values from [0,1] to [0,255]
        byte_map = np.where(self.bin_map==1, 0, 255)

        # Save the map as a PNG image and change back the directory
        cv2.imwrite('map.png', byte_map)

        # Save the map as a PNG image and change back the directory
        np.savetxt('map_matrix.txt', self.bin_map)

        # Set the current directory as the game directory again
        os.chdir(Assets.GAME_DIR)
