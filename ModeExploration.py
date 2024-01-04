import pygame

class ModeExploration:
    def __init__(self, map_matrix, surface):
        self.delay = 25  # Milliseconds
        self.map_matrix = map_matrix
        self.surface = surface
        
    def next_point(self, id, pos, step):
        pygame.time.delay(self.delay)

        pos = (pos[0] - (id+1)*10, pos[1] - 10)

        return pos
    
    def mission_completed(self):
        return False
    
    def wall_hit(self, pos, icon):
        return False
    
    def line_of_sight(self):
        pass
