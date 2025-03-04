import random
from .base import TrafficAgent

class Vehicle(TrafficAgent):

#     def setup(self):
#         super().setup()
#         self.ticketed = False
#         self.collision = False
#         self.speed_limit = 5
#         self.speed = random.randint(0, self.speed_limit)

    def __init__(self, vehicle_id):
        super().__init__()
        self.id = vehicle_id
        self.ticketed = False
        self.collision = False
        self.speed_limit = 5
        self.speed = random.randint(0, self.speed_limit)
    
    def accelerate(self):
        if random.random() < 0.7:
            self.speed += random.randint(1, 3)
        self.speed = min(self.speed, 10)
    
    def decelerate(self):
        if random.random() < 0.5:
            self.speed -= 1
        self.speed = max(self.speed, 0)

# # Movimiento del vehiculo en la cuadricula
#     def move(self):
#         dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
#         new_x = max(0, min(self.position[0] + dx, self.model.grid_size - 1))
#         new_y = max(0, min(self.position[1] + dy, self.model.grid_size - 1))
#         self.position = (new_x, new_y)
#         self.check_collision()
#         self.movements += 1
    
    def move(self, grid_size):
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x = max(0, min(self.position[0] + dx, grid_size - 1))
        new_y = max(0, min(self.position[1] + dy, grid_size - 1))
        self.position = (new_x, new_y)
        self.movements += 1
        return {"new_position": self.position}
    
#     # Detección de colisiones
#     def check_collision(self):
#         all_vehicles = self.model.cars + self.model.motorcycles
#         for vehicle in all_vehicles:
#             if vehicle != self and vehicle.position == self.position:
#                 self.collision = True
#                 vehicle.collision = True
    
    def check_collision(self, all_vehicles):
        for vehicle in all_vehicles:
            if vehicle is not self and vehicle.position == self.position:
                self.collision = True
                vehicle.collision = True
                return True
        return False
        
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "id": self.id,
            "ticketed": self.ticketed,
            "collision": self.collision,
            "speed_limit": self.speed_limit
        })
        return base_dict
    

# class Car(Vehicle):
#     def setup(self):
#         super().setup()
#         self.speed_limit = 5

#     def obey_instructions(self):
#         if random.random() < 0.8:
#             self.speed = min(self.speed, self.speed_limit)
#         else:
#             self.accelerate()

class Car(Vehicle):
    def __init__(self, car_id):
        super().__init__(car_id)
        self.speed_limit = 5
    
    def obey_instructions(self):
        if random.random() < 0.8:  # 80% chance to obey
            self.speed = min(self.speed, self.speed_limit)
        else:
            self.accelerate()

# class Motorcycle(Vehicle):
#     def setup(self):
#         super().setup()
#         self.speed_limit = 7

#     def obey_instructions(self):
#         if random.random() < 0.6:
#             self.speed = min(self.speed, self.speed_limit)
#         else:
#             self.accelerate()

class Motorcycle(Vehicle):
    def __init__(self, moto_id):
        super().__init__(moto_id)
        self.speed_limit = 7
    
    def obey_instructions(self):
        if random.random() < 0.6:  # 60% chance to obey
            self.speed = min(self.speed, self.speed_limit)
        else:
            self.accelerate()