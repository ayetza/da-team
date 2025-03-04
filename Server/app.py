# Equipo: Defense Against the Dark Arts
# Sistemas Multiagentes y Graficas Computacionales
# 2 de marzo, 2025

from flask import Flask
from flask_restx import Api
from api.routes import setup_routes

def create_app():
    app = Flask(__name__)

    api = Api(
        app,
        version='1.0',
        title='Traffic Simulation API',
        description='A multi-agent traffic simulation API for game development',
        doc='/docs',
        validate=True
    )
    
    setup_routes(api)
    return app, api

if __name__ == '__main__':
    app, _ = create_app()
    app.run(debug=True)
    