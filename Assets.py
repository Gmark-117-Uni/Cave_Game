import os
import tkinter
import math
from enum import Enum

root = tkinter.Tk()


#  ____   _____  _____  _____  ___  _   _   ____  ____  
# / ___| | ____||_   _||_   _||_ _|| \ | | / ___|/ ___|
# \___ \ |  _|    | |    | |   | | |  \| || |  _ \___ \
#  ___) || |___   | |    | |   | | | |\  || |_| | ___) |
# |____/ |_____|  |_|    |_|  |___||_| \_| \____||____/

# Game directory: ..\CaveGame
GAME_DIR = os.path.dirname(os.path.abspath(__file__))

# Display dimensions
DISPLAY_W    = 1200
DISPLAY_H    = 750
FULLSCREEN_W = root.winfo_screenwidth() - 5
FULLSCREEN_H = root.winfo_screenheight() - 70

# Lists for menu voices and settings
main_menu_states    = ['Start', 'Options', 'Credits', 'Exit']
options_menu_states = ['Game Volume', 'Music Volume', 'Button Sound', 'Back']
sim_menu_states     = ['Mode', 'Map Dimension', 'Seed', 'Drones', 'Back', 'Start Simulation']
mode_options        = ["Cave exploration", "Rescue mission"]
map_options         = ["Small", "Medium", "Big"]
vision_options      = [     39,       19,     4]
drone_icon_options  = [(30,30),  (10,10), (1,1)]
seed                = [      5,       19,   837]

# Map Generator Inputs
step     = 10
strength = 16
life     = 75


#   ____  _         _     ____   ____   _____  ____  
#  / ___|| |       / \   / ___| / ___| | ____|/ ___| 
# | |    | |      / _ \  \___ \ \___ \ |  _|  \___ \ 
# | |___ | |___  / ___ \  ___) | ___) || |___  ___) |
#  \____||_____|/_/   \_\|____/ |____/ |_____||____/ 

class WormInputs(Enum):
        SMALL        = [4*step, 4*strength,    life]
        MEDIUM       = [2*step, 2*strength,  4*life]
        BIG          = [  step,   strength, 15*life]

class Colors(Enum):
        BLACK        = (  0,   0,   0)
        WHITE        = (255, 255, 255)
        EUCALYPTUS   = ( 95, 133, 117)
        GREENDARK    = (117, 132, 104)
        YELLOW       = (255, 255,  51)
        RED          = (255,   0,   0)
        GREEN        = ( 51, 255,  51)
        GREY         = (112, 128, 144)

class DroneColors(Enum):
        PINK         = (255,  51, 153)
        VIOLET       = (153,  51, 255)
        BLUE         = (  0,   0, 153)
        L_BLUE       = ( 51, 255, 255)
        GREEN        = ( 51, 255,  51)
        ORANGE       = (255, 128,   0)
        RED          = (255,   0,   0)
        BROWN        = (165,  42,  42)
        
class Fonts(Enum):
        BIG          = os.path.join(GAME_DIR, 'Assets', 'Fonts', 'Cave-Stone.ttf')  
        SMALL        = os.path.join(GAME_DIR, 'Assets', 'Fonts', '8-BIT.TTF') 

class Audio(Enum):
        AMBIENT      = os.path.join(GAME_DIR, 'Assets', 'Audio', 'Menu.wav')
        BUTTON       = os.path.join(GAME_DIR, 'Assets', 'Audio', 'Button.wav')

class Images(Enum):
        CAVE         = os.path.join(GAME_DIR, 'Assets', 'Images', 'cave.jpg')
        DARK_CAVE    = os.path.join(GAME_DIR, 'Assets', 'Images', 'cave_black.jpg')
        GAME_ICON    = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone.png')
        GAME_ICON_BG = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone_BG.jpg')
        ROVER        = os.path.join(GAME_DIR, 'Assets', 'Images', 'rover_top.png')
        DRONE        = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone_top.png')
        
        CAVE_MAP     = os.path.join(GAME_DIR, 'Assets',    'Map', 'map.png')
        CAVE_MATRIX  = os.path.join(GAME_DIR, 'Assets',    'Map', 'map_matrix.txt')
        CAVE_WALLS   = os.path.join(GAME_DIR, 'Assets',    'Map', 'walls.png')
        CAVE_FLOOR   = os.path.join(GAME_DIR, 'Assets',    'Map', 'floor.png')

