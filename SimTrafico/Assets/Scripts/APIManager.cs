using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json;
using APIStructures;

public class APIManager : MonoBehaviour
{
    public string simulationId;
    public string baseApiUrl = "http://127.0.0.1:5000/api/simulation/";
    public float stepInterval = 10f;

    [Header("Grid Settings")]
    public float cellSize = 10f;

    [Header("Movement Settings")]
    public float speedMultiplier = 2f;

    [Header("Motorcycle Settings")]
    public float motorcycleHeightOffset = 1f;  

    // NUEVO: Para manejar el dron
    [Header("Drone Settings")]
    public GameObject dronePrefab;
    private DroneBehavior droneBehavior; 
    private int previousDroneCongestions = 0;
    private int previousDroneCollisions = 0;

    private Dictionary<int, CarMovement> cars = new Dictionary<int, CarMovement>();
    private Dictionary<int, MotorcycleMovement> motorcycles = new Dictionary<int, MotorcycleMovement>();
    private PoliceOfficer policeOfficer;

    public GameObject carPrefab;
    public GameObject motorcyclePrefab;
    public GameObject policePrefab;
    public int gridSize = 10;
    public int numCars = 10;
    public int numMotorcycles = 5;

    // Variables para la Policía
    private int previousTicketsIssued = 0;
    private int previousCongestionsResolved = 0;
    private int previousDroneRequests = 0;

    private int currentTicketsIssued = 0;
    private int currentCongestionsResolved = 0;
    private int currentDroneRequests = 0;

    private void Start()
    {
        // Inicia la creación de la simulación al arrancar
        StartCoroutine(CreateSimulation());
    }

