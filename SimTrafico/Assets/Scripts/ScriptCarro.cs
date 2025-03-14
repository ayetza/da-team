using UnityEngine;
using System.Collections;

public class CarMovement : MonoBehaviour
{
    public int carId;
    private float moveSpeed = 5f;
    public float rotationSpeed = 6f;
    private bool isMoving;
    private Vector3 targetPosition;

    public float hoverAmplitudeMin = 0.1f;
    public float hoverAmplitudeMax = 0.3f;
    public float hoverSpeedMin = 1f;
    public float hoverSpeedMax = 2.5f;

    private float hoverAmplitude;
    private float hoverSpeed;
    private float baseY;

    private bool ticketEffectActive;

    [SerializeField]
    private GameObject redLightPrefab;

    [Header("Collision Lift Settings")]
    public float liftHeight = 2f; 
    public float liftDuration = 1f; 
    public float liftSpeedMultiplier = 2f; // 🔥 Hace que suba más rápido
    private bool isLifted;

    private float originalY;

    private void Start()
    {
        targetPosition = transform.position;
        
        baseY = transform.position.y;
        originalY = baseY;

        hoverAmplitude = Random.Range(hoverAmplitudeMin, hoverAmplitudeMax);
        hoverSpeed = Random.Range(hoverSpeedMin, hoverSpeedMax);

        StartCoroutine(HoverEffect());
    }

    private IEnumerator HoverEffect()
    {
        while (true)
        {
            float hoverOffset = Mathf.Sin(Time.time * hoverSpeed) * hoverAmplitude;
            transform.position = new Vector3(
                transform.position.x,
                baseY + hoverOffset,
                transform.position.z
            );
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
        Vector3 destinationXZ = new Vector3(finalPosition.x * 10f, transform.position.y, finalPosition.y * 10f);

        float distXZ = Vector2.Distance(
            new Vector2(transform.position.x, transform.position.z),
            new Vector2(destinationXZ.x, destinationXZ.z)
        );

        while (distXZ > 0.1f)
        {
            Vector3 nextStep = GetNextStep(destinationXZ);
            yield return RotateTowards(nextStep);
            yield return MoveSmoothly(nextStep);

            distXZ = Vector2.Distance(
                new Vector2(transform.position.x, transform.position.z),
                new Vector2(destinationXZ.x, destinationXZ.z)
            );
        }

        isMoving = false;
    }

    Vector3 GetNextStep(Vector3 destinationXZ)
    {
        Vector3 direction = destinationXZ - transform.position;
        Vector3 step = transform.position;

        if (Mathf.Abs(direction.x) > 0.1f && Mathf.Abs(direction.z) > 0.1f)
        {
            if (Random.value < 0.5f)
                step.x += Mathf.Sign(direction.x) * 10f;
            else
                step.z += Mathf.Sign(direction.z) * 10f;
        }
        else if (Mathf.Abs(direction.x) > 0.1f)
        {
            step.x += Mathf.Sign(direction.x) * 10f;
        }
        else if (Mathf.Abs(direction.z) > 0.1f)
        {
            step.z += Mathf.Sign(direction.z) * 10f;
        }
        return step;
    }

    IEnumerator RotateTowards(Vector3 targetPos)
    {
        Vector3 direction = (targetPos - transform.position).normalized;
        if (direction != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            while (Quaternion.Angle(transform.rotation, targetRotation) > 0.1f)
            {
                transform.rotation = Quaternion.Lerp(
                    transform.rotation, targetRotation,
                    Time.deltaTime * rotationSpeed
                );
                yield return null;
            }
            transform.rotation = targetRotation;
        }
    }

    IEnumerator MoveSmoothly(Vector3 endPos)
    {
        Vector3 startPos = transform.position;
        Vector3 endPosFixed = new Vector3(endPos.x, transform.position.y, endPos.z);

        float distanceXZ = Vector2.Distance(
            new Vector2(startPos.x, startPos.z),
            new Vector2(endPosFixed.x, endPosFixed.z)
        );

        float duration = distanceXZ / moveSpeed;
        float elapsedTime = 0f;

        while (elapsedTime < duration)
        {
            float t = elapsedTime / duration;

            float newX = Mathf.Lerp(startPos.x, endPosFixed.x, t);
            float newZ = Mathf.Lerp(startPos.z, endPosFixed.z, t);
            
            transform.position = new Vector3(newX, transform.position.y, newZ);

            elapsedTime += Time.deltaTime;
            yield return null;
        }
        transform.position = new Vector3(endPosFixed.x, transform.position.y, endPosFixed.z);
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("CarMovement"))
        {
            var otherCar = other.GetComponent<CarMovement>();
            if (otherCar != null)
            {
                if (this.carId > otherCar.carId)
                {
                    if (!isLifted)
                    {
                        StartCoroutine(LiftUntilNoCollision());
                    }
                }
            }
        }
    }

    IEnumerator LiftUntilNoCollision()
    {
        isLifted = true;

        float startY = baseY;
        float elevatedY = baseY + liftHeight;
        float elapsed = 0f;

        // 1. 🔥 Subimos más rápido multiplicando la velocidad de subida
        while (elapsed < (liftDuration / liftSpeedMultiplier))
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / (liftDuration / liftSpeedMultiplier));
            baseY = Mathf.Lerp(startY, elevatedY, t);
            yield return null;
        }

        // 2. Esperamos hasta que no haya colisión
        yield return new WaitUntil(() => !IsCollidingWithCar());

        // 3. 🔥 Bajamos con velocidad normal
        elapsed = 0f;
        while (elapsed < liftDuration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / liftDuration);
            baseY = Mathf.Lerp(elevatedY, startY, t);
            yield return null;
        }

        baseY = startY;
        isLifted = false;
    }

    bool IsCollidingWithCar()
    {
        Collider[] hits = Physics.OverlapSphere(transform.position, 1f);
        foreach (var h in hits)
        {
            if (h.CompareTag("CarMovement") && h.gameObject != this.gameObject)
            {
                return true;
            }
        }
        return false;
    }

    public void SetTicketed(bool ticketed)
    {
        if (ticketed && !ticketEffectActive)
        {
            StartCoroutine(TicketEffect());
        }
    }

    IEnumerator TicketEffect()
    {
        ticketEffectActive = true;

        if (redLightPrefab != null)
        {
            GameObject lightObj = Instantiate(redLightPrefab, transform);
            lightObj.transform.localPosition = new Vector3(0f, 1f, 0f);
        }

        yield return new WaitForSeconds(5f);

        if (redLightPrefab != null)
        {
            GameObject existing = transform.Find(redLightPrefab.name + "(Clone)")?.gameObject;
            if (existing != null) Destroy(existing);
        }

        ticketEffectActive = false;
    }
}
