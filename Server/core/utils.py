import random

#     def random_empty_position(self, occupied):
#         while True:
#             x = random.randint(0, self.grid_size - 1)
#             y = random.randint(0, self.grid_size - 1)
#             if (x, y) not in occupied:
#                 return (x, y)


def generate_random_position(grid_size, occupied_positions):
    while True:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        position = (x, y)
        if position not in occupied_positions:
            return position