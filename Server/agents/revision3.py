# Equipo: Defense Against the Dark Arts
# Revision 3 | Sistemas Multiagentes y Graficas Computacionales
# 9 de marzo, 2025

import random
import matplotlib.pyplot as plt
from owlready2 import *
import agentpy as ap


# 1. Ontología 
onto = get_ontology("file://traffic_ontology.owl").load()


# 2. Funciones auxiliares
def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


# 3. Clase base TrafficAgent 
class TrafficAgent(ap.Agent):
    def setup(self):
        self.speed = 0
        self.movements = 0
        self.position = (0, 0)

# 4. Clase Drone 
class Drone(TrafficAgent):
    def resolve_collisions_and_congestion(self, model):
        """
        El dron resuelve:
          - Colisiones (baja velocidad y marca collision=False)
          - Congestiones (baja velocidad en celdas con >= 3 vehiculos)
        """
        # Resolver colisiones
        collisions = [v for v in (model.cars + model.motorcycles) if v.collision]
        if collisions:
            print("Dron interviniendo para resolver colisiones...")
            for vehicle in collisions:
                vehicle.speed = max(vehicle.speed - 1, 0)
                vehicle.collision = False
            print("Colisiones resueltas por el dron.")
            self.movements += 1

        # Resolver congestiones
        congested_cells = model.detect_congestion()
        if congested_cells:
            print(f"Dron detecta congestiones en: {congested_cells}")
            for cell in congested_cells:
                # Disminuye velocidad a los vehiculos en esa celda
                vehicles_in_cell = [v for v in (model.cars + model.motorcycles) if v.position == cell]
                for v in vehicles_in_cell:
                    v.speed = max(v.speed - 1, 0)
            print("Dron resolvió las congestiones.")
            self.movements += 1


# 5. Clase base Vehicle
class Vehicle(TrafficAgent):
    def setup(self):
        super().setup()
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
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x = max(0, min(self.position[0] + dx, self.model.grid_size - 1))
        new_y = max(0, min(self.position[1] + dy, self.model.grid_size - 1))
        self.position = (new_x, new_y)
        self.check_collision()
        self.movements += 1

    def check_collision(self):
        all_vehicles = self.model.cars + self.model.motorcycles
        for vehicle in all_vehicles:
            if vehicle != self and vehicle.position == self.position:
                self.collision = True
                vehicle.collision = True


