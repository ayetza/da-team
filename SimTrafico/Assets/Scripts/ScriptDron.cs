using UnityEngine;
using System.Collections;

public class DroneBehavior : MonoBehaviour
{
    [Header("Flotación Futurista")]
    public float hoverAmplitudeMin = 0.1f;
    public float hoverAmplitudeMax = 0.3f;
    public float hoverSpeedMin = 1f;
    public float hoverSpeedMax = 2.5f;

    [Header("Altura y Elevación")]
    // Un poco más alto que el policía (por ejemplo 18f en lugar de 15f)
    public float targetHeight = 18f;
    public float liftSpeed = 3f;

    [Header("Rotación Aleatoria")]
    public float minRotationSpeed = 5f;
    public float maxRotationSpeed = 15f;
    public float minRotationTime = 1f;
    public float maxRotationTime = 3f;
    public float minPauseTime = 1f;
    public float maxPauseTime = 4f;

    private float hoverAmplitude;
    private float hoverSpeed;
    private Vector3 initialPosition;
    private bool hasReachedHeight = false;
    private MusicManager musicManager;

    private void Start()
    {
        // Escogemos valores aleatorios de flotación
        hoverAmplitude = Random.Range(hoverAmplitudeMin, hoverAmplitudeMax);
        hoverSpeed = Random.Range(hoverSpeedMin, hoverSpeedMax);

        // Posición inicial
        initialPosition = transform.position;

        // Referencia al MusicManager
        musicManager = FindObjectOfType<MusicManager>();

        // Comenzamos la corrutina para elevarnos a la altura objetivo
        StartCoroutine(LiftToHeight());
    }

    private IEnumerator LiftToHeight()
    {
        // Definimos la posición objetivo (con la targetHeight elegida)
        Vector3 targetPosition = new Vector3(initialPosition.x, targetHeight, initialPosition.z);

        // Interpolamos desde la posición actual hasta la targetHeight
        while (Vector3.Distance(transform.position, targetPosition) > 0.1f)
        {
            transform.position = Vector3.Lerp(transform.position, targetPosition, Time.deltaTime * liftSpeed);
            yield return null;
        }

        hasReachedHeight = true;

        // Aquí podrías reproducir un sonido propio del dron (similar al PoliceSiren)
        // Si tu MusicManager tiene un método, por ejemplo "PlayDroneSiren()", lo llamas:
        // musicManager?.PlayDroneSiren();

        // Si no, usa un método genérico que ya tengas o deja en blanco
        // musicManager?.PlayPoliceSiren(); // <-- si quieres usar la misma sirena del policía

        // Comenzamos la flotación y la rotación
        StartCoroutine(HoverEffect());
        StartCoroutine(RandomRotationLoop());
    }

    private IEnumerator HoverEffect()
    {
        while (true)
        {
            float hoverOffset = Mathf.Sin(Time.time * hoverSpeed) * hoverAmplitude;
            // Mantenemos la X y Z fijos, variamos la Y con el offset
            transform.position = new Vector3(initialPosition.x, targetHeight + hoverOffset, initialPosition.z);
            yield return null;
        }
    }

    private IEnumerator RandomRotationLoop()
    {
        while (true)
        {
            // Escoge dirección aleatoria (50% izquierda, 50% derecha)
            float direction = Random.value < 0.5f ? -1f : 1f;

            // Velocidad de giro aleatoria dentro del rango
            float rotationSpeed = Random.Range(minRotationSpeed, maxRotationSpeed);

            // Duración aleatoria del giro
            float rotationDuration = Random.Range(minRotationTime, maxRotationTime);

            float elapsedTime = 0f;

            // Rotamos sobre el eje Y
            while (elapsedTime < rotationDuration)
            {
                transform.Rotate(Vector3.up, direction * rotationSpeed * Time.deltaTime);
                elapsedTime += Time.deltaTime;
                yield return null;
            }

            // Pausa aleatoria antes de la siguiente rotación
            float pauseTime = Random.Range(minPauseTime, maxPauseTime);
            yield return new WaitForSeconds(pauseTime);
        }
    }

    /// <summary>
    /// Permite posicionar el dron al iniciar. Puedes llamarlo desde tu APIManager.
    /// </summary>
    public void SetInitialPosition(Vector2 position)
    {
        initialPosition = new Vector3(position.x * 10, targetHeight, position.y * 10);
        transform.position = initialPosition;
    }

    /// <summary>
    /// Se llama cuando el dron resuelve una colisión; reproduce un sonido o muestra un efecto.
    /// </summary>
    public void ResolveCollision()
    {
        Debug.Log("Dron ha resuelto una colisión.");
        // Usa el método que gustes del MusicManager
        musicManager?.PlayExplosion();
    }

    /// <summary>
    /// Se llama cuando el dron resuelve una congestión; reproduce un sonido o muestra un efecto.
    /// </summary>
    public void ResolveCongestion()
    {
        Debug.Log("Dron ha resuelto una congestión.");
        // Usa el método que gustes del MusicManager
        musicManager?.PlayCongestionResolved();
    }
}
