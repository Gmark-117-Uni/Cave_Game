import random as rand
from Fleet import Fleet
import pygame
import Assets

class MissionControl():
    def __init__(self, game):
        # Set the seed from the settings
        rand.seed(game.sim_settings[1])

        self.game = game
        self.settings = game.sim_settings
        self.cave_gen = self.game.cave_gen
        self.cave_map = self.cave_gen.bin_map
        self.cave_png = Assets.Images['CAVE_MAP'].value
        self.surface= game.display
        
        # Find a suitable start position
        self.set_start_pos()
        
        # Start mission
        self.start_mission()
        
        # Exit the simulation if the input is given
        while self.game.playing:
            pygame.display.update()
            self.game.check_events()

            if self.game.BACK_KEY or self.game.START_KEY:
                self.game.playing = False
                self.game.curr_menu.run_display = True
                self.game.to_windowed()

    def start_mission(self):
        # Create the drones
        self.fleet = Fleet(self.game, self, self.start_pos)

        # Keep moving the drones
        while True:
            self.fleet.move_drones()
            self.clear_previous_drones()

    # Among the starting positions of the worms, find one that is viable
    def set_start_pos(self):
        good_point = False
        while not good_point:  
            # Take one of the starting positions of the worms as the start position for the mission
            i = rand.randint(0,3)
            self.start_pos = (self.cave_gen.worm_x[i],self.cave_gen.worm_y[i])

            # If the point is white choose it as a start position
            if self.cave_map[self.start_pos[1]][self.start_pos[0]] == 0:  # White
                good_point = True

    def clear_previous_drones(self):
        # Load the CAVE_MAP image
        cave_map = pygame.image.load(self.cave_png).convert_alpha()
        # Draw the CAVE_MAP image onto the game window
        self.game.window.blit(cave_map, (0, 0))
        # Update the display
        pygame.display.update()