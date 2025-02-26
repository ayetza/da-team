# Codigo realizado por Defense Against the Dark Nights
# Actividad. M3
# Febrero 2025

from owlready2 import *
import agentpy as ap
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 1. Definición de la Ontología ---

#  Ontologia desde un archivo externo
onto = get_ontology("file://traffic_ontology.owl")

with onto:
    # Definicion de las clases principales de la ontologia
    class Agente(Thing):
        pass

    class Orden(Thing):
        pass

    class Multa(Orden):
        pass

    class Avanzar(Orden):
        pass

    # Propiedades que relacionan agentes con ordenes y nivel de estres.
    class tiene_orden(ObjectProperty, FunctionalProperty):
        domain = [Agente]
        range = [Orden]

    class tiene_stress(DataProperty, FunctionalProperty):
        domain = [Agente]
        range = [int]

onto.save()

# --- 2. Definicion de los Agentes y Comunicacion ---

# Clase para gestionar la comunicacion entre agentes mediante un buffer compartido.
class Message:
    environment_buffer = []

    def __init__(self, sender, receiver, performative, content):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative
        self.content = content

    def send(self):
        Message.environment_buffer.append(self)

# Clase del agente policia que supervisa el trafico.
class TrafficPolice(ap.Agent):
    def setup(self):
        """Inicializa el agente policía con una representación en la ontología."""
        self.myself = onto.Agente()
        self.myself.tiene_stress = 0

    def send_order(self, order_type, car):
        """Envía una orden a un auto, ya sea avanzar o una multa."""
        if order_type == "Avanzar":
            order = onto.Avanzar()
        elif order_type == "Multa":
            order = onto.Multa()
        
        self.myself.tiene_orden = order
        
        msg = Message(
            sender=self.id,
            receiver=car.id,
            performative="orden",
            content={"tipo": order_type, "valor": 1}
        )
        msg.send()
        
        if order_type == "Multa":
            self.myself.tiene_stress += 1

    def check_speed(self, car):
        """Verifica la velocidad de un auto y emite una multa si excede el límite."""
        if car.speed > 2:
            self.send_order("Multa", car)

# Clase del agente auto que interactua con el entorno y el policia.
class Car(ap.Agent):
    def setup(self):
        self.myself = onto.Agente()
        self.myself.tiene_stress = 0
        self.speed = 2

    # Procesa los mensajes recibidos desde el entorno
    def process_messages(self):
        for msg in Message.environment_buffer:
            if msg.receiver == self.id and msg.performative == "orden":
                if msg.content["tipo"] == "Multa":
                    self.myself.tiene_stress += 2
                Message.environment_buffer.remove(msg)

    # Modifica la velocidad del auto de manera aleatoria
    def random_speed_change(self):
        if random.random() < 0.1:
            self.speed += 1
        elif random.random() < 0.1:
            self.speed = max(0, self.speed - 1)

# --- 3. Simulacion y Visualizacion ---

# Simulacion que gestiona la interaccion entre los agentes.
class TrafficModel(ap.Model):
    # Configura el entorno de la simulacion
    def setup(self):
        self.grid = ap.Grid(self, (10, 10))
        self.police = TrafficPolice(self)
        self.car = Car(self)
        self.grid.add_agents([self.police, self.car], random=True)
        
        self.fig, self.ax = plt.subplots()
        self.visualize_setup()

    # Ejecuta un paso de la simulacion donde los agentes interactuan
    def step(self):
        self.police.check_speed(self.car)
        self.car.process_messages()
        self.car.random_speed_change()
        self.update_ontology_stats()
        self.visualize()

    # Estado actual de los agentes en la simulacion
    def update_ontology_stats(self):
        print(f"Auto - Stress: {self.car.myself.tiene_stress}, Velocidad: {self.car.speed}")
        print(f"Policía - Orden: {self.police.myself.tiene_orden}, Stress: {self.police.myself.tiene_stress}")

    # Configuracion de la visualizacion de la simulacion
    def visualize_setup(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_xticks(range(11))
        self.ax.set_yticks(range(11))
        self.ax.grid(True)
        self.ax.set_title('Simulacion de Trafico Urbano')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')

    def visualize(self):
        self.ax.clear()
        self.visualize_setup()

        car_pos = self.grid.positions[self.car]
        police_pos = self.grid.positions[self.police]

        car_patch = patches.Circle((car_pos[0] + 0.5, car_pos[1] + 0.5), 0.3, color='blue', label='Auto')
        police_patch = patches.Circle((police_pos[0] + 0.5, police_pos[1] + 0.5), 0.3, color='red', label='Policia')
        
        self.ax.add_patch(car_patch)
        self.ax.add_patch(police_patch)
        
        self.ax.text(car_pos[0] + 0.5, car_pos[1] + 0.8, 
                     f"Stress: {self.car.myself.tiene_stress}\nVelocidad: {self.car.speed}", 
                     color='white', ha='center', va='center', fontsize=10, bbox=dict(facecolor='blue', alpha=0.5))
        self.ax.text(police_pos[0] + 0.5, police_pos[1] + 0.8, 
                     f"Stress: {self.police.myself.tiene_stress}\nOrden: {self.police.myself.tiene_orden}", 
                     color='white', ha='center', va='center', fontsize=10, bbox=dict(facecolor='red', alpha=0.5))

        plt.legend()
        plt.draw()
        plt.pause(0.1)

# --- Ejecución de la Simulacion ---
if __name__ == "__main__":
    model = TrafficModel()
    results = model.run(steps=10)
    plt.show()