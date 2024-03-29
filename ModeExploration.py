import pygame
import sys
import random as rand
from Assets import Axes, next_cell_coords

class ModeExploration:
    def __init__(self, map_matrix, surface):
        self.delay = 0  # Milliseconds
        self.map_matrix = map_matrix
        self.surface = surface
    
    def next_pos(self, pos, step, graph, node_id):
        dirs    = list(range(360))    # How many directions can it take (put 360 for every direction)
        targets = []
        dir_res = int(360/len(dirs))

        for i in range(len(dirs)):
            targets.append([0,0])

        for i in dirs:
            targets[i][0], targets[i][1] = next_cell_coords(*pos, step, i*dir_res)

        # If there is at least one dir left to be explored
        while dirs:
            chosen_dir = rand.choice(dirs)
            graph.add_node(node_id, *targets[chosen_dir])

            if graph.is_free(graph.surface):
                return *targets[chosen_dir],
        
            dirs.remove(chosen_dir)
            
        # If there are no dirs left with white pixels just beyond the edge of the vision circle
        # move back one step
        return (graph.x[node_id-3], graph.y[node_id-3])

    def mission_completed(self):
        return False
    
    def wall_hit(self, pos):
        if self.map_matrix[pos[1]][pos[0]]==1:
            return True
        
        return False
    
    def line_of_sight(self):
        pass
