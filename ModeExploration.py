import pygame

class ModeExploration:
    def __init__(self, start_pos, num_drones):
        self.pos = start_pos
        self.num_drones = num_drones
        self.delay = 300  # Milliseconds
        
    def next_point(self, id):
        pygame.time.delay(self.delay)

        self.pos = (self.pos[0] - (id+1)*10, self.pos[1] - 10)

        return self.pos
