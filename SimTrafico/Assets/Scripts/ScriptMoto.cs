using UnityEngine;
using System.Collections;

public class MotorcycleMovement : MonoBehaviour
{
    public int motoId;
    private float moveSpeed = 6f; // Velocidad inicial
    public float rotationSpeed = 6f;
    private bool isMoving = false;
    private Vector3 targetPosition;

    [Header("Flotación Futurista")]
    public float hoverAmplitudeMin = 0.1f;
    public float hoverAmplitudeMax = 0.3f;
    public float hoverSpeedMin = 1f;
    public float hoverSpeedMax = 2.5f;

    private MusicManager musicManager;
    private float hoverAmplitude;
    private float hoverSpeed;
    private float baseY;

    private void Start()
    {
        targetPosition = transform.position;
        musicManager = FindObjectOfType<MusicManager>();

        baseY = transform.position.y;
        hoverAmplitude = Random.Range(hoverAmplitudeMin, hoverAmplitudeMax);
        hoverSpeed = Random.Range(hoverSpeedMin, hoverSpeedMax);

        StartCoroutine(HoverEffect());
    }

    private IEnumerator HoverEffect()
    {
        while (true)
        {
            float hoverOffset = Mathf.Sin(Time.time * hoverSpeed) * hoverAmplitude;
            transform.position = new Vector3(transform.position.x, baseY + hoverOffset, transform.position.z);
            yield return null;
        }
    }

    public void SetSpeed(float newSpeed)
    {
        moveSpeed = newSpeed;
    }

    public void MoveTo(Vector2 newPos)
    {
        if (isMoving) return;

        isMoving = true;
        StartCoroutine(MoveStepByStep(newPos));
    }

    IEnumerator MoveStepByStep(Vector2 finalPosition)
    {
        Vector3 destination = new Vector3(finalPosition.x * 10, baseY, finalPosition.y * 10);

        while (Vector3.Distance(transform.position, destination) > 0.1f)
        {
            Vector3 nextStep = GetNextStep(destination);
            StartCoroutine(RotateTowards(nextStep)); // ROTACIÓN ANTES DE MOVER
            yield return StartCoroutine(MoveSmoothly(nextStep));
        }

        isMoving = false;
    }

    Vector3 GetNextStep(Vector3 destination)
    {
        Vector3 direction = destination - transform.position;
        Vector3 step = transform.position;

        if (Mathf.Abs(direction.x) > 0.1f && Mathf.Abs(direction.z) > 0.1f)
        {
            if (Random.value < 0.5f)
                step.x += Mathf.Sign(direction.x) * 10;
            else
                step.z += Mathf.Sign(direction.z) * 10;
        }
        else if (Mathf.Abs(direction.x) > 0.1f)
        {
            step.x += Mathf.Sign(direction.x) * 10;
        }
        else if (Mathf.Abs(direction.z) > 0.1f)
        {
            step.z += Mathf.Sign(direction.z) * 10;
        }

        return step;
    }

    IEnumerator RotateTowards(Vector3 nextPosition)
    {
        Vector3 direction = (nextPosition - transform.position).normalized;
        if (direction != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            while (Quaternion.Angle(transform.rotation, targetRotation) > 0.1f)
            {
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, Time.deltaTime * rotationSpeed);
                yield return null;
            }
            transform.rotation = targetRotation;
        }
    }

    IEnumerator MoveSmoothly(Vector3 endPos)
    {
        Vector3 startPos = transform.position;
        float distance = Vector3.Distance(startPos, endPos);
        float duration = distance / moveSpeed;

        float elapsedTime = 0f;

        while (elapsedTime < duration)
        {
            transform.position = Vector3.Lerp(startPos, endPos, elapsedTime / duration);
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        transform.position = endPos;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            if (musicManager != null)
            {
                musicManager.PlayExplosion();
            }
        }
    }
}
