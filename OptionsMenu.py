import configparser
import os
import time
import pygame
import pygame.mixer as mix
from Menu import Menu
import Assets

class OptionsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)

        # Get the list of states for this menu and set the current one
        self.states = Assets.options_menu_states    # ['Game Volume', 'Music Volume',
                                                    # 'Button Sound', 'Back']
        self.default_state = 0
        self.state  = self.states[self.default_state]
        
        # Define positions for the texts
        self.align_left      = self.mid_w - 50
        self.align_right     = self.mid_w + 50
        self.subtitle_height = self.mid_h - 150

        self.states_x = [self.align_left] * (len(self.states)-1)
        self.states_x.append(self.mid_w)
        self.states_y = [self.mid_h - 40,    # Game Volume
                         self.mid_h,         # Music Volume
                         self.mid_h + 40,    # Button Sound
                         self.mid_h + 120]   # Back
        
        # Set the initial and possible positions of the cursor
        self.cursor_offset = -30

        self.cursor_x = [self.mid_w - 335 + self.cursor_offset,    # Game Volume
                         self.mid_w - 350 + self.cursor_offset,    # Music Volume
                         self.mid_w - 335 + self.cursor_offset,    # Button Sound
                         self.mid_w -  45 + self.cursor_offset]    # Back
        self.cursor_y = [self.states_y[0],     # Game Volume
                         self.states_y[1],     # Music Volume
                         self.states_y[2],     # Button Sound
                         self.states_y[3]]     # Back
        
        self.cursor_pos = [self.cursor_x[self.default_state],
                           self.cursor_y[self.default_state]]

        # Load options from the configuration file
        self.load_options()

        # Define slider positions
        self.slider_x, self.slider_y = self.align_right , self.states_y[0]
        self.max_slider_width        = 200
        self.slider_width            = int(self.max_slider_width * (self.volume / 200))

    # Display the Options menu
    def display(self):
        self.run_display = True
        
        while self.run_display:
            # Check for inputs
            self.game.check_events()
            self.check_input()
            time.sleep(0.1)

            # Set background
            self.game.display.blit(self.dark_background, (0, 0))
            
            # Display sound and volume options
            # TITLE
            self.draw_text('Audio settings', 50,
                           self.mid_w,
                           self.subtitle_height,
                           Assets.Fonts['BIG'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDTOP'].value)
            # VOICES
            self.draw_text('Game volume', 25,
                           self.states_x[0],
                           self.states_y[0],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Music volume', 25,
                           self.states_x[1],
                           self.states_y[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Button sound', 25,
                           self.states_x[2],
                           self.states_y[2],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['MIDRIGHT'].value)
            self.draw_text('Back', 25,
                           self.states_x[3],
                           self.states_y[3],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['WHITE'].value,
                           Assets.RectHandle['CENTER'].value)
            # VALUES
            self.draw_volume_slider()
            self.draw_text('on' if self.sound_on_off=='on' else 'off', 25,
                           self.align_right,
                           self.states_y[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['EUCALYPTUS'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            self.draw_text('on' if self.button_sound=='on' else 'off', 25,
                           self.align_right,
                           self.states_y[2],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['EUCALYPTUS'].value,
                           Assets.RectHandle['MIDLEFT'].value)
            # CURSOR
            self.draw_text('X', 30,
                           self.cursor_pos[0],
                           self.cursor_pos[1],
                           Assets.Fonts['SMALL'].value,
                           Assets.Colors['RED'].value,
                           Assets.RectHandle['CENTER'].value)
            
            self.game.blit_screen()
            
            # Reset state and cursor position
            if self.run_display==False:
                self.state = self.states[self.default_state]
                self.cursor_pos = [self.cursor_x[self.default_state],
                                self.cursor_y[self.default_state]]
            
    # Draw the volume slider
    def draw_volume_slider(self):
        # Draw the background bar
        pygame.draw.rect(self.game.display, Assets.Colors['WHITE'].value,
                         (self.slider_x, self.slider_y - 8, self.max_slider_width, 20))
        # Draw the slider bar
        pygame.draw.rect(self.game.display, Assets.Colors['GREEN'].value,
                         (self.slider_x, self.slider_y - 8, self.slider_width, 20))
        
    # Handle user input
    def check_input(self):
        # Check if the player wants to move the cursor
        [self.cursor_pos, self.state] = self.move_cursor(self.states, self.state, self.cursor_pos,
                                                         self.cursor_x, self.cursor_y)
        
        # Get the pressed keys
        keys = pygame.key.get_pressed()

        # Go back to the Main menu
        if self.game.BACK_KEY or (self.game.START_KEY and self.state == 'Back'):
            self.save_options()
            self.play_button(self.button_sound)
            
            self.run_display = self.to_main_menu()
            return
        
        # Set the value of the current option
        if self.game.START_KEY:
            self.play_button(self.button_sound)

            match self.state, self.sound_on_off:
                case 'Music Volume', 'on':
                    mix.music.stop()
                    self.sound_on_off = 'off'
                    return
                case 'Music Volume', 'off':
                    mix.music.play(-1)
                    self.sound_on_off = 'on'
                    return
            
            if self.state == 'Button Sound':
                self.button_sound = 'off' if self.button_sound == 'on' else 'on'
                return
        
        # Turn down the volume
        if self.state == 'Game Volume' and keys[pygame.K_LEFT]:
            self.volume_down()
            self.play_button(self.button_sound)
            return

        # Turn up the volume
        if self.state == 'Game Volume' and keys[pygame.K_RIGHT]:
            self.volume_up()
            self.play_button(self.button_sound)
    
    # Increase the volume
    def volume_up(self):
        # Set the new volume value (up to a maximum)
        self.volume = min(self.volume + 20, 200)

        # Update slider bar length
        self.slider_width = int(self.max_slider_width * (self.volume / 200))

        # Set the new volume
        mix.music.set_volume(self.volume/400)
        self.button.set_volume(self.volume/400)

    # Decrease the volume
    def volume_down(self):
        # Set the new volume value (up to a maximum)
        self.volume = max(self.volume -20, 0)

        # Update slider bar length
        self.slider_width = int(self.max_slider_width * (self.volume / 200))

        # Set the new volume
        mix.music.set_volume(self.volume/400)
        self.button.set_volume(self.volume/400)
                 
    # Load from file or initialise options
    def load_options(self):
        # Set configuration file path
        config_path = (os.path.join(Assets.GAME_DIR, 'GameConfig', 'options.ini'))  
        
        # Initialise options for the very first time
        if not os.path.exists(config_path):
            self.volume       = 100
            self.sound_on_off = 'on'
            self.button_sound = 'on'
            return
        
        # Load options from the configuration file
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Get the option values or set default values if not available in the config file
        self.volume       = config.getint('Options', self.states[0], fallback=100)
        self.sound_on_off = config.get('Options', self.states[1], fallback='on')
        self.button_sound = config.get('Options', self.states[2], fallback='on')
        
        # Set the volume based on the configuration file value
        mix.music.set_volume(self.volume / 400) 

    # Save selected options
    def save_options(self):
        # Set configuration file path
        config_path = (os.path.join(Assets.GAME_DIR, 'GameConfig', 'options.ini'))  
        config      = configparser.ConfigParser()
        
        # Define the options values
        config['Options'] = {
            'Game volume' : self.volume,
            'Music volume': self.sound_on_off,
            'Button sound': self.button_sound
        }
        
        # Create or overwrite the file
        with open(config_path, 'w') if os.path.isfile(config_path) else open(config_path, 'a') as configfile:
            config.write(configfile)