class RectHandle(Enum):
        CENTER       = 'Center'
        MIDTOP       = 'Midtop'
        MIDRIGHT     = 'Midright'
        MIDLEFT      = 'Midleft'

class Brush(Enum):
        ROUND        = 0
        ELLIPSE      = 1
        CHAOTIC      = 2
        DIAMOND      = 3
        OCTAGON      = 4
        RECTANGULAR  = 5

class Axes():
        def __init__(self, step_len):
                self.up      = 0
                self.diag_q1 = step_len
                self.right   = 2*step_len
                self.diag_q4 = 3*step_len
                self.down    = 4*step_len
                self.diag_q3 = 5*step_len
                self.left    = 6*step_len
                self.diag_q2 = 7*step_len

                self.list  = [self.up, self.diag_q1, self.right, self.diag_q4,
                              self.down, self.diag_q3, self.left, self.diag_q2]


#  _____  _   _  _   _   ____  _____  ___   ___   _   _  ____  
# |  ___|| | | || \ | | / ___||_   _||_ _| / _ \ | \ | |/ ___|
# | |_   | | | ||  \| || |      | |   | | | | | ||  \| |\___ \
# |  _|  | |_| || |\  || |___   | |   | | | |_| || |\  | ___) |
# |_|     \___/ |_| \_| \____|  |_|  |___| \___/ |_| \_||____/

# Calculate the square of the passed argument
def sqr(x):
        return x**2

# Map the given direction to the possible pixels,
# given the length of the step
def map_direction(step_len, dir):
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
def next_cell_coords(x, y, step_len, dir):
        assert step_len>0

        target_cell, targets = map_direction(step_len, dir)

        axes = Axes(step_len)
        
        # Check on axes and diagonals
        match target_cell:
                case axes.up:
                        y -= step_len
                        return x, y
                case axes.diag_q1:
                        x += step_len
                        y -= step_len
                        return x, y
                case axes.right:
                        x += step_len
                        return x, y
                case axes.diag_q4:
                        x += step_len
                        y += step_len
                        return x, y
                case axes.down:
                        y += step_len
                        return x, y
                case axes.diag_q3:
                        x -= step_len
                        y += step_len
                        return x, y
                case axes.left:
                        x -= step_len
                        return x, y
                case axes.diag_q2:
                        x -= step_len
                        y -= step_len
                        return x, y

        # Check on pixels between axes and diagonals
        for i in axes.list:
                if i==0:
                        check = range(axes.list[-1] + 1, targets)
                else:
                        check = range(axes.list[axes.list.index(i)-1]+1, i)
                
                for j in check:
                        if target_cell==j:
                                match i:
                                        case axes.up:
                                                x -= targets - j
                                                y -= step_len
                                                return x, y
                                        case axes.diag_q1:
                                                x += j
                                                y -= step_len
                                                return x, y
                                        case axes.right:
                                                x += step_len
                                                y -= i - j
                                                return x, y
                                        case axes.diag_q4:
                                                x += step_len
                                                y += i - j
                                                return x, y
                                        case axes.down:
                                                x += i - j
                                                y += step_len
                                                return x, y
                                        case axes.diag_q3:
                                                x -= j - i + step_len
                                                y += step_len
                                                return x, y
                                        case axes.left:
                                                x -= step_len
                                                y += i - j
                                                return x, y
                                        case axes.diag_q2:
                                                x -= step_len
                                                y -= j - i + step_len
                                                return x, y

def wall_hit(map_matrix, pos):
        if map_matrix[pos[1]][pos[0]]==1:
                return True

        return False