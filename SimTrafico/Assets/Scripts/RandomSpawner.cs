using UnityEngine;
using UnityEngine.Tilemaps;

public class RandomSpawner : MonoBehaviour
{
    public Grid grid; // Reference to the Grid component
    public Tilemap tilemap; // Reference to the Tilemap
    public GameObject ItemPrefab;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
            SpawnObjectAtPosition();
    }

    void SpawnObjectAtPosition()
{
    Vector3Int gridCell = grid.WorldToCell(transform.position); // Get grid coordinates
    // Get the world position of the tile center
    Vector3 worldPosition = tilemap.GetCellCenterWorld(gridCell);

    // Instantiate the item at the tile's world position
    GameObject spawnedItem = Instantiate(ItemPrefab, worldPosition, Quaternion.identity);

    // Make the spawned object look at the origin (0, 0)
    Vector3 directionToOrigin = worldPosition - new Vector3(0, 0, 0) ; // Direction towards (0, 0)
    spawnedItem.transform.rotation = Quaternion.LookRotation(directionToOrigin);

    Debug.Log($"Spawned at grid position: X: {gridCell.x}, Y: {gridCell.y}, World Position: {worldPosition}");
}

}
