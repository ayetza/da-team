from flask_restx import fields

def create_api_models(api):

    create_simulation_model = api.model('CreateSimulationRequest', {
        'grid_size': fields.Integer(required=False, default=10, min=0, max=20),
        'num_cars': fields.Integer(required=False, default=10, min=0, max=50),
        'num_motorcycles': fields.Integer(required=False, default=5, min=0, max=30)
    })

    error_model = api.model('ErrorResponse', {
        'success': fields.Boolean(default=False),
        'message': fields.String(required=True)
    })

    vehicle_model = api.model('Vehicle', {
        'id': fields.Integer(required=True),
        'position': fields.List(fields.Integer),
        'speed': fields.Integer,
        'speed_limit': fields.Integer,
        'ticketed': fields.Boolean,
        'collision': fields.Boolean
    })

    simulation_state_model = api.model('SimulationState', {
        'simulation_id': fields.String(required=True),
        'grid_size': fields.Integer(required=True),
        'current_step': fields.Integer(required=True),
        'cars': fields.List(fields.Nested(vehicle_model)),
        'motorcycles': fields.List(fields.Nested(vehicle_model)),
        'police': fields.Raw(),
        'drone': fields.Raw(),
        'congested_cells': fields.List(fields.List(fields.Integer))
    })

    movement_results_model = api.model('MovementResults', {
        'cars_moved': fields.Integer,
        'motorcycles_moved': fields.Integer,
        'collisions_detected': fields.Integer,
        'congested_cells': fields.List(fields.List(fields.Integer)),
        'game_over': fields.Boolean,
        'reason': fields.String,
        'task_completed': fields.Boolean
    })

    simulation_step_response = api.model('SimulationStepResponse', {
        'message': fields.String(default='Simulation step processed'),
        'movement_results': fields.Nested(movement_results_model),
        'updated_positions': fields.Raw()
    })

    return {
        'create_simulation_model': create_simulation_model,
        'error_model': error_model,
        'simulation_state_model': simulation_state_model,
        'simulation_step_response': simulation_step_response,
        'movement_results_model': movement_results_model
    }