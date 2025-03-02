from datetime import datetime
from agents.police import Police
from agents.drone import Drone
from agents.vehicles import Car, Motorcycle
from .utils import generate_random_position

class TrafficSimulation:

#     def setup(self):
#         self.grid_size = 10

#         self.police = Police(self)
#         self.drone = Drone(self)
#         self.cars = ap.AgentList(self, 10, Car)
#         self.motorcycles = ap.AgentList(self, 5, Motorcycle)

#         self.agents = [self.police, self.drone] + list(self.cars) + list(self.motorcycles)

#         occupied_positions = []
#         for agent in self.agents:
#             agent.position = self.random_empty_position(occupied_positions)
#             occupied_positions.append(agent.position)

#         self.task_completed = False
#         self.task_completion_time = None

    def __init__(self, simulation_id, grid_size=10, num_cars=10, num_motorcycles=5):
        self.simulation_id = simulation_id
        self.grid_size = grid_size
        self.start_time = datetime.now()
        self.police = Police()
        self.drone = Drone()
        self.cars = [Car(i) for i in range(num_cars)]
        self.motorcycles = [Motorcycle(i) for i in range(num_motorcycles)]
        self.agents = [self.police, self.drone] + self.cars + self.motorcycles
        self._initialize_positions()
        self.task_completed = False
        self.task_completion_time = None
        self.failed_congestions = 0
        self.current_step = 0
    
    def _initialize_positions(self):
        occupied_positions = []
        for agent in self.agents:
            agent.position = generate_random_position(self.grid_size, occupied_positions)
            occupied_positions.append(agent.position)

#     # Deteccion de congestion en celdas con 3 o más vehiculos
#     def detect_congestion(self):
#         position_counts = {}
#         for vehicle in self.cars + self.motorcycles:
#             pos = vehicle.position
#             position_counts[pos] = position_counts.get(pos, 0) + 1
#         return [pos for pos, count in position_counts.items() if count >= 3]
    
    def detect_congestion(self):
        position_counts = {}
        for vehicle in self.cars + self.motorcycles:
            pos = vehicle.position
            position_counts[pos] = position_counts.get(pos, 0) + 1
        return [pos for pos, count in position_counts.items() if count >= 3]
    
#     def step(self):
#         all_vehicles = self.cars + self.motorcycles
        
#         for vehicle in all_vehicles:
#             vehicle.accelerate()
#             vehicle.move()
#             vehicle.obey_instructions()
            
#             if vehicle.speed > vehicle.speed_limit:
#                 self.police.issue_ticket(vehicle)

#         self.police.request_drone_assistance()
        
#         # Deteccion y manejo de congestiones
#         congested_cells = self.detect_congestion()
#         if congested_cells:
#             print(f"¡Congestiones detectadas en celdas: {congested_cells}!")
#             all_resolved = True
#             for cell in congested_cells:
#                 if not self.police.resolve_congestion(cell):
#                     all_resolved = False
            
#             if all_resolved:
#                 self.police.failed_congestions = 0
#                 print("Todas las congestiones resueltas.")
#             else:
#                 self.police.failed_congestions += 1
#                 print(f"Fallos consecutivos en resolver congestiones: {self.police.failed_congestions}")
                
#             if self.police.failed_congestions >= 3:
#                 print("Simulación terminada: Tres fallos consecutivos en resolver congestiones.")
#                 self.stop()
#         else:
#             self.police.failed_congestions = 0
        
#         # Verificar finalizacion de tarea
#         if not any(v.collision for v in all_vehicles) and \
#            not any(v.speed > v.speed_limit for v in all_vehicles):
#             if not self.task_completed:
#                 self.task_completed = True
#                 self.task_completion_time = self.t
    
    def step(self):
        self.current_step += 1
        movement_results = {
            "cars_moved": 0,
            "motorcycles_moved": 0,
            "collisions_detected": 0
        }
        
        updated_positions = {"cars": {}, "motorcycles": {}}
        
        for car in self.cars:
            car.accelerate()
            car.move(self.grid_size)
            car.obey_instructions()
            updated_positions["cars"][car.id] = car.position
            movement_results["cars_moved"] += 1
        
        for motorcycle in self.motorcycles:
            motorcycle.accelerate()
            motorcycle.move(self.grid_size)
            motorcycle.obey_instructions()
            updated_positions["motorcycles"][motorcycle.id] = motorcycle.position
            movement_results["motorcycles_moved"] += 1
        
        self._detect_collisions()
        movement_results["collisions_detected"] = sum(1 for v in self.cars + self.motorcycles if v.collision)
        
        congested_cells = self.detect_congestion()
        movement_results["congested_cells"] = congested_cells
        
        if self.failed_congestions >= 3:
            movement_results["game_over"] = True
            movement_results["reason"] = "Three consecutive failures to resolve congestion"
        
        all_vehicles = self.cars + self.motorcycles
        if not any(v.collision for v in all_vehicles) and not any(v.speed > v.speed_limit for v in all_vehicles):
            if not self.task_completed:
                self.task_completed = True
                self.task_completion_time = self.current_step
                movement_results["task_completed"] = True
        
        return {
            "movement_results": movement_results,
            "updated_positions": updated_positions
        }
    
    def _detect_collisions(self):

        for vehicle in self.cars + self.motorcycles:
            vehicle.collision = False
        
        all_vehicles = self.cars + self.motorcycles
        for i, vehicle in enumerate(all_vehicles):
            for other in all_vehicles[i+1:]:  
                if vehicle.position == other.position:
                    vehicle.collision = True
                    other.collision = True
    
    def get_state(self):
        return {
            "simulation_id": self.simulation_id,
            "grid": {
                "size": self.grid_size
            },
            "current_step": self.current_step,
            "agents": {
                "police": self.police.to_dict(),
                "drone": self.drone.to_dict(),
                "cars": [car.to_dict() for car in self.cars],
                "motorcycles": [motorcycle.to_dict() for motorcycle in self.motorcycles]
            },
            "congested_cells": self.detect_congestion(),
            "status": {
                "task_completed": self.task_completed,
                "task_completion_time": self.task_completion_time,
                "failed_congestions": self.failed_congestions
            }
        }

