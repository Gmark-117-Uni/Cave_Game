import numpy as np
import random as rand
import math
import pygame
from multiprocessing import Process
import cv2
import Assets

class MapGenerator():
    def __init__(self, game):
        self.game        = game
        self.settings    = game.sim_settings
        self.surface     = game.display
        self.width       = Assets.FULLSCREEN_W
        self.height      = Assets.FULLSCREEN_H
        self.border_thck = 50
        self.bin_map     = np.ones([self.height,self.width])
        self.worm_inputs = Assets.WormInputs[self.settings[0]].value
        
        # Set the seed
        rand.seed(self.settings[1])

        # Set starting positions for the worms
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

        # Initialise worm management settings
        self.proc_num     = 8
        self.targets      = list(map(int, np.linspace(0,self.proc_num-1,self.proc_num)))
        self.proc_counter = 0

        # Generate worms to eat the map simultaneously
        self.dig_map(self.proc_num)

        # Perform image processing on the result
        self.process_map()

        # Display the map
        self.draw_map(self.bin_map)

        # Exit the simulation if the input is given
        while self.game.playing:
            self.game.check_events()
            if self.game.BACK_KEY or self.game.START_KEY:
                self.game.playing               = False
                self.game.curr_menu.run_display = True
                
                self.surface = self.game.to_windowed()

    # Create multiple worms and let them eat the map simultaneously
    # while displaying the loading screen
    def dig_map(self, proc_num):
        proc_list = []
        
        self.game.curr_menu.loading_screen(self.proc_counter, 'Digging...')

        for i in range(proc_num):
            proc_list.append(Process(target=self.worm(self.worm_x[i], self.worm_y[i], *(self.worm_inputs), i)))
            proc_list[i].start()

        for i in range(proc_num):
            proc_list[i].join()

    # Given multiple maps, perform an OR operation on every pixel
    def merge_maps(self, map_list):
        tot_map = map_list[0]
        for i in range(len(map_list)):
            if i!=0:
                tot_map = tot_map | map_list[i]
        
        return tot_map

    # Perform image processing of the raw map
    def process_map(self):
        self.game.curr_menu.blit_loading('Growing stalactites...')

        # Define the kernel dimensions and prep the map matrix
        kernel_dim = self.worm_inputs[1] - 1
        input_map  = self.bin_map.astype("uint8")
        
        # Apply a median blur filter to smooth borders 
        processed_map = cv2.medianBlur(input_map, kernel_dim)

        # Remove isolated caves
        clean_map = self.remove_hermit_caves(processed_map)
        
        # Add stalactites to the smoothed cave
        self.bin_map = self.merge_maps([input_map, clean_map]) 

    # Remove isolated caves
    def remove_hermit_caves(self,image):
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

    # Dispaly the map in the window
    def draw_map(self, input_map, x1=0, x2=Assets.FULLSCREEN_W-1, y1=0, y2=Assets.FULLSCREEN_H-1):
        self.surface = self.game.to_maximised()

        # Make the background black
        self.surface.fill(Assets.Colors['BLACK'].value)

        # WHITE ->  AIR  -> 0
        # BLACK -> WALLS -> 1
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                match input_map[y][x]:
                    case 0: pygame.draw.circle(self.surface, Assets.Colors['WHITE'].value, (x,y), 1)
                    case 2: pygame.draw.circle(self.surface, Assets.Colors['RED'].value, (x,y), 1)
        self.game.blit_screen()

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
            
            x, y = self.next_cell_coords(x, y, step, self.dir)
            life -= 1

        self.connect_rooms(x, y, step, stren, id)
        
        self.proc_counter += 1
        self.game.curr_menu.loading_screen(self.proc_counter, 'Digging...')

    # Calculate the square of the passed argument
    def sqr(self, x):
        return x**2

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

    # Map the given direction to the possible pixels,
    # given the length of the step
    def map_direction(self, step_len, dir):
        # Number of possible cells for a given step length
        targets = step_len * 8

        # The circle is divided into N sectors based on the number of targets
        sector_len = 360 / targets

        # The sectors are shifted backwards to align with the positions of the cells
        sector_offset = math.floor(sector_len / 2)

        # Sectors must be aligned with pixels positions and shifted back
        # Therefore the second half of a sector ends up in the next one
        corrected_dir = dir + sector_offset

        # Sector numbering starts at 0
        target_cell = math.floor((corrected_dir % 360)/ sector_len)

        return target_cell, targets

    # Calculate the coordinates of the pixel for the next step
    def next_cell_coords(self, x, y, step_len, dir):
        target_cell, targets = self.map_direction(step_len, dir)

        cases = Assets.Axes(step_len)
        
        # Check on axes and diagonals
        match target_cell:
            case cases.up:
                y -= step_len
                return x, y
            case cases.diag1:
                x += step_len
                y -= step_len
                return x, y
            case cases.right:
                x += step_len
                return x, y
            case cases.diag4:
                x += step_len
                y += step_len
                return x, y
            case cases.down:
                y += step_len
                return x, y
            case cases.diag3:
                x -= step_len
                y += step_len
                return x, y
            case cases.left:
                x -= step_len
                return x, y
            case cases.diag2:
                x -= step_len
                y -= step_len
                return x, y

        # Check on pixels between axes and diagonals
        if (step_len-1)!=0:
            for i in cases.list:
                if i==0:
                    check = range(cases.list[-1] + 1, targets)
                else:
                    check = range(cases.list[cases.list.index(i)-1]+1, i)
                
                for j in check:
                    if target_cell==j:
                        match i:
                            case cases.up:
                                x -= targets - j
                                y -= step_len
                                return x, y
                            case cases.diag1:
                                x += j
                                y -= step_len
                                return x, y
                            case cases.right:
                                x += step_len
                                y -= i - j
                                return x, y
                            case cases.diag4:
                                x += step_len
                                y += i - j
                                return x, y
                            case cases.down:
                                x += i - j
                                y += step_len
                                return x, y
                            case cases.diag3:
                                x -= j - i + step_len
                                y += step_len
                                return x, y
                            case cases.left:
                                x -= step_len
                                y += i - j
                                return x, y
                            case cases.diag2:
                                x -= step_len
                                y -= j - i + step_len
                                return x, y

    # Choose the shape of the eaten part
    def choose_brush(self, x1, y1, x2, y2, stren):
        # Choose randomly between the brushes
        mode = Assets.Brush(rand.randint(0,4)).name
        
        # Given the brush, check if the pixel is eaten or not
        match mode:
            case 'CIRCLE':
                dist = math.sqrt(self.sqr(x2-x1) + self.sqr(y2-y1))
                return True if dist<(0.5*stren) else False
            case 'ELLIPSE':
                dist = self.sqr(x2-x1) + 6*self.sqr(y2-y1)
                return True if dist<self.sqr(0.5*stren) else False
            case 'DIAMOND':
                dist = abs(x2-x1) + abs(y2-y1)
                return True if dist<(0.5*stren) else False
            case 'OCTAGON':
                dist = abs(x2-x1) + abs(y2-y1)
                return True if dist<(0.75*stren) else False
            case 'CHAOTIC':
                dist = math.sqrt(self.sqr(x2-x1) + self.sqr(y2-y1))
                return True if dist<(rand.uniform(0.2,0.4)*stren) else False
            case 'RECTANGULAR':
                return True

    # Ensure there are no inacessible rooms
    def connect_rooms(self, x, y, step, stren, id):

        x_min, x_max, y_min, y_max, target = self.assign_target(step, id)

        while (x<x_min or x>x_max or y<y_min or y>y_max):
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
            
            x, y = self.next_cell_coords(x, y, step, self.dir)

    # Set the course for the starting point of the closest worm
    def homing_sys(self, x, y, target):
        # Calculate the direction to get to the target
        rad_dir    = math.atan2((y - self.worm_y[target]), (x - self.worm_x[target]))
        deg_dir    = (rad_dir if rad_dir >= 0 else (2*math.pi + rad_dir)) * 180 / math.pi
        target_dir = int(deg_dir - 90 if deg_dir>=90 else deg_dir + 270)

        # Randomically change direction to maintain realism
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
