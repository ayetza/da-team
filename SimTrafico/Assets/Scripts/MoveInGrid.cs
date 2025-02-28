using UnityEngine;
using UnityEngine.Tilemaps;

public class MoveInGrid : MonoBehaviour
{
    public float moveInterval = 2f; // Time in seconds between each move
    [SerializeField] public Tilemap groundTilemap;

    private void Awake()
    {
        groundTilemap = GameAssets.i.tilemap;
    }


    private void Move(Vector3 direction) {
        transform.position += direction;
    }

    private void MoveToRandomTile() {
        // Ensure the Tilemap is assigned before accessing it
        if (groundTilemap == null) {
            Debug.LogError("Tilemap not assigned.");
            return;
        }

        // Get the bounds of the tilemap
        BoundsInt bounds = groundTilemap.cellBounds;

        // Get a random position within the bounds of the tilemap
        int randomX = Random.Range(bounds.xMin, bounds.xMax);
        int randomY = Random.Range(bounds.yMin, bounds.yMax);

        // Convert the random grid position to world coordinates
        Vector3Int randomCell = new Vector3Int(randomX, randomY, 0);
        Vector3 worldPosition = groundTilemap.GetCellCenterWorld(randomCell);

        // Move the object to the random tile's world position
        transform.position = worldPosition;

        Debug.Log($"Moved to random tile at: {worldPosition}");
    }
}
