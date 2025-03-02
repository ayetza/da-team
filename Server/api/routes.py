
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
            
            return {
                'message': "Simulation step processed",
                'movement_results': result,
                'updated_positions': {}
            }, 200
    


    # Endpoint para mover al policía
    @simulation_api.route('/<string:simulation_id>/police/move')
    @simulation_api.param('simulation_id', 'The simulation identifier')

    class PoliceMovement(Resource):

        @simulation_api.doc(body=models['police_movement_model'])
        @simulation_api.response(200, 'Success')
        @simulation_api.response(400, 'Entrada inválida', model=models['error_model'])
        @simulation_api.response(404, 'Simulación no encontrada', model=models['error_model'])
        
        def post(self, simulation_id):

            try:
                simulation = get_simulation(simulation_id)
                
                if not simulation:
                    return {
                        'success': False, 
                        'message': f"Simulación con ID {simulation_id} no encontrada"
                    }, 404
            
                data = request.json
                if not data or 'position' not in data:
                    return {
                        'success': False,
                        'message': "Se requiere una posición"
                    }, 400
                
                new_position = data['position']
                
                # Mover al policía a la nueva posición
                simulation.police.position = new_position
                simulation.police.movements += 1
                
                carros_en_exceso_de_velocidad = []
                
                for vehicle in simulation.cars + simulation.motorcycles:
                    x_diff = abs(vehicle.position[0] - new_position[0])
                    y_diff = abs(vehicle.position[1] - new_position[1])
                    
                    if x_diff <= 1 and y_diff <= 1 and vehicle.speed > vehicle.speed_limit:
                        carros_en_exceso_de_velocidad.append({
                            "id": vehicle.id,
                            "type": vehicle.__class__.__name__.lower(),
                            "position": vehicle.position,
                            "speed": vehicle.speed,
                            "speed_limit": vehicle.speed_limit
                        })
                
                congested_cells = simulation.detect_congestion()
                nearby_congestions = [
                    cell for cell in congested_cells if 
                    abs(cell[0] - new_position[0]) <= 1 and abs(cell[1] - new_position[1]) <= 1
                ]
                
                return {
                    "message": "Policía movida exitosamente",
                    "new_position": new_position,
                    "nearby_speeders": carros_en_exceso_de_velocidad,
                    "nearby_congestions": nearby_congestions
                }, 200
                
            except Exception as e:
                return {
                    'success': False,
                    'message': str(e)
                }, 400
    


    # Endpoint para emitir un ticket a un vehículo en exceso de velocidad
    @simulation_api.route('/<string:simulation_id>/police/issue-ticket')
    @simulation_api.param('simulation_id', 'The simulation identifier')

    class IssueTicket(Resource):
    
        @simulation_api.doc(body=models['issue_ticket_model'])
        @simulation_api.response(200, 'Success', model=models['issue_ticket_response'])
        @simulation_api.response(400, 'Entrada inválida', model=models['error_model'])
        @simulation_api.response(404, 'Simulación o vehículo no encontrado', model=models['error_model'])
    
        def post(self, simulation_id):

            try:
                simulation = get_simulation(simulation_id)
                
                if not simulation:
                    return {
                        'success': False,
                        'message': f"Simulación con ID {simulation_id} no encontrada"
                    }, 404
                
                data = request.json
                if not data or 'vehicle_id' not in data or 'vehicle_type' not in data:
                    return {
                        'success': False,
                        'message': "vehicle_id and vehicle_type are required"
                    }, 400
                
                vehicle_id = data['vehicle_id']
                vehicle_type = data['vehicle_type']

                vehicle = None
                if vehicle_type == "car":
                    for car in simulation.cars:
                        if car.id == vehicle_id:
                            vehicle = car
                            break
                else: 
                    for motorcycle in simulation.motorcycles:
                        if motorcycle.id == vehicle_id:
                            vehicle = motorcycle
                            break
                
                if not vehicle:
                    return {
                        'success': False,
                        'message': f"{vehicle_type.capitalize()} con ID {vehicle_id} no encontrado"
                    }, 404
                
                result = simulation.police.issue_ticket(vehicle, simulation)
                
                return {
                    'message': "Ticket emitido exitosamente" if result.get("success", False) else "Error al emitir el ticket",
                    'vehicle': {
                        "id": vehicle.id,
                        "type": vehicle_type,
                        "original_speed": result.get("original_speed", vehicle.speed),
                        "new_speed": result.get("new_speed", vehicle.speed)
                    },
                    'ticket_success': result.get("success", False),
                    'tickets_issued_count': len(simulation.police.tickets_issued)
                }, 200
                
            except Exception as e:
                return {
                    'success': False,
                    'message': str(e)
                }, 400
    


    # Endpoint para resolver congestión en una celda específica
    @simulation_api.route('/<string:simulation_id>/police/resolve-congestion')
    @simulation_api.param('simulation_id', 'The simulation identifier')

    class ResolveCongestion(Resource):
    
        @simulation_api.doc(body=models['resolve_congestion_model'])
        @simulation_api.response(200, 'Success', model=models['resolve_congestion_response'])
        @simulation_api.response(400, 'Entrada inválida', model=models['error_model'])
        @simulation_api.response(404, 'Simulación no encontrada', model=models['error_model'])
    
        def post(self, simulation_id):

            try:
                simulation = get_simulation(simulation_id)
                
                if not simulation:
                    return {
                        'success': False,
                        'message': f"Simulación con ID {simulation_id} no encontrada"
                    }, 404
                
                data = request.json
                if not data or 'cell' not in data:
                    return {
                        'success': False,
                        'message': "Se requiere una celda"
                    }, 400
                
                cell = data['cell']
                
                congested_cells = simulation.detect_congestion()
                if cell not in congested_cells:
                    return {
                        'success': False,
                        'message': f"Cell {cell} is not congested"
                    }, 400
                
                result = simulation.police.resolve_congestion(cell, simulation)
                
                return {
                    'message': "Intento de resolución de congestión",
                    'success': result.get("success", False),
                    'cell': cell,
                    'vehicles_affected': result.get("vehicles_affected", []),
                    'congestions_resolved_count': simulation.police.congestion_resolved
                }, 200
                
            except Exception as e:
                return {
                    'success': False,
                    'message': str(e)
                }, 400
    


    # Endpoint para solicitar ayuda de un dron
    @simulation_api.route('/<string:simulation_id>/police/request-drone')
    @simulation_api.param('simulation_id', 'The simulation identifier')

    class RequestDroneAssistance(Resource):
    
        @simulation_api.response(200, 'Success')
        @simulation_api.response(404, 'Simulación no encontrada', model=models['error_model'])
        
        def post(self, simulation_id):

            try:
                simulation = get_simulation(simulation_id)
                
                if not simulation:
                    return {'success': False, 'message': f"Simulación con ID {simulation_id} no encontrada"}, 404
                
                result = simulation.police.request_drone_assistance(simulation)
                
                drone_position = simulation.drone.position
                
                return {
                    "message": "Solicitud de ayuda de dron",
                    "success": result.get("success", False),
                    "drone_moved": True if result.get("success", False) else False,
                    "drone_new_position": drone_position,
                    "collisions_resolved": result.get("collisions_resolved", []),
                    "drone_requests_count": simulation.police.drone_requests
                }, 200
                
            except Exception as e:
                return {'success': False, 'message': str(e)}, 400
    


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