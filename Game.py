import os
import sys
import pygame
import Assets
from MainMenu import MainMenu
from OptionsMenu import OptionsMenu
from SimulationMenu import SimulationMenu
from CreditsMenu import CreditsMenu
from MapGenerator import MapGenerator
from MissionControl import MissionControl

class Game():
    def __init__(self): 
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # Initialise pygame features
        pygame.init()
        
        # If we run the game we are not necessary playing
        self.running, self.playing = True, False
        
        # Initialise key flags to navigate in the menu
        self.UP_KEY,   self.DOWN_KEY, self.START_KEY = False, False, False
        self.BACK_KEY, self.LEFT_KEY, self.RIGHT_KEY = False, False, False
        
        self.to_windowed()

        # Initialise each menu and set the current one
        self.options         = OptionsMenu(self)
        self.main_menu       = MainMenu(self)
        self.credits         = CreditsMenu(self)
        self.simulation      = SimulationMenu(self)
        self.curr_menu       = self.main_menu


    #   ____     _     __  __  _____   _       ___    ___   ____  
    #  / ___|   / \   |  \/  || ____| | |     / _ \  / _ \ |  _ \ 
    # | |  _   / _ \  | |\/| ||  _|   | |    | | | || | | || |_) |
    # | |_| | / ___ \ | |  | || |___  | |___ | |_| || |_| ||  __/ 
    #  \____|/_/   \_\|_|  |_||_____| |_____| \___/  \___/ |_|    
    
    # Run the simulation
    def game_loop(self):
        if self.playing:
            # Settings : [Mode, Map Dimension, Seed, Drone Number]
            self.sim_settings  = self.simulation.get_sim_settings()
            # Generate the cave
            self.cartographer = MapGenerator(self, True)
            # Prep and Start the mission
            self.mission_control = MissionControl(self)


    #  __  __     _     _   _     _      ____  _____      ___  _   _  ____   _   _  _____  ____  
    # |  \/  |   / \   | \ | |   / \    / ___|| ____|    |_ _|| \ | ||  _ \ | | | ||_   _|/ ___|
    # | |\/| |  / _ \  |  \| |  / _ \  | |  _ |  _|       | | |  \| || |_) || | | |  | |  \___ \
    # | |  | | / ___ \ | |\  | / ___ \ | |_| || |___      | | | |\  ||  __/ | |_| |  | |   ___) |
    # |_|  |_|/_/   \_\|_| \_|/_/   \_\ \____||_____|    |___||_| \_||_|     \___/   |_|  |____/

    # Check player inputs
    def check_events(self):
        # Get the input
        for event in pygame.event.get():
            match event.type:
                # If the player clicks the x on top of the window exit the game
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # If the player clicks something on the keyboard
                # they can go up or down with the arrows or
                # they can select with ENTER and go back with BACKSPACE
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_RETURN:
                            self.START_KEY = True
                        case pygame.K_BACKSPACE:
                            self.BACK_KEY  = True
                        case pygame.K_DOWN:
                            self.DOWN_KEY  = True
                        case pygame.K_UP:
                            self.UP_KEY    = True
                        case pygame.K_LEFT:
                            self.LEFT_KEY  = True
                        case pygame.K_RIGHT:
                            self.RIGHT_KEY = True
                    
    # Reset pushed key flags
    def reset_keys(self):
        self.UP_KEY,   self.DOWN_KEY, self.START_KEY = False, False, False
        self.BACK_KEY, self.LEFT_KEY, self.RIGHT_KEY = False, False, False


    #  __  __     _     _   _     _      ____  _____      ____   ___  ____   ____   _         _    __   __
    # |  \/  |   / \   | \ | |   / \    / ___|| ____|    |  _ \ |_ _|/ ___| |  _ \ | |       / \   \ \ / /
    # | |\/| |  / _ \  |  \| |  / _ \  | |  _ |  _|      | | | | | | \___ \ | |_) || |      / _ \   \ V /
    # | |  | | / ___ \ | |\  | / ___ \ | |_| || |___     | |_| | | |  ___) ||  __/ | |___  / ___ \   | |
    # |_|  |_|/_/   \_\|_| \_|/_/   \_\ \____||_____|    |____/ |___||____/ |_|    |_____|/_/   \_\  |_|

    # Update the display
    def blit_screen(self):
        self.window.blit(self.display, (0, 0))
        pygame.display.update()
        self.reset_keys()

    # Maximise the window
    def to_maximised(self):
        # Choose and set window dimensions
        self.width = Assets.FULLSCREEN_W
        self.height = Assets.FULLSCREEN_H

        # Initialise window
        self.display = pygame.Surface((self.width,self.height))
        self.window = pygame.display.set_mode((self.width,self.height), pygame.SCALED)
        
        # Set window title
        pygame.display.set_caption('Cave Game')

        # Set game icon
        pygame.display.set_icon(pygame.image.load(Assets.Images['GAME_ICON'].value))
        # pygame.display.set_icon(pygame.image.load(Assets.Images['GAME_ICON_BG'].value))

        return self.display

    # Return to the originial window dimensions
    def to_windowed(self):
        # Choose and set window dimensions
        self.width = Assets.DISPLAY_W
        self.height = Assets.DISPLAY_H

        # Initialise window
        self.display = pygame.Surface((self.width,self.height))
        self.window  = pygame.display.set_mode((self.width,self.height), pygame.SCALED)

        # Set window title
        pygame.display.set_caption('Cave Game')

        # Set game icon
        pygame.display.set_icon(pygame.image.load(Assets.Images['GAME_ICON'].value))
        # pygame.display.set_icon(pygame.image.load(Assets.Images['GAME_ICON_BG'].value))

        return self.display
