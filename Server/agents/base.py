class TrafficAgent:
    """Clase base para todos los agentes en la simulacion"""
    def __init__(self):
        self.speed = 0
        self.movements = 0
        self.position = (0, 0)
        
    def to_dict(self):
        """Convertir agente a un diccionario para respuestas de API"""
        return {
            "position": self.position,
            "speed": self.speed,
            "movements": self.movements
        }