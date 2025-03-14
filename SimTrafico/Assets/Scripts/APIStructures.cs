using System.Collections.Generic;
using UnityEngine;

namespace APIStructures
{
    [System.Serializable]
    public class SimulationResponse
    {
        // Para el /create
        public string simulation_id;
        public string message;
        public InitialState initial_state;  // Solo existe en /create

        // Para el /state
        public Grid grid;     
        public int current_step;
        public Agents agents;  
        public List<float[]> congested_cells;
        public Status status;
    }

    [System.Serializable]
    public class Status
    {
        public bool task_completed;
        public int failed_congestions;
        public int total_movements;
        public string start_time;
    }

    [System.Serializable]
    public class InitialState
    {
        public string simulation_id;
        public Grid grid;
        public int current_step;
        public Agents agents;
    }

    [System.Serializable]
    public class Grid
    {
        public int size;
    }

    [System.Serializable]
    public class Agents
    {
        public List<Car> cars;
        public List<Motorcycle> motorcycles;
        public PoliceOfficerData police;
        public DroneData drone; // <--- NUEVO: Para manejar datos del dron
    }

    [System.Serializable]
    public class Car
    {
        public int id;
        public float[] position;
        public int speed;
        public bool ticketed;

        public Vector2 GetPosition()
        {
            return new Vector2(position[0], position[1]);
        }
    }

    [System.Serializable]
    public class Motorcycle
    {
        public int id;
        public float[] position;
        public int speed;

        public Vector2 GetPosition()
        {
            return new Vector2(position[0], position[1]);
        }
    }

    [System.Serializable]
    public class PoliceOfficerData
    {
        public float[] position;
        public int tickets_issued_count;
        public int congestion_resolved;
        public int drone_requests;

        public Vector2 GetPosition()
        {
            return new Vector2(position[0], position[1]);
        }
    }

    // NUEVO: Datos del dron
    [System.Serializable]
    public class DroneData
    {
        public float[] position;
        public int speed;
        public int movements;
        public int congestions_resolved;
        public int collisions_resolved;

        public Vector2 GetPosition()
        {
            return new Vector2(position[0], position[1]);
        }
    }

    [System.Serializable]
    public class StepResponse
    {
        public string message;
        public MovementResults movement_results;
        public UpdatedPositions updated_positions;
    }

    [System.Serializable]
    public class MovementResults
    {
        public int tickets_issued_count;
        public List<float[]> congested_cells;
    }

    [System.Serializable]
    public class UpdatedPositions
    {
        public List<CarUpdate> cars;
        public List<MotorcycleUpdate> motorcycles;
        public PoliceUpdate police;
        public DroneUpdate drone;
    }

    [System.Serializable]
    public class CarUpdate
    {
        public int id;
        public float[] position;
    }

    [System.Serializable]
    public class MotorcycleUpdate
    {
        public int id;
        public float[] position;
    }

    [System.Serializable]
    public class PoliceUpdate
    {
        public float[] position;
    }

    [System.Serializable]
    public class DroneUpdate
    {
        public float[] position;
    }
}
