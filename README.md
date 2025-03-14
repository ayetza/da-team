 # Sistemas Multiagentes y Gráficas Computacionales | Evidencia Final
 Fecha: 14 de marzo, 2025 

# Introducción
- Este proyecto implementa una simulación de tráfico con agentes inteligentes que utilizan Q-Learning para optimizar su comportamiento. Incluye:
- Vehículos autónomos (autos y motocicletas)
- Policía con aprendizaje Q-Learning
- Dron asistente para gestión de colisiones y congestiones

# Instalación
- Requisitos del Sistema
- Python 3.8 o superior
- Dependencias necesarias: random, matplotlib, owlready2, agentpy
- Archivo de ontología: traffic_ontology.owl (debe estar en el mismo directorio)

# Instalación de Dependencias
Ejecute el siguiente comando para instalar las librerías requeridas:
pip install matplotlib owlready2 agentpy

# Si usa un entorno virtual:
python -m venv venv
# En Linux/macOS
source venv/bin/activate  
# En Windows
venv\Scripts\activate   
pip install matplotlib owlready2 agentpy

# Configuración
Carga de la Ontología
El modelo utiliza traffic_ontology.owl para representar el tráfico y sus reglas. Se carga con:
onto = get_ontology("file://traffic_ontology.owl").load()

# Parámetros del Modelo

- Tamaño de la cuadrícula: 10x10
# Cantidad de agentes:
- 5 autos
- 3 motocicletas
- 1 policía
- 1 dron
# Velocidades máximas:
- Autos: 5
- Motocicletas: 7
# Parámetros de aprendizaje Q-Learning:
- alpha = 0.1
- gamma = 0.9
- epsilon = 0.1

# Ejecución de la Simulación
# (ESTO CORRESPONDE A UNITY)

# Durante la ejecución:
- Los vehículos aceleran, desaceleran y se mueven según su algoritmo de Q-Learning.
- El policía detecta congestiones y decide resolverlas o llamar al dron.
- Se emiten multas a vehículos que exceden los límites de velocidad.
- La simulación se detiene si hay tres fallos consecutivos en resolver congestiones.

# Visualización de Resultados
# Estado final de los agentes en la simulación:
# (ESTO CORRESPONDE A UNITY)

# Gráficos de análisis:
- Evolución de colisiones y congestiones a lo largo del tiempo.
- Acciones del Policía (resolver directamente vs. llamar al dron).

# Contribución
Si deseas contribuir a este proyecto:
- Realiza un fork del repositorio.
- Crea una nueva branch (feature/nueva-funcionalidad).
- Haz un commit de tus cambios (git commit -m 'Agrega nueva funcionalidad').
- Envía un pull request.

# Licencia
Este proyecto está bajo la licencia MIT. Puedes utilizarlo, modificarlo y compartirlo libremente, respetando los derechos de los autores.
Defense Against the Dark Arts 
- Gustavo García Téllez - A01644060
- Ayetza Y Infante Garcia - A01709011
- Fernanda Ríos Juárez- A01656047
- Álvaro Solano González - A01643948
- Sebastián Borjas Lizardi - A01748052
- Lesly Citlaly Gallegos Acosta - A01563036






