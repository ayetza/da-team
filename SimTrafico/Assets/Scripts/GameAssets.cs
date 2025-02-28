using UnityEngine;
using UnityEngine.Tilemaps;

public class GameAssets : MonoBehaviour
{
    private static GameAssets _i;

    public static GameAssets i
    {
        get
        {
            if (_i == null)
            {
                // Load and instantiate the GameAssets prefab (which should have the Tilemap component attached)
                _i = Instantiate(Resources.Load("GameAssetsPrefab") as GameAssets);
            }
            return _i;
        }
    }

    // Reference to the Tilemap
    public Tilemap tilemap;
}
