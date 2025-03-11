import random
from .base import TrafficAgent

class Police(TrafficAgent):
    def __init__(self, model=None):
        super().__init__(model)
        self.tickets_issued = []
        self.congestion_resolved = 0
        self.drone_requests = 0
        self.failed_congestions = 0

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

        self.actions = ["resolve_myself", "call_drone"]
        self.Q = {}

    def get_state(self):
        # Contar colisiones activas
        collisions_count = sum(1 for v in (self.model.cars + self.model.motorcycles) if v.collision)
        # Contar celdas congestionadas
        congested_cells = self.model.detect_congestion()
        congestion_count = len(congested_cells)

        # Limitar el conteo a un tope
        if collisions_count > 5:
            collisions_count = 5
        if congestion_count > 5:
            congestion_count = 5

        return (collisions_count, congestion_count)
    
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.Q.get(state, {})
            if not q_values:
                return random.choice(self.actions)
            return max(q_values, key=q_values.get)
        
    def compute_reward(self, collisions_before, congestions_before, action):
        """
        Se define según:
         - Cuántos choques y congestiones había.
         - Si llamó al dron (podemos penalizar o no su uso).
        """
        reward = 0
        # Penaliza la existencia de colisiones y congestiones
        reward -= 2 * collisions_before
        reward -= 3 * congestions_before

        # Costo por llamar al dron 
        if action == "call_drone":
            reward -= 2
        return reward
    
    def update_Q(self, state, action, reward, next_state):
        current_q = self.Q.setdefault(state, {}).get(action, 0.0)
        next_q_values = self.Q.setdefault(next_state, {})
        max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.Q[state][action] = new_q

    def resolve_collisions_and_congestion_myself(self):
        """
        El policía resuelve ambos problemas directamente:
          - Elimina colisiones bajando velocidad
          - Disminuye velocidad en celdas congestionadas
        """
        collisions = [v for v in (self.model.cars + self.model.motorcycles) if v.collision]
        if collisions:
            print("Policía resolviendo colisiones él mismo...")
            for vehicle in collisions:
                vehicle.speed = max(vehicle.speed - 1, 0)
                vehicle.collision = False
            print("Colisiones resueltas por Policía.")
            self.movements += 1

        congested_cells = self.model.detect_congestion()
        if congested_cells:
            print(f"Policía detecta congestiones en: {congested_cells}")
            for cell in congested_cells:
                vehicles_in_cell = [v for v in (self.model.cars + self.model.motorcycles) if v.position == cell]
                for v in vehicles_in_cell:
                    v.speed = max(v.speed - 1, 0)
            self.congestion_resolved += len(congested_cells)
            print("Policía resolvió congestiones.")
            self.movements += 1

    def call_drone(self):
        """
        Llama al dron para que resuelva colisiones y congestiones.
        """
        self.drone_requests += 1
        self.movements += 1
        print("Policía solicita asistencia del dron.")
        self.model.drone.resolve_collisions_and_congestion(self.model)

    def issue_ticket(self, vehicle):
        """
        Emite multas a vehículos con exceso de velocidad.
        """
        if vehicle.speed > vehicle.speed_limit and not vehicle.ticketed:
            original_speed = vehicle.speed
            vehicle.ticketed = True
            if random.random() < 0.7:
                vehicle.speed = max(vehicle.speed - 2, 2)
            self.tickets_issued.append((vehicle, original_speed, vehicle.speed))
            self.movements += 1
            print(f"Multa emitida a {type(vehicle).__name__} en {vehicle.position}: {original_speed} -> {vehicle.speed}")

    def step(self):
        """
        1) El policía observa el estado (colisiones, congestiones).
        2) Elige acción (resolve_myself o call_drone).
        3) Ejecuta la acción.
        4) Emite multas (opcional hacerlo antes o después).
        5) Calcula reward y actualiza Q.
        """
        state = self.get_state()
        action = self.choose_action(state)

        collisions_before, congestions_before = state

        if action == "resolve_myself":
            self.resolve_collisions_and_congestion_myself()
        else:
            self.call_drone()
            
        reward = self.compute_reward(collisions_before, congestions_before, action)
        
        next_state = self.get_state()
        
        self.update_Q(state, action, reward, next_state)
        
    def to_dict(self):
        """Convertir policia a un diccionario con propiedades adicionales de policia"""
        base_dict = super().to_dict()
        base_dict.update({
            "tickets_issued_count": len(self.tickets_issued),
            "congestion_resolved": self.congestion_resolved,
            "drone_requests": self.drone_requests,
            "failed_congestions": self.failed_congestions
        })
        return base_dict