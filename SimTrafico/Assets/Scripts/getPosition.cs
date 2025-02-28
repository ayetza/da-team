using UnityEngine;
using UnityEngine.Tilemaps;


public class GridPositionChecker : MonoBehaviour

{

    public Grid grid; // Reference to the Grid component



    void Update()

    {

        Vector3Int gridCell = grid.WorldToCell(transform.position); // Get grid coordinates

        Debug.Log($"Current grid position: X: {gridCell.x}, Y: {gridCell.y}"); 

    }

}
