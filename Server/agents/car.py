from .vehicles import Vehicle
import random
from core.utils import distance

class Car(Vehicle):
    def __init__(self, car_id, model=None):
        super().__init__(car_id, model)
        self.speed_limit = 5
        
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1

        self.actions = ["accelerate", "maintain", "decelerate"]
        self.Q = {}

    def get_state(self):
        if not self.model:
            return (0, 0, 0)
            
        speed_level = min(self.speed // 2, 3)  
        near_police = 1 if distance(self.position, self.model.police.position) <= 2 else 0
        
        num_veh = 0
        if hasattr(self.model, 'cars') and hasattr(self.model, 'motorcycles'):
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