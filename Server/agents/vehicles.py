import random
from .base import TrafficAgent

class Vehicle(TrafficAgent):

    def __init__(self, vehicle_id, model=None):
        super().__init__(model)
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
    
    def move(self):
        if self.speed == 0:
            return {"new_position": self.position}
            
        primary_direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        dx, dy = primary_direction
        
        steps = min(self.speed, random.randint(1, self.speed))
        dx *= steps
        dy *= steps
        
        grid_size = self.model.grid_size
        new_x = max(0, min(self.position[0] + dx, grid_size - 1))
        new_y = max(0, min(self.position[1] + dy, grid_size - 1))
        
        old_position = self.position
        self.position = (new_x, new_y)
        self.check_collision()
        self.movements += 1
        
        return {
            "new_position": self.position,
            "old_position": old_position,
            "steps": steps
        }
    
    def check_collision(self):
        all_vehicles = self.model.cars + self.model.motorcycles
        for vehicle in all_vehicles:
            if vehicle is not self and vehicle.position == self.position:
                self.collision = True
                vehicle.collision = True
        
    def obey_instructions(self):
        pass
        
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "id": self.id,
            "ticketed": self.ticketed,
            "collision": self.collision,
            "speed_limit": self.speed_limit,
        })
        return base_dict

