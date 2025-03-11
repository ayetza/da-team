import random

def generate_random_position(grid_size, occupied_positions):
    while True:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        position = (x, y)
        if position not in occupied_positions:
            return position
        
def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])