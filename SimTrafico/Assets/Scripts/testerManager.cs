using UnityEngine;

public class TesterManager : MonoBehaviour
{
    [Header("Grid Configuration")]
    public int gridSize = 10;         // Número de celdas en la cuadrícula (x y z)
    public float cellSize = 10f;      // Tamaño de cada celda
    public GameObject intersectionPrefab; // Prefab para cada "cuadrado" (o nodo) de la cuadrícula

    [Header("Gizmo Settings")]
    public Color lineColor = Color.yellow; // Color de las líneas en la vista de escena
    public bool showLinesInEditor = true;  // ¿Dibujar líneas en la vista del Editor?

    private void Start()
    {
        // Generamos un “cuadrado” en cada intersección
        for (int x = 0; x < gridSize; x++)
        {
            for (int y = 0; y < gridSize; y++)
            {
                // Calculamos la posición en Unity
                Vector3 position = new Vector3(x * cellSize, 0f, y * cellSize);

                // Instanciamos el prefab de la intersección (si existe)
                if (intersectionPrefab != null)
                {
                    Instantiate(intersectionPrefab, position, Quaternion.identity, transform);
                }
                else
                {
                    Debug.LogWarning("No se asignó un intersectionPrefab en TesterManager.");
                }
            }
        }
    }

    // Este método dibuja líneas en la vista del Editor (y en modo de juego si tienes Gizmos activados)
    private void OnDrawGizmos()
    {
        if (!showLinesInEditor) return;

        Gizmos.color = lineColor;

        // Recorremos cada intersección y dibujamos líneas hacia la derecha y hacia "arriba"
        for (int x = 0; x < gridSize; x++)
        {
            for (int y = 0; y < gridSize; y++)
            {
                Vector3 start = new Vector3(x * cellSize, 0f, y * cellSize);

                // Dibuja la línea hacia la intersección de la derecha
                if (x < gridSize - 1)
                {
                    Vector3 right = new Vector3((x + 1) * cellSize, 0f, y * cellSize);
                    Gizmos.DrawLine(start, right);
                }

                // Dibuja la línea hacia la intersección “superior”
                if (y < gridSize - 1)
                {
                    Vector3 up = new Vector3(x * cellSize, 0f, (y + 1) * cellSize);
                    Gizmos.DrawLine(start, up);
                }
            }
        }
    }
}
