import pygame
import Assets
from ModeExploration import ModeExploration
from ModeSearchNRescue import ModeSearchNRescue

class Drone():
    def __init__(self, game, id, drone_rect, color, icon):
        self.game        = game
        self.settings    = game.sim_settings
        self.id          = id
        self.rect        = drone_rect
        self.radius      = 40   # TO BE CALCULATED BASED ON MAP DIMENSION
        self.pos         = drone_rect.center
        self.color       = color
        self.alpha       = 150
        self.icon        = icon
        self.pos_history = [self.pos]
        
        # EXPLORATION is 0 / Search&Rescue is 1
        self.explorer = ModeExploration(self.pos, self.settings[3]) if self.settings[0]==0 else ModeSearchNRescue(self.pos)
        
        # Calculate next position
        self.next_pos = self.explorer.next_point(self.id)

        self.blit_drone()

    # Calculate the next position of the drone
    def move(self):
        self.pos_history.append(self.pos)

        self.pos = self.next_pos

        self.next_pos = self.explorer.next_point(self.id)
    
    def draw(self):
        self.draw_path()
        self.blit_drone()

    def draw_path(self):
        self.floor_surf = pygame.Surface((self.game.width,self.game.height), pygame.SRCALPHA)
        pygame.draw.lines(self.floor_surf, (*self.color, int(2*self.alpha/3)), False, self.pos_history, self.radius)
        # Blit the color surface onto the target surface
        self.game.window.blit(self.floor_surf, (0,0))

    def blit_drone(self):
        # Create a surface to draw the circle (              dimensions, activate transprancy)
        self.circle_surface = pygame.Surface((self.radius, self.radius),      pygame.SRCALPHA)
                        # (            surface,                     color, center of the circle on the surface,      radius)
        pygame.draw.circle(self.circle_surface, (*self.color, self.alpha),           (self.radius,self.radius), self.radius)

        # Blit the circle at the initial point
        self.game.window.blit(self.circle_surface, self.pos)
        
        # The walls cover everything but the drone icon
        cave_walls = pygame.image.load(Assets.Images['CAVE_WALLS'].value).convert_alpha()
        self.game.window.blit(cave_walls, (0, 0))

        # Blit the drone at the initial point
        self.game.window.blit(self.icon, self.pos)
