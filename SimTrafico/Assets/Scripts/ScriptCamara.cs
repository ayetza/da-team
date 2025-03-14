using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float moveSpeed = 10f; // Velocidad normal
    public float fastSpeedMultiplier = 2f; // Multiplicador cuando se mantiene Shift
    public float mouseSensitivity = 2f; // Sensibilidad del mouse
    public float verticalSpeed = 5f; // Velocidad de subida/bajada

    private float rotationX = 0f;
    private float rotationY = 0f;

    void Start()
    {
        // Bloquear cursor en el centro y ocultarlo
        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        // Movimiento de la cámara con WASD y altura con Espacio/Control
        float speed = Input.GetKey(KeyCode.LeftShift) ? moveSpeed * fastSpeedMultiplier : moveSpeed;

        Vector3 move = new Vector3(
            Input.GetAxis("Horizontal"), // A/D = Izquierda/Derecha
            (Input.GetKey(KeyCode.Space) ? 1 : 0) - (Input.GetKey(KeyCode.LeftControl) ? 1 : 0), // Espacio/Subir, Control/Bajar
            Input.GetAxis("Vertical") // W/S = Adelante/Atrás
        );

        transform.position += transform.TransformDirection(move) * speed * Time.deltaTime;

        // Rotación de la cámara con el mouse
        rotationX -= Input.GetAxis("Mouse Y") * mouseSensitivity;
        rotationY += Input.GetAxis("Mouse X") * mouseSensitivity;
        rotationX = Mathf.Clamp(rotationX, -90f, 90f); // Limita la rotación vertical

        transform.rotation = Quaternion.Euler(rotationX, rotationY, 0);
    }
}
