import pygame
import random as rand
from Assets import Axes, next_cell_coords

class ModeExploration:
    def __init__(self, map_matrix, surface):
        self.delay = 0  # Milliseconds
        self.map_matrix = map_matrix
        self.surface = surface
        
    def next_pos(self, pos, step):
        pygame.time.delay(self.delay)

        next_pos, unexplored_dirs = self.choose_dir(pos, step)

        return next_pos, unexplored_dirs
    
    def choose_dir(self, pos, step):
        dirs    = list(range(16))
        targets = []
        dir_res = int(360/len(dirs))

        for i in range(len(dirs)):
            targets.append([0,0])

        for i in dirs:
            targets[i][0], targets[i][1] = next_cell_coords(pos[0], pos[1], step, i*dir_res)

        chosen_dir = rand.choice(dirs)
        while self.wall_hit(targets[chosen_dir]):
            chosen_dir = rand.choice(dirs)

        next_pos = (targets[chosen_dir][0], targets[chosen_dir][1])
        dirs.remove(chosen_dir)

        return next_pos, dirs

    def mission_completed(self):
        return False
    
    def wall_hit(self, pos):
        if self.map_matrix[pos[1]][pos[0]]==1:
            return True
        
        return False
    
    def line_of_sight(self):
        pass
