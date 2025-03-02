# traffic_simulation/agents/police.py
import random
from .base import TrafficAgent

class Police(TrafficAgent):
    def __init__(self):
        super().__init__()
        self.tickets_issued = []
        self.congestion_resolved = 0
        self.drone_requests = 0
        self.failed_congestions = 0

#     def issue_ticket(self, vehicle):
#         if vehicle.speed > vehicle.speed_limit and not vehicle.ticketed:
#             original_speed = vehicle.speed
#             vehicle.ticketed = True
#             if random.random() < 0.7:
#                 vehicle.speed = max(vehicle.speed - 2, 2)
#             self.tickets_issued.append((vehicle, original_speed, vehicle.speed))
#             self.movements += 1
#             print(f"Multa emitida a {type(vehicle).__name__} en {vehicle.position}: {original_speed} -> {vehicle.speed}")
        
    def issue_ticket(self, vehicle, simulation):
        """Emitir una multa a un vehiculo que exceda el limite de velocidad"""
        if vehicle.speed > vehicle.speed_limit and not vehicle.ticketed:
            original_speed = vehicle.speed
            vehicle.ticketed = True
            result = {"vehicle_id": vehicle.id, "vehicle_type": vehicle.__class__.__name__.lower()}
            
            if random.random() < 0.7:
                vehicle.speed = max(vehicle.speed - 2, 2)
                result["success"] = True
            else:
                result["success"] = False
                
            self.tickets_issued.append((vehicle.id, vehicle.__class__.__name__, original_speed, vehicle.speed))
            self.movements += 1
            
            result["original_speed"] = original_speed
            result["new_speed"] = vehicle.speed
            return result
        return {"success": False, "reason": "Vehicle is not speeding or already ticketed"}
    

# # Función para resolver congestiones en una celda especifica
#     def resolve_congestion(self, cell):
#         vehicles_in_cell = [v for v in self.model.cars + self.model.motorcycles if v.position == cell]
#         if random.random() < 0.7:  
#             for vehicle in vehicles_in_cell:
#                 vehicle.speed = max(vehicle.speed - 1, 2)
#             self.congestion_resolved += 1
#             self.movements += 1
#             print(f"Congestion en {cell} resuelta.")
#             return True
#         else:
#             print(f"Fallo al resolver congestion en {cell}.")
#             return False
    
    def resolve_congestion(self, cell, simulation):
        """Resolver congestiones en una celda especifica"""
        vehicles_in_cell = [v for v in simulation.cars + simulation.motorcycles if v.position == cell]
        affected_vehicles = []
        
        if random.random() < 0.7:
            for vehicle in vehicles_in_cell:
                original_speed = vehicle.speed
                vehicle.speed = max(vehicle.speed - 1, 2)
                affected_vehicles.append({
                    "id": vehicle.id,
                    "type": vehicle.__class__.__name__.lower(),
                    "original_speed": original_speed,
                    "new_speed": vehicle.speed
                })
            self.congestion_resolved += 1
            self.movements += 1
            return {"success": True, "vehicles_affected": affected_vehicles}
        else:
            simulation.failed_congestions += 1
            return {"success": False, "consecutive_failures": simulation.failed_congestions}
        
#     # Funcion para solicitar asistencia del dron
#     def request_drone_assistance(self):
#         if random.random() < 0.5:
#             self.drone_requests += 1
#             self.movements += 1
#             print("Policoa solicita asistencia del dron.")
#             self.model.drone.assist_police(self.model.cars + self.model.motorcycles)
#         else:
#             print("Policia no solicita asistencia del dron.")
    
    def request_drone_assistance(self, simulation):
        """Solicitar asistencia del dron"""
        if random.random() < 0.5:  # 50% success rate
            self.drone_requests += 1
            self.movements += 1
            return simulation.drone.assist_police(simulation.cars + simulation.motorcycles)
        return {"success": False, "reason": "Drone assistance request failed"}
        
    def to_dict(self):
        """Convertir policia a un diccionario con propiedades adicionales de policia"""
        base_dict = super().to_dict()
        base_dict.update({
            "tickets_issued_count": len(self.tickets_issued),
            "congestion_resolved": self.congestion_resolved,
            "drone_requests": self.drone_requests
        })
        return base_dict