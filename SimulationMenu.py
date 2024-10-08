import os
import time
import configparser
import pygame
import Assets
from Menu import Menu

class SimulationMenu(Menu):
    def __init__(self, game):
        super().__init__(game)

        # Get the list of states for this menu and set the current one
        self.states = Assets.sim_menu_states    # ['Mode', 'Map Dimension', 'Seed', 'Drones',
                                                #  'Scan Mode', 'Back', 'Start Simulation']
        self.default_state = len(self.states) - 1
        self.state  = self.states[self.default_state]

        # Initialise the possible options and their iterators
        self.mode_options   = Assets.mode_options
        self.map_options    = Assets.map_options
        self.scan_options   = Assets.scan_options

        self.mode      = 0
        self.map_dim   = 0
        self.n_drones  = 3
        self.scan_mode = 0
       
        # Define positions for menu text
        self.align_left      = self.mid_w - 50
        self.align_right     = self.mid_w + 50
        self.subtitle_height = self.mid_h - 170
        
        self.states_x = [self.align_left] * (len(self.states)-2)
        self.states_x.extend([self.mid_w] * 2)
        self.states_y = [self.mid_h -  90,  # Mode
                         self.mid_h -  50,  # Map Dimension
                         self.mid_h -  10,  # Seed
                         self.mid_h +  30,  # Drones
                         self.mid_h +  70,  # Scan Mode
                         self.mid_h + 120,  # Back
                         self.mid_h + 220]  # Start Simulation
        
        # Set the initial position of the cursor
        self.cursor_offset = -30

        self.cursor_x = [self.align_left - 110 + self.cursor_offset,  # Mode
                         self.align_left - 310 + self.cursor_offset,  # Map Dimension
                         self.align_left -  95 + self.cursor_offset,  # Seed
                         self.align_left - 145 + self.cursor_offset,  # Drones
                         self.align_left - 220 + self.cursor_offset,  # Scan Mode
                         self.mid_w      -  45 + self.cursor_offset,  # Back
                         -100]                                        # Start Simulation
        self.cursor_y = [self.states_y[0],  # Mode
                         self.states_y[1],  # Map Dimension
                         self.states_y[2],  # Seed
                         self.states_y[3],  # Drones
                         self.states_y[4],  # Scan Mode
                         self.states_y[5],  # Back
                         -100]              # Start Simulation
        
        self.cursor_pos = [self.cursor_x[self.default_state],
                           self.cursor_y[self.default_state]]

        # Set the seed input cursor position
        self.input_cursor_offset = 25

        # Set the seed input
        self.set_seed_input()

        # Initialize the number input flag
        self.number_input = False  
    
    # Display the Simulation menu
    def display(self):
        self.run_display = True

        while self.run_display:
            # Check for inputs
            self.game.check_events()
            self.check_input()
            time.sleep(0.05)

            # Set background 
            self.game.display.blit(self.dark_background,(0,0))

            # Display sound and volume options
            # TITLE
            self.draw_text('Simulation Settings', 50,
                           self.mid_w,
                           self.subtitle_height,
                           Assets.Fonts['BIG'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['CENTER'].value)
            # VOICES
            self.draw_text('Mode', 25,
                           self.states_x[0],
                           self.states_y[0],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Map dimension', 25,
                           self.states_x[1],
                           self.states_y[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Seed', 25,
                           self.states_x[2],
                           self.states_y[2],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Drones', 25,
                           self.states_x[3],
                           self.states_y[3],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Scan Mode', 25,
                           self.states_x[4],
                           self.states_y[4],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Back', 25,
                           self.states_x[5],
                           self.states_y[5],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['CENTER'].value)
            self.draw_text('Start Simulation',
                           100 if self.state==self.states[self.default_state] else 80,
                           self.states_x[6],
                           self.states_y[6],
                           Assets.Fonts['BIG'].value,
                           Assets.Colors['RED'].value if self.state==self.states[self.default_state]
                           else Assets.Colors['EUCALYPTUS'].value,
                           Assets.RectHandle['CENTER'].value)
            
            # VALUES
            self.draw_text(f'{self.mode_options[self.mode]}', 25,
                           self.align_right,
                           self.states_y[0],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['GREENDARK'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text(f'{self.map_options[self.map_dim]}', 25,
                           self.align_right,
                           self.states_y[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['GREENDARK'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            if len(self.seed_input)==0 and (time.time() % 1)>=0.5:
                self.draw_text('Enter Seed', 25,
                               self.align_right,
                               self.states_y[2],
                               Assets.Fonts['SMALL'].value,
                               Assets.Colors['RED'].value,
                               Assets.RectHandle['MIDLEFT'].value)
            else:
                self.draw_text(f'{self.seed_input}', 25,
                               self.align_right,
                               self.states_y[2],
                               Assets.Fonts['SMALL'].value,
                               Assets.Colors['GREENDARK'].value,
                               Assets.RectHandle['MIDLEFT'].value)
            self.draw_text(f'{self.n_drones}', 25,
                           self.align_right,
                           self.states_y[3],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['GREENDARK'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text(f'{self.scan_options[self.scan_mode]}', 25,
                           self.align_right,
                           self.states_y[4],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['GREENDARK'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            
            # CURSORS
            self.draw_text('X', 30,
                           self.cursor_pos[0],
                           self.cursor_pos[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['RED'].value,
                           Assets.RectHandle['CENTER'].value)
            self.draw_input_cursor()

            self.game.blit_screen()
            
            # Reset state and cursor position
            if self.run_display==False:
                self.state      = self.states[self.default_state]
                self.cursor_pos = [self.cursor_x[self.default_state],
                                   self.cursor_y[self.default_state]]

    # Draw the input cursor for the Seed option
    def draw_input_cursor(self):
        # If the player is currently on the Seed option ...
        if self.state == 'Seed':
            # ... Draw a cursor line to indicate the input field
            pygame.draw.line(self.game.display,
                             Assets.Colors['GREENDARK'].value,
                             (self.input_cursor_x, self.input_cursor_y),
                             (self.input_cursor_x + 20, self.input_cursor_y),
                             4)

    # Handle user input
    def check_input(self):
        # Check if the player wants to move the cursor
        [self.cursor_pos, self.state] = self.move_cursor(self.states, self.state, self.cursor_pos,
                                                         self.cursor_x, self.cursor_y)
        
        # Depending on the current option, delete the last input or go back to the Main menu
        if self.game.BACK_KEY:
            self.play_button(self.game.options.button_sound)
            match self.state:
                case 'Seed':
                    self.set_seed()
                    return
                case _:
                    self.run_display = self.to_main_menu()
                    return

        # Set the value of the current option
        if self.game.START_KEY:
            self.play_button(self.game.options.button_sound)

            match self.state:
                # Launch the simulation
                case 'Start Simulation':
                    if len(self.seed_input)!=0:
                        self.save_symSettings()
                        self.game.playing = True
                        self.run_display = False
                        self.game.blit_screen()
                        return
                # Go back to the Main menu
                case 'Back':
                    self.run_display = self.to_main_menu()
                    return
                case 'Mode':
                    self.mode = 1 if self.mode == 0 else 0
                    return
                case 'Map Dimension':
                    match self.map_dim:
                        case 0: self.map_dim = 1
                        case 1: self.map_dim = 2
                        case 2: self.map_dim = 0
                    self.set_seed_input()
                    self.game.blit_screen()
                    return
                case 'Seed':
                    if len(self.seed_input)>0:
                        self.state = self.states[-1]
                case 'Drones':
                    match self.n_drones:
                        case 8:
                            self.n_drones = 3
                        case _:
                            self.n_drones += 1
                    return
                case 'Scan Mode':
                    self.scan_mode = 1 if self.scan_mode == 0 else 0
                    return
        
        # Handle seed input
        self.set_seed()
    
    # Handle input for the Seed option
    def set_seed(self):
        if not self.number_input:
            # Get pressed keys
            keys = pygame.key.get_pressed()
            # Find the pressed number
            for key in range(0, 10):
                if keys[pygame.K_0 + key]:
                    # Update the seed string
                    self.seed_input += str(key)
                    self.number_input = True
                    # Move the input cursor
                    self.input_cursor_x = self.align_right + self.input_cursor_offset*len(self.seed_input)
                    return

            # Handle deleting last input
            if keys[pygame.K_BACKSPACE]:
                # Update the seed string
                self.seed_input = self.seed_input[:-1]
                self.number_input = True
                # Move the input cursor
                self.input_cursor_x = self.align_right + self.input_cursor_offset*len(self.seed_input)
                return

        # Reset the flag if no keys are pressed
        if not any(pygame.key.get_pressed()):
            self.number_input = False

    # Save selected options
    def save_symSettings(self):
        # Set configuration file path
        config_path = (os.path.join(Assets.GAME_DIR, 'GameConfig', 'symSettings.ini'))  
        config = configparser.ConfigParser()

        # Define the options values
        config['symSettings'] = {
            'Mode': self.mode_options[self.mode],
            'Map_dimension': self.map_options[self.map_dim],
            'Seed': self.seed_input,
            'Drones': self.n_drones,
            'Scan Mode': self.scan_options[self.scan_mode]
        }

        # Create or overwrite the file
        with open(config_path, 'w') if os.path.isfile(config_path) else open(config_path, 'a') as configfile:
            config.write(configfile)

    # Return the chosen map dimension
    def get_sim_settings(self):
        match self.map_dim:
            case 0: map_dim = 'SMALL'
            case 1: map_dim = 'MEDIUM'
            case 2: map_dim = 'BIG'
        
        settings = [self.mode,
                    map_dim,
                    int(self.seed_input),
                    self.n_drones,
                    self.scan_mode]
        
        return settings

    # Set the seed
    def set_seed_input(self):
        match self.map_dim:
            case 0: self.seed_input = str(Assets.seed[0])
            case 1: self.seed_input = str(Assets.seed[1])
            case 2: self.seed_input = str(Assets.seed[2])
        
        self.set_input_cursor_pos()

    # Update the position of the Seed cursor
    def set_input_cursor_pos(self):
        self.input_cursor_x = self.align_right + self.input_cursor_offset*len(self.seed_input)
        self.input_cursor_y = self.states_y[2] + 15
