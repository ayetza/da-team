from flask import request
from flask_restx import Resource, Namespace
from .manager import create_simulation, get_simulation, delete_simulation
from .models import create_api_models

def setup_routes(api):
    simulation_api = Namespace('simulation', description='Simulation operations')
    
    api.add_namespace(simulation_api, path='/api/simulation')
    
    models = create_api_models(simulation_api)



    # Endpoint para crear una nueva simulación
    @simulation_api.route('/create')

    class CreateSimulation(Resource):
        @simulation_api.expect(models['create_simulation_model'])
        @simulation_api.response(201, 'Simulation created successfully')
        @simulation_api.response(400, 'Invalid input', model=models['error_model'])
        def post(self):

            try:
                data = request.json or {}
                result = create_simulation(
                    grid_size=data.get('grid_size', 10),
                    num_cars=data.get('num_cars', 10),
                    num_motorcycles=data.get('num_motorcycles', 5)
                )
                return result, 201
            except Exception as e:
                return {'success': False, 'message': str(e)}, 400
            

    
    # Endpoint para obtener el estado actual de una simulación
    @simulation_api.route('/<string:simulation_id>/state')
    @simulation_api.param('simulation_id')

    class SimulationStateRoute(Resource):
        
        @simulation_api.response(200, 'Success', model=models['simulation_state_model'])
        @simulation_api.response(404, 'Simulación no encontrada', model=models['error_model'])
        
        def get(self, simulation_id):
            simulation = get_simulation(simulation_id)
            
            if not simulation:

                return models['error_model'](success=False, message=f"Simulación con ID {simulation_id} no encontrada").dict(), 404
                
            return simulation.get_state(), 200
    


    # Endpoint para avanzar la simulación por un paso
    @simulation_api.route('/<string:simulation_id>/step')
    @simulation_api.param('simulation_id', 'The simulation identifier')

    class SimulationStep(Resource):
        
        @simulation_api.response(200, 'Success', model=models['simulation_step_response'])
        @simulation_api.response(404, 'Simulación no encontrada', model=models['error_model'])
        
        def post(self, simulation_id):
            """Avanzar la simulación por un paso"""
            simulation = get_simulation(simulation_id)
            
            if not simulation:
                return {
                    'success': False, 
                    'message': f"Simulación con ID {simulation_id} no encontrada"
                }, 404
            result = simulation.step()
            
            updated_positions = {
                'cars': [{'id': car.id, 'position': car.position} for car in simulation.cars],
                'motorcycles': [{'id': motorcycle.id, 'position': motorcycle.position} for motorcycle in simulation.motorcycles],
                'police': {'position': simulation.police.position},
                'drone': {'position': simulation.drone.position}
            }
            
            return {
                'message': "Simulation step processed",
                'movement_results': result,
                'updated_positions': updated_positions
            }, 200
    
    # Endpoint para eliminar una simulación
    @simulation_api.route('/<string:simulation_id>')
    @simulation_api.param('simulation_id', 'The simulation identifier')
   
    class DeleteSimulation(Resource):
   
        @simulation_api.response(200, 'Success')
        @simulation_api.response(404, 'Simulation not found')
   
        def delete(self, simulation_id):
            result = delete_simulation(simulation_id)
            
            if not result.get("success", False):
                return {'success': False, 'message': result.get("message", "Error al eliminar la simulación")}, 404
                
            return result, 200

    return api