# Equipo: Defense Against the Dark Arts
# Evidencia 1 | Sistemas Multiagentes y Graficas Computacionales
# 29 de febrero, 2025

from owlready2 import *
import agentpy as ap
import random
import matplotlib.pyplot as plt

# Cargar la ontología
onto = get_ontology("file://traffic_ontology.owl").load()

# Clase base para todos los agentes en la simulacion
class TrafficAgent(ap.Agent):
    def setup(self):
        self.speed = 0
        self.movements = 0
        self.position = (0, 0)

# Clase para el agente de policia
class Police(TrafficAgent):
    def setup(self):
        super().setup()
        self.tickets_issued = []
        self.congestion_resolved = 0
        self.drone_requests = 0
        self.failed_congestions = 0

# Funcion para emitir multas a vehiculos que excedan el limite de velocidad
    def issue_ticket(self, vehicle):
        if vehicle.speed > vehicle.speed_limit and not vehicle.ticketed:
            original_speed = vehicle.speed
            vehicle.ticketed = True
            if random.random() < 0.7:
                vehicle.speed = max(vehicle.speed - 2, 2)
            self.tickets_issued.append((vehicle, original_speed, vehicle.speed))
            self.movements += 1
            print(f"Multa emitida a {type(vehicle).__name__} en {vehicle.position}: {original_speed} -> {vehicle.speed}")

# Función para resolver congestiones en una celda especifica
    def resolve_congestion(self, cell):
        vehicles_in_cell = [v for v in self.model.cars + self.model.motorcycles if v.position == cell]
        if random.random() < 0.7:  
            for vehicle in vehicles_in_cell:
                vehicle.speed = max(vehicle.speed - 1, 2)
            self.congestion_resolved += 1
            self.movements += 1
            print(f"Congestion en {cell} resuelta.")
            return True
        else:
            print(f"Fallo al resolver congestion en {cell}.")
            return False

    # Funcion para solicitar asistencia del dron
    def request_drone_assistance(self):
        if random.random() < 0.5:
            self.drone_requests += 1
            self.movements += 1
            print("Policoa solicita asistencia del dron.")
            self.model.drone.assist_police(self.model.cars + self.model.motorcycles)
        else:
            print("Policia no solicita asistencia del dron.")

# Clase del dron, que ayuda en la resolucion de colisiones
class Drone(TrafficAgent):
    def assist_police(self, vehicles):
        collisions = [v for v in vehicles if v.collision]
        
        if collisions:
            print("Dron interviniendo para resolver colisiones...")
            for vehicle in collisions:
                vehicle.speed = max(vehicle.speed - 1, 0)
            for vehicle in collisions:
                vehicle.collision = False
            
            self.movements += 2
            print("Colisiones resueltas por el dron.")

# Clase base para vehiculos
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

# Movimiento del vehiculo en la cuadricula
    def move(self):
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x = max(0, min(self.position[0] + dx, self.model.grid_size - 1))
        new_y = max(0, min(self.position[1] + dy, self.model.grid_size - 1))
        self.position = (new_x, new_y)
        self.check_collision()
        self.movements += 1
        
    # Detección de colisiones
    def check_collision(self):
        all_vehicles = self.model.cars + self.model.motorcycles
        for vehicle in all_vehicles:
            if vehicle != self and vehicle.position == self.position:
                self.collision = True
                vehicle.collision = True

# Clases especificas para autos y motocicletas
class Car(Vehicle):
    def setup(self):
        super().setup()
        self.speed_limit = 5

    def obey_instructions(self):
        if random.random() < 0.8:
            self.speed = min(self.speed, self.speed_limit)
        else:
            self.accelerate()

class Motorcycle(Vehicle):
    def setup(self):
        super().setup()
        self.speed_limit = 7

    def obey_instructions(self):
        if random.random() < 0.6:
            self.speed = min(self.speed, self.speed_limit)
        else:
            self.accelerate()

