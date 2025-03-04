from .base import TrafficAgent

# class Drone(TrafficAgent):
#     def assist_police(self, vehicles):
#         collisions = [v for v in vehicles if v.collision]
        
#         if collisions:
#             print("Dron interviniendo para resolver colisiones...")
#             for vehicle in collisions:
#                 vehicle.speed = max(vehicle.speed - 1, 0)
#             for vehicle in collisions:
#                 vehicle.collision = False
            
#             self.movements += 2
#             print("Colisiones resueltas por el dron.")


class Drone(TrafficAgent):
    """Dron que ayuda a resolver colisiones entre vehiculos"""
    def assist_police(self, vehicles):
        """Ayudar a resolver colisiones entre vehiculos"""
        collisions = [v for v in vehicles if v.collision]
        resolved_collisions = []
        
        if collisions:
            for vehicle in collisions:
                original_speed = vehicle.speed
                vehicle.speed = max(vehicle.speed - 1, 0)
                resolved_collisions.append({
                    "id": vehicle.id,
                    "type": vehicle.__class__.__name__.lower(),
                    "position": vehicle.position,
                    "original_speed": original_speed,
                    "new_speed": vehicle.speed
                })
                
            for vehicle in collisions:
                vehicle.collision = False
            
            self.movements += 2
            return {"success": True, "collisions_resolved": resolved_collisions}
        return {"success": False, "reason": "No hay colisiones para resolver"}