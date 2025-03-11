from datetime import datetime
from agents.police import Police
from agents.drone import Drone
from agents.car import Car
from agents.motorcycle import Motorcycle
from .utils import generate_random_position

class TrafficSimulation:


    def __init__(self, simulation_id, grid_size=10, num_cars=5, num_motorcycles=3):
        self.simulation_id = simulation_id
        self.grid_size = grid_size
        self.start_time = datetime.now()
        
        self.police = Police(self)
        self.drone = Drone(self)
        self.cars = [Car(i, self) for i in range(num_cars)]
        self.motorcycles = [Motorcycle(i, self) for i in range(num_motorcycles)]
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
    
    def detect_congestion(self):
        """Celdas con 3 o más vehículos se consideran congestionadas."""
        position_counts = {}
        for vehicle in self.cars + self.motorcycles:
            pos = vehicle.position
            if pos in position_counts:
                position_counts[pos] += 1
            else:
                position_counts[pos] = 1
        return [list(pos) for pos, count in position_counts.items() if count >= 3]
    
    
    def step(self):
        movement_results = {
            'cars_moved': 0,
            'motorcycles_moved': 0,
            'collisions_detected': 0,
            'congested_cells': [],
            'game_over': False,
            'reason': None,
            'task_completed': self.task_completed
        }

        for vehicle in (self.cars + self.motorcycles):
            vehicle.accelerate()
            old_pos = vehicle.position
            vehicle.move()
            if old_pos != vehicle.position:
                if isinstance(vehicle, Car):
                    movement_results['cars_moved'] += 1
                else:
                    movement_results['motorcycles_moved'] += 1
            vehicle.obey_instructions()

        self.police.step()

        for vehicle in (self.cars + self.motorcycles):
            if vehicle.speed > vehicle.speed_limit:
                self.police.issue_ticket(vehicle)

        congested_cells = self.detect_congestion()
        movement_results['congested_cells'] = congested_cells
        
        if congested_cells:
            print(f"¡Aún quedan congestiones en celdas: {congested_cells}!")
            self.police.failed_congestions += 1
            print(f"Fallos consecutivos: {self.police.failed_congestions}")
            if self.police.failed_congestions >= 3:
                print("Simulación terminada: Tres fallos consecutivos en resolver congestiones.")
                movement_results['game_over'] = True
                movement_results['reason'] = "Tres fallos consecutivos en resolver congestiones"
                return movement_results
        else:
            self.police.failed_congestions = 0

        collisions = [v for v in (self.cars + self.motorcycles) if v.collision]
        movement_results['collisions_detected'] = len(collisions)
        
        any_collision = bool(collisions)
        any_overspeed = any((v.speed > v.speed_limit) for v in (self.cars + self.motorcycles))

        if not any_collision and not any_overspeed:
            if not self.task_completed:
                self.task_completed = True
                self.task_completion_time = datetime.now()
                movement_results['task_completed'] = True

        self.current_step += 1
        return movement_results

    def end(self):
        total_movements = sum(agent.movements for agent in self.agents)
        print("\n--- Resultados Finales ---")
        print(f"Tiempo de completado: {self.task_completion_time if self.task_completion_time else 'No completado'}")
        print(f"Movimientos totales: {total_movements}")
        print(f"Movimientos del policia: {self.police.movements}")
        print(f"Multas emitidas: {len(self.police.tickets_issued)}")
        for (veh, old_s, new_s) in self.police.tickets_issued:
            print(f" - {type(veh).__name__} multado en {veh.position}: {old_s} -> {new_s}")
        print(f"Congestiones resueltas (por policía): {self.police.congestion_resolved}")
        print(f"Solicitudes de dron: {self.police.drone_requests}")

    
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
        total_movements = sum(agent.movements for agent in self.agents)
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
                "task_completion_time": self.task_completion_time.isoformat() if self.task_completion_time else None,
                "failed_congestions": self.failed_congestions,
                "total_movements": total_movements,
                "start_time": self.start_time.isoformat()
            }
        }

