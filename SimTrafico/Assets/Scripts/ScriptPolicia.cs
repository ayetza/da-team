using UnityEngine;
using System.Collections;

public class PoliceOfficer : MonoBehaviour
{
    public float hoverAmplitudeMin = 0.1f;
    public float hoverAmplitudeMax = 0.3f;
    public float hoverSpeedMin = 1f;
    public float hoverSpeedMax = 2.5f;
    public float targetHeight = 15f;
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
        hoverAmplitude = Random.Range(hoverAmplitudeMin, hoverAmplitudeMax);
        hoverSpeed = Random.Range(hoverSpeedMin, hoverSpeedMax);
        initialPosition = transform.position;
        musicManager = FindObjectOfType<MusicManager>();

        StartCoroutine(LiftToHeight());
    }

    private IEnumerator LiftToHeight()
    {
        Vector3 targetPosition = new Vector3(initialPosition.x, targetHeight, initialPosition.z);

        while (Vector3.Distance(transform.position, targetPosition) > 0.1f)
        {
            transform.position = Vector3.Lerp(transform.position, targetPosition, Time.deltaTime * liftSpeed);
            yield return null;
        }

        hasReachedHeight = true;
        musicManager?.PlayPoliceSiren();
        StartCoroutine(HoverEffect());
        StartCoroutine(RandomRotationLoop());
    }

    private IEnumerator HoverEffect()
    {
        while (true)
        {
            float hoverOffset = Mathf.Sin(Time.time * hoverSpeed) * hoverAmplitude;
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

            while (elapsedTime < rotationDuration)
            {
                transform.Rotate(Vector3.up, direction * rotationSpeed * Time.deltaTime);
                elapsedTime += Time.deltaTime;
                yield return null;
            }

            // Se detiene por un tiempo aleatorio antes de la siguiente rotación
            float pauseTime = Random.Range(minPauseTime, maxPauseTime);
            yield return new WaitForSeconds(pauseTime);
        }
    }

    public void SetInitialPosition(Vector2 position)
    {
        initialPosition = new Vector3(position.x * 10, targetHeight, position.y * 10);
        transform.position = initialPosition;
    }

    public void IssueTicket()
    {
        Debug.Log("Policía ha emitido una multa.");
        musicManager?.PlayTicketIssued();
    }

    public void ResolveCollision()
    {
        Debug.Log("Policía ha resuelto una colisión.");
        musicManager?.PlayExplosion();
    }

    public void ResolveCongestion()
    {
        Debug.Log("Policía ha resuelto una congestión.");
        musicManager?.PlayCongestionResolved();
    }

    public void RequestDroneSupport()
    {
        Debug.Log("Policía ha solicitado apoyo del dron.");
        musicManager?.PlayDroneRequest();
    }
}
