from .base import TrafficAgent

class Drone(TrafficAgent):


    def resolve_collisions_and_congestion(self, model):


        """
        El dron resuelve:
          - Colisiones (baja velocidad y marca collision=False)
          - Congestiones (baja velocidad en celdas con >= 3 vehiculos)
        """
        collisions = [v for v in (model.cars + model.motorcycles) if v.collision]
        if collisions:
            print("Dron interviniendo para resolver colisiones...")
            for vehicle in collisions:
                vehicle.speed = max(vehicle.speed - 1, 0)
                vehicle.collision = False
            print("Colisiones resueltas por el dron.")
            self.movements += 1

        congested_cells = model.detect_congestion()
        if congested_cells:
            print(f"Dron detecta congestiones en: {congested_cells}")
            for cell in congested_cells:
                vehicles_in_cell = [v for v in (model.cars + model.motorcycles) if v.position == cell]
                for v in vehicles_in_cell:
                    v.speed = max(v.speed - 1, 0)
            print("Dron resolvió las congestiones.")
            self.movements += 1

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "movements": self.movements
        })
        return base_dict