    /// <summary>
    /// 1) Crea la simulación con un POST /create
    /// </summary>
    IEnumerator CreateSimulation()
    {
        string apiUrl = baseApiUrl + "create";

        var requestData = new
        {
            grid_size = gridSize,
            num_cars = numCars,
            num_motorcycles = numMotorcycles
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
                SimulationResponse response =
                    JsonConvert.DeserializeObject<SimulationResponse>(request.downloadHandler.text);

                simulationId = response.simulation_id;
                Debug.Log("Simulación creada: " + simulationId);

                InstantiateEntities(response);
                StartCoroutine(StepSimulation());
            }
            else
            {
                Debug.LogError("Error en la solicitud /create: " + request.error);
            }
        }
    }

    /// <summary>
    /// 2) Instancia los coches, motos, policía y dron que vinieron en el estado inicial
    /// </summary>
    void InstantiateEntities(SimulationResponse response)
    {
        if (response.initial_state != null &&
            response.initial_state.agents != null)
        {
            // COCHES
            if (response.initial_state.agents.cars != null)
            {
                foreach (var car in response.initial_state.agents.cars)
                {
                    Vector2 carPos = car.GetPosition();
                    GameObject carObject = Instantiate(
                        carPrefab,
                        new Vector3(carPos.x * cellSize, 2f, carPos.y * cellSize),
                        Quaternion.identity
                    );

                    CarMovement carMovement = carObject.GetComponent<CarMovement>();
                    carMovement.carId = car.id;
                    carMovement.SetSpeed(car.speed * speedMultiplier);
                    carMovement.SetTicketed(car.ticketed);
                    cars[car.id] = carMovement;
                }
            }

            // MOTOS
            if (response.initial_state.agents.motorcycles != null)
            {
                foreach (var moto in response.initial_state.agents.motorcycles)
                {
                    Vector2 motoPos = moto.GetPosition();
                    GameObject motoObject = Instantiate(
                        motorcyclePrefab,
                        new Vector3(motoPos.x * cellSize, 2f + motorcycleHeightOffset, motoPos.y * cellSize),
                        Quaternion.identity
                    );

                    MotorcycleMovement motoMovement = motoObject.GetComponent<MotorcycleMovement>();
                    motoMovement.motoId = moto.id;
                    motoMovement.SetSpeed(moto.speed * speedMultiplier);
                    motorcycles[moto.id] = motoMovement;
                }
            }

            // POLICÍA
            if (response.initial_state.agents.police != null)
            {
                Vector2 policePos = response.initial_state.agents.police.GetPosition();
                GameObject policeObject = Instantiate(
                    policePrefab,
                    new Vector3(policePos.x * cellSize, 2f, policePos.y * cellSize),
                    Quaternion.identity
                );

                policeOfficer = policeObject.GetComponent<PoliceOfficer>();
                policeOfficer.SetInitialPosition(policePos);

                previousTicketsIssued = response.initial_state.agents.police.tickets_issued_count;
                previousCongestionsResolved = response.initial_state.agents.police.congestion_resolved;
                previousDroneRequests = response.initial_state.agents.police.drone_requests;

                currentTicketsIssued = previousTicketsIssued;
                currentCongestionsResolved = previousCongestionsResolved;
                currentDroneRequests = previousDroneRequests;
            }

            // DRON
            if (response.initial_state.agents.drone != null && dronePrefab != null)
            {
                Vector2 dronePos = response.initial_state.agents.drone.GetPosition();
                GameObject droneObject = Instantiate(
                    dronePrefab,
                    new Vector3(dronePos.x * cellSize, 2f, dronePos.y * cellSize), // Ajusta la altura si quieres
                    Quaternion.identity
                );

                droneBehavior = droneObject.GetComponent<DroneBehavior>();
                // Guardar valores previos de congestiones y colisiones
                previousDroneCongestions = response.initial_state.agents.drone.congestions_resolved;
                previousDroneCollisions = response.initial_state.agents.drone.collisions_resolved;
            }
        }
    }

    /// <summary>
    /// 3) Llama al endpoint /step en un ciclo infinito
    /// </summary>
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
                    StepResponse response =
                        JsonConvert.DeserializeObject<StepResponse>(request.downloadHandler.text);

                    UpdateEntities(response);
                    StartCoroutine(UpdateStateAndHandlePoliceActions());
                }
                else
                {
                    Debug.LogError("Error en el /step: " + request.error);
                }
            }
        }
    }

    /// <summary>
    /// 4) Llama a /state y maneja acciones de la policía y el dron
    /// </summary>
    IEnumerator UpdateStateAndHandlePoliceActions()
    {
        string apiUrl = $"{baseApiUrl}{simulationId}/state";

        using (UnityWebRequest request = new UnityWebRequest(apiUrl, "GET"))
        {
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Accept", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                SimulationResponse response =
                    JsonConvert.DeserializeObject<SimulationResponse>(request.downloadHandler.text);

                HandlePoliceActions(response);
                UpdateCarsTicketStatus(response);

                // Manejo del dron
                HandleDroneActions(response);
            }
            else
            {
                Debug.LogError("Error al obtener el /state: " + request.error);
            }
        }
    }

    /// <summary>
    /// Actualiza las posiciones de coches y motos basadas en la respuesta del /step
    /// </summary>
    void UpdateEntities(StepResponse response)
    {
        if (response.updated_positions != null)
        {
            if (response.updated_positions.cars != null)
            {
                foreach (var car in response.updated_positions.cars)
                {
                    if (cars.ContainsKey(car.id))
                    {
                        Vector2 newPos = new Vector2(car.position[0], car.position[1]);
                        cars[car.id].MoveTo(newPos);
                    }
                }
            }

            if (response.updated_positions.motorcycles != null)
            {
                foreach (var moto in response.updated_positions.motorcycles)
                {
                    if (motorcycles.ContainsKey(moto.id))
                    {
                        Vector2 newPos = new Vector2(moto.position[0], moto.position[1]);
                        motorcycles[moto.id].MoveTo(newPos);
                    }
                }
            }

            // Dron Update (si la API lo usa en updated_positions)
            if (response.updated_positions.drone != null && droneBehavior != null)
            {
                // Si quisieras mover el dron, podrías hacerlo acá,
                // pero dijiste que el dron NO se mueve, solo suena.
                // Aun así, si la API cambiara la pos, podríamos setearlo:
                // droneBehavior.transform.position = new Vector3(...);
            }
        }
    }

    /// <summary>
    /// Maneja las acciones del policía (multas, congestiones, drones)
    /// para /create (initial_state) o /state (agents)
    /// </summary>
    void HandlePoliceActions(SimulationResponse response)
    {
        PoliceOfficerData policeData = null;

        if (response.initial_state != null && 
            response.initial_state.agents != null && 
            response.initial_state.agents.police != null)
        {
            policeData = response.initial_state.agents.police;
        }
        else if (response.agents != null && response.agents.police != null)
        {
            policeData = response.agents.police;
        }

        if (policeData != null && policeOfficer != null)
        {
            currentTicketsIssued = policeData.tickets_issued_count;
            currentCongestionsResolved = policeData.congestion_resolved;
            currentDroneRequests = policeData.drone_requests;

            // Nuevas multas
            if (currentTicketsIssued > previousTicketsIssued)
            {
                int ticketsToIssue = currentTicketsIssued - previousTicketsIssued;
                for (int i = 0; i < ticketsToIssue; i++)
                {
                    policeOfficer.IssueTicket();
                }
            }

            // Nuevas congestiones resueltas
            if (currentCongestionsResolved > previousCongestionsResolved)
            {
                policeOfficer.ResolveCongestion();
            }

            // Nuevas solicitudes de dron
            if (currentDroneRequests > previousDroneRequests)
            {
                int dronesToRequest = currentDroneRequests - previousDroneRequests;
                for (int i = 0; i < dronesToRequest; i++)
                {
                    policeOfficer.RequestDroneSupport();
                }
            }

            previousTicketsIssued = currentTicketsIssued;
            previousCongestionsResolved = currentCongestionsResolved;
            previousDroneRequests = currentDroneRequests;
        }
        else
        {
            Debug.LogError("Datos de policía nulos en el estado de la simulación.");
        }
    }

    /// <summary>
    /// Maneja el dron: reproduce sonidos si resolvió congestiones o colisiones
    /// </summary>
    void HandleDroneActions(SimulationResponse response)
    {
        // Revisamos la info del dron en /state
        if (response.agents != null && response.agents.drone != null && droneBehavior != null)
        {
            int currentDroneCongestions = response.agents.drone.congestions_resolved;
            int currentDroneCollisions = response.agents.drone.collisions_resolved;

            // ¿Incrementaron las congestiones resueltas?
            if (currentDroneCongestions > previousDroneCongestions)
            {
                int newCount = currentDroneCongestions - previousDroneCongestions;
                for (int i = 0; i < newCount; i++)
                {
                    droneBehavior.ResolveCongestion();
                }
            }

            // ¿Incrementaron las colisiones resueltas?
            if (currentDroneCollisions > previousDroneCollisions)
            {
                int newCount = currentDroneCollisions - previousDroneCollisions;
                for (int i = 0; i < newCount; i++)
                {
                    droneBehavior.ResolveCollision();
                }
            }

            previousDroneCongestions = currentDroneCongestions;
            previousDroneCollisions = currentDroneCollisions;
        }
        else
        {
            // No hay dron en la simulación, o no lo hemos instanciado
            // Debug.Log("Datos de dron nulos o droneBehavior no asignado.");
        }
    }

    /// <summary>
    /// 5) Actualiza el campo "ticketed" de cada coche según el /state actual
    /// </summary>
    void UpdateCarsTicketStatus(SimulationResponse response)
    {
        if (response.agents != null && response.agents.cars != null)
        {
            foreach (var carData in response.agents.cars)
            {
                if (cars.ContainsKey(carData.id))
                {
                    cars[carData.id].SetTicketed(carData.ticketed);
                }
            }
        }
        /*
        // Si quieres aplicar ticketed también a las motos, 
        // define un método SetTicketed en MotorcycleMovement y descomenta esto:
        if (response.agents != null && response.agents.motorcycles != null)
        {
            foreach (var motoData in response.agents.motorcycles)
            {
                if (motorcycles.ContainsKey(motoData.id))
                {
                    // motorcycles[motoData.id].SetTicketed(motoData.ticketed);
                }
            }
        }
        */
    }
}
