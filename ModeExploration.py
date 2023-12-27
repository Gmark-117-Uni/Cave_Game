import pygame

class ModeExploration:
    def __init__(self, start_pos):
        self.pos = start_pos
        self.delay = 25  # Milliseconds
        
    def next_point(self, id):
        pygame.time.delay(self.delay)

        self.pos = (self.pos[0] - (id+1)*10, self.pos[1] - 10)

        return self.pos