# 6. Q-Learning Vehicles (Car y Motorcycle) 
class QLearningCar(Vehicle):
    def setup(self):
        super().setup()
        self.speed_limit = 5
        
        # Parámetros de Q-Learning
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

        self.actions = ["accelerate", "maintain", "decelerate"]
        self.Q = {}

    def get_state(self):
        speed_level = min(self.speed // 2, 3)  
        near_police = 1 if distance(self.position, self.model.police.position) <= 2 else 0
        num_veh = sum(1 for v in (self.model.cars + self.model.motorcycles) if v.position == self.position)
        congested = 1 if num_veh >= 3 else 0
        return (speed_level, near_police, congested)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.Q.get(state, {})
            if not q_values:
                return random.choice(self.actions)
            return max(q_values, key=q_values.get)

    def compute_reward(self):
        reward = 0
        if self.collision:
            reward -= 10
        if (self.speed > self.speed_limit) and self.ticketed:
            reward -= 5
        if not self.collision and not self.ticketed:
            reward += 1
        return reward

    def update_Q(self, state, action, reward, next_state):
        current_q = self.Q.setdefault(state, {}).get(action, 0.0)
        next_q_values = self.Q.setdefault(next_state, {})
        max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.Q[state][action] = new_q

    def obey_instructions(self):
        state = self.get_state()
        action = self.choose_action(state)
        if action == "accelerate":
            self.accelerate()
        elif action == "maintain":
            pass
        elif action == "decelerate":
            self.decelerate()

        reward = self.compute_reward()
        next_state = self.get_state()
        self.update_Q(state, action, reward, next_state)


class QLearningMotorcycle(Vehicle):
    def setup(self):
        super().setup()
        self.speed_limit = 7
        
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

        self.actions = ["accelerate", "maintain", "decelerate"]
        self.Q = {}

    def get_state(self):
        speed_level = min(self.speed // 2, 3)
        near_police = 1 if distance(self.position, self.model.police.position) <= 2 else 0
        num_veh = sum(1 for v in (self.model.cars + self.model.motorcycles) if v.position == self.position)
        congested = 1 if num_veh >= 3 else 0
        return (speed_level, near_police, congested)

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.Q.get(state, {})
            if not q_values:
                return random.choice(self.actions)
            return max(q_values, key=q_values.get)

    def compute_reward(self):
        reward = 0
        if self.collision:
            reward -= 10
        if (self.speed > self.speed_limit) and self.ticketed:
            reward -= 5
        if not self.collision and not self.ticketed:
            reward += 1
        return reward

    def update_Q(self, state, action, reward, next_state):
        current_q = self.Q.setdefault(state, {}).get(action, 0.0)
        next_q_values = self.Q.setdefault(next_state, {})
        max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.Q[state][action] = new_q

    def obey_instructions(self):
        state = self.get_state()
        action = self.choose_action(state)
        if action == "accelerate":
            self.accelerate()
        elif action == "maintain":
            pass
        elif action == "decelerate":
            self.decelerate()

        reward = self.compute_reward()
        next_state = self.get_state()
        self.update_Q(state, action, reward, next_state)

# 7. Q-Learning Police 
class QLearningPolice(TrafficAgent):
    """
    El policía puede:
     - Resolver colisiones y congestiones él mismo 
     - Llamar al dron para que resuelva ambos problemas 
     - Emitir multas 
    """
    def setup(self):
        super().setup()
        self.tickets_issued = []
        self.congestion_resolved = 0
        self.drone_requests = 0
        self.failed_congestions = 0

        # Parámetros de Q-Learning
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2

        # Acciones
        self.actions = ["resolve_myself", "call_drone"]
        self.Q = {}

    # Tipo de estado
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

    # Recompensa del policía
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

    # Métodos para acciones del policía
    def resolve_collisions_and_congestion_myself(self):
        """
        El policía resuelve ambos problemas directamente:
          - Elimina colisiones bajando velocidad
          - Disminuye velocidad en celdas congestionadas
        """
        # Resolver colisiones
        collisions = [v for v in (self.model.cars + self.model.motorcycles) if v.collision]
        if collisions:
            print("Policía resolviendo colisiones él mismo...")
            for vehicle in collisions:
                vehicle.speed = max(vehicle.speed - 1, 0)
                vehicle.collision = False
            print("Colisiones resueltas por Policía.")
            self.movements += 1

        # Resolver congestiones
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
            # Reduce la velocidad si es multado
            if random.random() < 0.7:
                vehicle.speed = max(vehicle.speed - 2, 2)
            self.tickets_issued.append((vehicle, original_speed, vehicle.speed))
            self.movements += 1
            print(f"Multa emitida a {type(vehicle).__name__} en {vehicle.position}: {original_speed} -> {vehicle.speed}")

    # Paso Q-Learning del policía
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
        
        # Nuevo estado
        next_state = self.get_state()
        
        self.update_Q(state, action, reward, next_state)

# 8. Modelo principal
class TrafficModel(ap.Model):
    def setup(self):
        self.grid_size = 10

        # Se usa QLearningPolice y Drone
        self.police = QLearningPolice(self)
        self.drone = Drone(self)

        # Se crean listas de agentes con nuestras clases Q-Learning
        self.cars = ap.AgentList(self, 5, QLearningCar)
        self.motorcycles = ap.AgentList(self, 3, QLearningMotorcycle)
        self.agents = [self.police, self.drone] + list(self.cars) + list(self.motorcycles)

        # Se asignan posiciones aleatorias no repetidas
        occupied_positions = []
        for agent in self.agents:
            agent.position = self.random_empty_position(occupied_positions)
            occupied_positions.append(agent.position)

        self.task_completed = False
        self.task_completion_time = None

    def random_empty_position(self, occupied):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if (x, y) not in occupied:
                return (x, y)

    def detect_congestion(self):
        """Celdas con 3 o más vehículos se consideran congestionadas."""
        position_counts = {}
        for vehicle in self.cars + self.motorcycles:
            pos = vehicle.position
            position_counts[pos] = position_counts.get(pos, 0) + 1
        return [pos for pos, count in position_counts.items() if count >= 3]

    def step(self):
        # Vehículos actúan
        for vehicle in (self.cars + self.motorcycles):
            vehicle.accelerate()
            vehicle.move()
            vehicle.obey_instructions()

        # El policía hace su lógica Q-Learning:
        self.police.step()

        # Se emiten multas  
        for vehicle in (self.cars + self.motorcycles):
            if vehicle.speed > vehicle.speed_limit:
                self.police.issue_ticket(vehicle)

        # Se verifica si hay congestiones que el policía no resolvió
        congested_cells = self.detect_congestion()
        if congested_cells:
            print(f"¡Aún quedan congestiones en celdas: {congested_cells}!")
            self.police.failed_congestions += 1
            print(f"Fallos consecutivos: {self.police.failed_congestions}")
            if self.police.failed_congestions >= 3:
                print("Simulación terminada: Tres fallos consecutivos en resolver congestiones.")
                self.stop()
        else:
            self.police.failed_congestions = 0

        # Se comprueban colisiones y excesos de velocidad para ver si se completa la tarea 
        any_collision = any(v.collision for v in (self.cars + self.motorcycles))
        any_overspeed = any((v.speed > v.speed_limit) for v in (self.cars + self.motorcycles))

        if not any_collision and not any_overspeed:
            if not self.task_completed:
                self.task_completed = True
                self.task_completion_time = self.t

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

# 9. Ejecutar la simulación
model = TrafficModel()
results = model.run(steps=100)

# 10. Visualización de resultados
plt.figure(figsize=(8, 8))
ax = plt.gca()
ax.set_xlim(-1, model.grid_size)
ax.set_ylim(-1, model.grid_size)
ax.set_xticks(range(model.grid_size))
ax.set_yticks(range(model.grid_size))
ax.grid(True)

seen_labels = set()

def plot_agent(agent, marker, label):
    if label not in seen_labels:
        plt.plot(agent.position[0], agent.position[1], marker, markersize=8, label=label)
        seen_labels.add(label)
    else:
        plt.plot(agent.position[0], agent.position[1], marker, markersize=8)

for c in model.cars:
    plot_agent(c, 'ro', 'Car (QLearning)')
for m in model.motorcycles:
    plot_agent(m, 'bo', 'Motorcycle (QLearning)')
plot_agent(model.police, 'gs', 'Police (QLearning)')
plot_agent(model.drone, 'y^', 'Drone')

plt.title('Tráfico con Policía Q-Learning (Colisiones & Congestiones)')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.legend()
plt.show()
