using System.Collections;
using UnityEngine;

public class ObjectSwitcher : MonoBehaviour
{
    public GameObject[] frames; // Assign your objects in the Inspector
    public float frameRate = 0.5f; // Time between frames

    private int currentFrame = 0;

    void Start()
    {
        StartCoroutine(SwitchFrames());
    }

    IEnumerator SwitchFrames()
    {
        while (true)
        {
            for (int i = 0; i < frames.Length; i++)
                frames[i].SetActive(i == currentFrame);

            currentFrame = (currentFrame + 1) % frames.Length;
            yield return new WaitForSeconds(frameRate);
        }
    }
}
