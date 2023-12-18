import pygame

class ModeExploration:
    def __init__(self,start_point, num_drones):
        self.start_point = start_point
        self.num_drones = num_drones
        # Delay in milliseconds 
        self.delay = 300
        # Initialize your class attributes here
        self.stop_movement_flag = False
        self.step= 0
        
    def next_point(self):
        self.next_point = []  
        for i in range(self.num_drones):
            pygame.time.delay(self.delay) 
            point = self.start_point[i] 
            self.tmp_next_point = (point[0]-i*10, point[1] - 10)
            self.next_point.append(self.tmp_next_point)
        self.step += 1
        if self.step > 10:
            self.stop_movement_flag = True
            self.finish_exploration()
        return self.next_point
    
    def finish_exploration(self):
        
        return self.stop_movement_flag
