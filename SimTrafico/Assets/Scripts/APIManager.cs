using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;

public class APIManager : MonoBehaviour
{
    public string simulationId = "f9814394-8d70-49ba-8838-4c831da24659"; // Se debe actualizar dinámicamente si cambia
    public string baseApiUrl = "http://localhost:5000/api/simulation/";
    public float stepInterval = 10f; // Tiempo entre cada step

    private Dictionary<int, CarMovement> cars = new Dictionary<int, CarMovement>();

    public GameObject carPrefab;

    private void Start()
    {
        StartCoroutine(CreateSimulation());
    }

    IEnumerator CreateSimulation()
    {
        string apiUrl = baseApiUrl + "create";

        var requestData = new
        {
            grid_size = 5,
            num_cars = 10
        };
        string jsonData = JsonConvert.SerializeObject(requestData);

        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Accept", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                SimulationResponse response = JsonConvert.DeserializeObject<SimulationResponse>(request.downloadHandler.text);
                simulationId = response.simulation_id; // Guardamos el ID de la simulación
                Debug.Log("Simulación creada: " + simulationId);
                InstantiateCars(response);
                StartCoroutine(StepSimulation()); // Comienza el ciclo de steps
            }
            else
            {
                Debug.LogError("Error en la solicitud: " + request.error);
            }
        }
    }

void InstantiateCars(SimulationResponse response)
{
    if (response.initial_state != null)
    {
        foreach (var car in response.initial_state.agents.cars)
        {
            Vector2 carPos = car.GetPosition();
            GameObject carObject = Instantiate(carPrefab, new Vector3(carPos.x * 10, 0, carPos.y * 10), Quaternion.identity);
            CarMovement carMovement = carObject.GetComponent<CarMovement>();
            carMovement.carId = car.id;
            carMovement.moveSpeed = car.speed; // Asignar velocidad basada en la API
            cars[car.id] = carMovement;
        }
    }
}
    IEnumerator StepSimulation()
    {
        while (true)
        {
            yield return new WaitForSeconds(stepInterval);

            string apiUrl = $"{baseApiUrl}{simulationId}/step";

            using (UnityWebRequest request = new UnityWebRequest(apiUrl, "POST"))
            {
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Accept", "application/json");

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    StepResponse response = JsonConvert.DeserializeObject<StepResponse>(request.downloadHandler.text);
                    UpdateCarPositions(response);
                }
                else
                {
                    Debug.LogError("Error en el Step: " + request.error);
                }
            }
        }
    }

    void UpdateCarPositions(StepResponse response)
    {
        if (response.movement_results.updated_positions.cars != null)
        {
            foreach (var carEntry in response.movement_results.updated_positions.cars)
            {
                int carId = int.Parse(carEntry.Key);
                Vector2 newPos = new Vector2(carEntry.Value[0], carEntry.Value[1]);

                if (cars.ContainsKey(carId))
                {
                    cars[carId].MoveTo(newPos);
                }
            }
        }
    }
}

// Clases de la respuesta inicial
[System.Serializable]
public class SimulationResponse
{
    public string simulation_id;
    public string message;
    public InitialState initial_state;
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
}

[System.Serializable]
public class Car
{
    public int id;
    public float[] position;
    public int speed;

    public Vector2 GetPosition()
    {
        return new Vector2(position[0], position[1]);
    }
}

// Clases de la respuesta del Step
[System.Serializable]
public class StepResponse
{
    public string message;
    public MovementResults movement_results;
}

[System.Serializable]
public class MovementResults
{
    public UpdatedPositions updated_positions; // Agregamos esta estructura
}

[System.Serializable]
public class UpdatedPositions
{
    public Dictionary<string, float[]> cars; // Mapeamos las posiciones de los carros
}
