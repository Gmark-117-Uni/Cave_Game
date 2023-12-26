import os
import tkinter
from enum import Enum

root = tkinter.Tk()

# Game directory: ..\CaveGame
GAME_DIR = os.path.dirname(os.path.abspath(__file__))

# Display dimensions
DISPLAY_W = 1200
DISPLAY_H = 750
FULLSCREEN_W = 1920 - 5 # root.winfo_screenwidth() - 5
FULLSCREEN_H = root.winfo_screenheight() - 70

# Lists for menu voices and settings
main_menu_states    = ['Start', 'Options', 'Credits', 'Exit']
options_menu_states = ['Game Volume', 'Music Volume', 'Button Sound', 'Back']
sim_menu_states     = ['Mode', 'Map Dimension', 'Seed', 'Drones', 'Back', 'Start Simulation']
mode_options        = ["Cave exploration", "Rescue mission"]
map_options         = ["Small", "Medium", "Big"]
seed                = [     5,       19,    837]


# Calculate the square of the passed argument
def sqr(x):
        return x**2

class Colors(Enum):
        BLACK        = (0, 0, 0)
        WHITE        = (255, 255, 255)
        EUCALYPTUS   = (95, 133, 117)
        GREENDARK    = (117,132,104)
        RED          = (255,0,0)
        GREEN        = (51,255,51)

class DroneColors(Enum):
        PINK         = (255,51,153)
        VIOLET       = (153,51,255)
        BLUE         = (0,0,153)
        L_BLUE       = (51,255,255)
        GREEN        = (51,255,51)
        YELLOW       = (255,255,51)
        ORANGE       = (255,128,0)
        RED          = (255,0,0)
        
class Fonts(Enum):
        BIG        = os.path.join(GAME_DIR, 'Assets', 'Fonts', 'Cave-Stone.ttf')  
        SMALL      = os.path.join(GAME_DIR, 'Assets', 'Fonts', '8-BIT.TTF') 
        
class Audio(Enum):
        AMBIENT    = os.path.join(GAME_DIR, 'Assets', 'Audio', 'Menu.wav')
        BUTTON     = os.path.join(GAME_DIR, 'Assets', 'Audio', 'Button.wav')

class Images(Enum):
        CAVE         = os.path.join(GAME_DIR, 'Assets', 'Images', 'cave.jpg')
        DARK_CAVE    = os.path.join(GAME_DIR, 'Assets', 'Images', 'cave_black.jpg')
        GAME_ICON    = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone.png')
        GAME_ICON_BG = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone_BG.jpg')
        ROVER        = os.path.join(GAME_DIR, 'Assets', 'Images', 'rover_top.png')
        DRONE        = os.path.join(GAME_DIR, 'Assets', 'Images', 'drone_top.png')
        CAVE_MAP     = os.path.join(GAME_DIR, 'Assets', 'Map', 'map.png')
        CAVE_MATRIX  = os.path.join(GAME_DIR, 'Assets', 'Map', 'map_matrix.txt')
        CAVE_WALLS   = os.path.join(GAME_DIR, 'Assets', 'Map', 'walls.png')
        CAVE_FLOOR   = os.path.join(GAME_DIR, 'Assets', 'Map', 'floor.png')

class RectHandle(Enum):
        CENTER     = 'Center'
        MIDTOP     = 'Midtop'
        MIDRIGHT   = 'Midright'
        MIDLEFT    = 'Midleft'

class Axes():
        def __init__(self, step_len):
                self.up    = 0
                self.diag1 = step_len
                self.right = 2*step_len
                self.diag4 = 3*step_len
                self.down  = 4*step_len
                self.diag3 = 5*step_len
                self.left  = 6*step_len
                self.diag2 = 7*step_len
                self.list  = [self.up,
                              self.diag1,
                              self.right,
                              self.diag4,
                              self.down,
                              self.diag3,
                              self.left,
                              self.diag2]

class Brush(Enum):
        ROUND       = 0
        ELLIPSE     = 1
        CHAOTIC     = 2
        DIAMOND     = 3
        OCTAGON     = 4
        RECTANGULAR = 5

# Map Generator Inputs
step = 10
strength = 16
life = 75

class WormInputs(Enum):
        SMALL  = [4*step, 4*strength,    life]
        MEDIUM = [2*step, 2*strength,  4*life]
        BIG    = [  step,   strength, 15*life]
