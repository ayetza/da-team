import uuid
from core.simulation import TrafficSimulation

active_simulations = {}

def create_simulation(grid_size=10, num_cars=5, num_motorcycles=3):
    """Create a new traffic simulation with Q-Learning agents"""
    simulation_id = str(uuid.uuid4())
    simulation = TrafficSimulation(
        simulation_id=simulation_id,
        grid_size=grid_size,
        num_cars=num_cars,
        num_motorcycles=num_motorcycles
    )
    print(f"Simulación Q-Learning creada con ID: {simulation_id}")
    active_simulations[simulation_id] = simulation
    
    initial_state = simulation.get_state()
    
    return {
        "simulation_id": simulation_id,
        "message": "Simulacion iniciada",
        "initial_state": initial_state
    }

def get_simulation(simulation_id):
    """Get an existing simulation by ID"""
    simulation = active_simulations.get(simulation_id)
    if not simulation:
        return None
    return simulation

def delete_simulation(simulation_id):
    """Delete a simulation by ID"""
    if simulation_id in active_simulations:
        del active_simulations[simulation_id]
        print(f"Simulación eliminada con ID: {simulation_id}")
        return {"success": True, "message": f"Simulacion {simulation_id} eliminada exitosamente"}
    return {"success": False, "message": "Simulacion no encontrada"}