# Modelo de trafico basado en agentes
class TrafficModel(ap.Model):
    def setup(self):
        self.grid_size = 10

        self.police = Police(self)
        self.drone = Drone(self)
        self.cars = ap.AgentList(self, 10, Car)
        self.motorcycles = ap.AgentList(self, 5, Motorcycle)

        self.agents = [self.police, self.drone] + list(self.cars) + list(self.motorcycles)

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

    # Deteccion de congestion en celdas con 3 o más vehiculos
    def detect_congestion(self):
        position_counts = {}
        for vehicle in self.cars + self.motorcycles:
            pos = vehicle.position
            position_counts[pos] = position_counts.get(pos, 0) + 1
        return [pos for pos, count in position_counts.items() if count >= 3]

    def step(self):
        all_vehicles = self.cars + self.motorcycles
        
        for vehicle in all_vehicles:
            vehicle.accelerate()
            vehicle.move()
            vehicle.obey_instructions()
            
            if vehicle.speed > vehicle.speed_limit:
                self.police.issue_ticket(vehicle)

        self.police.request_drone_assistance()
        
        # Deteccion y manejo de congestiones
        congested_cells = self.detect_congestion()
        if congested_cells:
            print(f"¡Congestiones detectadas en celdas: {congested_cells}!")
            all_resolved = True
            for cell in congested_cells:
                if not self.police.resolve_congestion(cell):
                    all_resolved = False
            
            if all_resolved:
                self.police.failed_congestions = 0
                print("Todas las congestiones resueltas.")
            else:
                self.police.failed_congestions += 1
                print(f"Fallos consecutivos en resolver congestiones: {self.police.failed_congestions}")
                
            if self.police.failed_congestions >= 3:
                print("Simulación terminada: Tres fallos consecutivos en resolver congestiones.")
                self.stop()
        else:
            self.police.failed_congestions = 0
        
        # Verificar finalizacion de tarea
        if not any(v.collision for v in all_vehicles) and \
           not any(v.speed > v.speed_limit for v in all_vehicles):
            if not self.task_completed:
                self.task_completed = True
                self.task_completion_time = self.t

    def end(self):
        total_movements = sum(agent.movements for agent in self.agents)
        print("\n--- Resultados Finales ---")
        print(f"Tiempo de completado: {self.task_completion_time if self.task_completion_time else 'No completado'}")
        print(f"Movimientos totales: {total_movements}")
        print(f"Movimientos del policia: {self.police.movements}")
        print(f"Cantidad de multas emitidas: {len(self.police.tickets_issued)}")
        print("Vehículos multados:")
        for vehicle, speed, new_speed in self.police.tickets_issued:
            print(f"  - {type(vehicle).__name__} en {vehicle.position}: {speed} -> {new_speed}")
        print(f"Congestiones resueltas: {self.police.congestion_resolved}")
        print(f"Solicitudes de dron: {self.police.drone_requests}")

# Ejecutar la simulacion
model = TrafficModel()
results = model.run(steps=100)

# Visualizacion
plt.figure(figsize=(8, 8))
ax = plt.gca()
ax.set_xlim(-1, model.grid_size)
ax.set_ylim(-1, model.grid_size)
ax.set_xticks(range(model.grid_size))
ax.set_yticks(range(model.grid_size))
ax.grid(True)

for vehicle in model.cars:
    plt.plot(vehicle.position[0], vehicle.position[1], 'ro', markersize=8, label='Car' if 'Car' not in plt.gca().get_legend_handles_labels()[1] else "")
for bike in model.motorcycles:
    plt.plot(bike.position[0], bike.position[1], 'bo', markersize=8, label='Motorcycle' if 'Motorcycle' not in plt.gca().get_legend_handles_labels()[1] else "")
plt.plot(model.police.position[0], model.police.position[1], 'gs', markersize=12, label='Police')
plt.plot(model.drone.position[0], model.drone.position[1], 'y^', markersize=12, label='Drone')

plt.title('Estado Final de la Simulacion de Trafico')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.legend()
plt.show()