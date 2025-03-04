using UnityEngine;
using System.Collections;

public class CarMovement : MonoBehaviour
{
    public int carId;
    public float moveSpeed = 5f; // Ahora cada carro tiene su propia velocidad
    private Vector3 targetPosition;
    private MusicManager musicManager;

    private void Start()
    {
        targetPosition = transform.position; // Inicia en su posición inicial
        musicManager = FindObjectOfType<MusicManager>();
    }

    public void MoveTo(Vector2 newPos)
    {
        targetPosition = new Vector3(newPos.x * 10, transform.position.y, newPos.y * 10);
        StartCoroutine(MoveSmoothly());
    }

    IEnumerator MoveSmoothly()
    {
        Vector3 startPos = transform.position;
        Vector3 endPos = targetPosition;

        float distance = Vector3.Distance(startPos, endPos);
        float duration = distance / moveSpeed; // Calculamos el tiempo basado en la velocidad individual

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
        if (other.CompareTag("Player")) // Verifica colisión con otro objeto de tag "Player"
        {
            if (musicManager != null)
            {
                musicManager.PlayExplosion();
            }
        }
    }
}
