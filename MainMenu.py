import sys
import time
import pygame
import pygame.mixer as mix
import Assets
from Menu import Menu

class MainMenu(Menu):
    def __init__(self, game):
        # Initialize the base class (Menu)
        super().__init__(game)

        # Get the list of menu states and set the current state
        self.states = Assets.main_menu_states  # Menu options: ['Start', 'Options', 'Credits', 'Exit']
        self.state   = self.states[0] # Initialize the first state as the current state

        # Retrieve game options from the game instance
        self.options = game.options
        
        # Define text positions for the menu items
        self.align_left      = self.mid_w - 485
        self.title_height    = self.mid_h - 250
        self.subtitle_height = self.mid_h - 100
        
        # Initialize x and y positions for each menu item
        self.states_x = [self.align_left] * len(self.states)
        self.states_y = [self.mid_h - 20,    # Start
                         self.mid_h + 20,    # Options
                         self.mid_h + 60,    # Credits
                         self.mid_h + 100]   # Exit
        
        # Set the initial position of the cursor and its offset
        self.cursor_offset = -25

        # Initialize cursor positions for each menu item
        self.cursor_x = [self.states_x[0] + self.cursor_offset] * len(self.states)
        self.cursor_y = [self.states_y[0],    # Start
                         self.states_y[1],    # Options
                         self.states_y[2],    # Credits
                         self.states_y[3]]    # Exit
        
        self.cursor_pos = [self.cursor_x[0], self.cursor_y[0]]

    # Display the Main menu
    def display(self):
        self.run_display = True # Flag to keep the menu running
        
        # Initialize the mixer module for audio playback
        mix.init()
        
        # Play ambient music if the options allow it and no music is currently playing
        if self.options.sound_on_off == 'on' and not mix.music.get_busy():
            mix.music.play(-1) # Play music indefinitely
        
        while self.run_display:
            # Check for user inputs
            self.game.check_events()
            self.check_input()
            time.sleep(0.05) # Small delay to control the frame rate

            # Set the background for the menu
            self.game.display.blit(self.background,(0,0))
            
            # Set the positions on the screen
            # TITLE
            self.draw_text('CAVE EXPLORATION', 110,
                           self.align_left,
                           self.title_height,
                           Assets.Fonts['BIG'].value,
                           Assets.Colors['EUCALYPTUS'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            # MENU OPTIONS
            self.draw_text('Main Menu', 50,
                           self.align_left,
                           self.subtitle_height,
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text('Start Simulation', 25,
                           self.states_x[0],
                           self.states_y[0],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text('Audio', 25,
                           self.states_x[1],
                           self.states_y[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text('Credits', 25,
                           self.states_x[2],
                           self.states_y[2],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text('Exit', 25,
                           self.states_x[3],
                           self.states_y[3],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            # CURSOR
            self.draw_text('X', 30,
                           self.cursor_pos[0],
                           self.cursor_pos[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['RED'].value,
                           Assets.RectHandle['CENTER'].value)

            self.game.blit_screen()
            
    # Handle user input for menu navigation
    def check_input(self):
        # Move the cursor based on player input
        [self.cursor_pos, self.state] = self.move_cursor(self.states, self.state, self.cursor_pos,
                                                         self.cursor_x, self.cursor_y)
        
        # Determine what happens when the player selects an option
        if self.game.START_KEY:
            match self.state:
                case 'Start':
                    self.game.curr_menu = self.game.simulation
                    self.play_button(self.options.button_sound)
                case 'Options':
                    self.game.curr_menu = self.game.options
                    self.play_button(self.options.button_sound)
                case 'Credits':
                    self.game.curr_menu = self.game.credits
                    self.play_button(self.options.button_sound)
                case 'Exit':
                    self.play_button(self.options.button_sound)
                    pygame.quit()
                    sys.exit()
            self.run_display = False
