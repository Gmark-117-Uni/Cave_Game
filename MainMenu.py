import sys
import time
import pygame
import pygame.mixer as mix
import Assets
from Menu import Menu

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)

        # Get the list of states for this menu and set the current one
        self.states = Assets.main_menu_states   # ['Start', 'Options',
                                                # 'Credits', 'Exit']
        self.state   = self.states[0]

        # Get game options
        self.options = game.options
        
        # Define positions for the texts
        self.align_left      = self.mid_w - 485
        self.title_height    = self.mid_h - 250
        self.subtitle_height = self.mid_h - 100

        self.states_x = [self.align_left] * len(self.states)
        self.states_y = [self.mid_h - 20,    # Start
                         self.mid_h + 20,    # Options
                         self.mid_h + 60,    # Credits
                         self.mid_h + 100]   # Exit
        
        # Set the initial and possible positions of the cursor and it's offset
        self.cursor_offset = -25

        self.cursor_x = [self.states_x[0] + self.cursor_offset] * len(self.states)
        self.cursor_y = [self.states_y[0],    # Start
                         self.states_y[1],    # Options
                         self.states_y[2],    # Credits
                         self.states_y[3],]   # Exit
        
        self.cursor_pos = [self.cursor_x[0], self.cursor_y[0]]

    # Display the Main menu
    def display(self):
        self.run_display = True
        
        # Initialize the mixer module for audio
        mix.init()
        
        # Play the ambient music if the options allow it
        if self.options.sound_on_off == 'on' and not mix.music.get_busy():
            mix.music.play(-1)
        
        while self.run_display:
            # Check for inputs
            self.game.check_events()
            self.check_input()
            time.sleep(0.05)

            # Set the background
            self.game.display.blit(self.background,(0,0))
            
            # Set the positions on the screen
            # TITLE
            self.draw_text('CAVE EXPLORATION', 110,
                           self.align_left,
                           self.title_height,
                           Assets.Fonts['BIG'].value,
                           Assets.Colors['EUCALYPTUS'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            # VOICES
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
            
    # Handle user input
    def check_input(self):
        # Check if the player wants to move the cursor
        [self.cursor_pos, self.state] = self.move_cursor(self.states, self.state, self.cursor_pos,
                                                         self.cursor_x, self.cursor_y)
        
        # Reach the selected menu
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
