import pygame
import Assets

class Drone():
    def __init__(self, game, drone_rect, color, icon):
        self.game  = game
        self.rect  = drone_rect
        self.pos   = drone_rect.center
        self.color = color
        self.icon  = icon

    # Calculate the next position of the drone
    def move_drone(self, step):
       self.next_pos = (self.pos[0] + step, self.pos[1])

       return self.next_pos
    
    def draw_drone(self):
        # Calculate the radius of the circle
        radius = 40
            
        # Create a surface to draw the circle
        circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (*self.color, 128), (radius,radius), radius)   
        # Blit the circle surface onto the game window
        self.game.window.blit(circle_surface, (self.rect.centerx - radius, self.rect.centery - radius))
        # Create drone
        self.game.window.blit(self.icon, (self.rect.centerx - self.icon.get_width() / 2, self.rect.centery - self.icon.get_height() / 2))
        
        # Update the display
        pygame.display.update()