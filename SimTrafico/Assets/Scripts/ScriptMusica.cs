using UnityEngine;

public class MusicManager : MonoBehaviour
{
    public AudioClip musicClip; // Clip de música
    public AudioClip explosionClip; // Clip de sonido para explosiones

    [Range(0f, 1f)] public float musicVolume = 1f; // Volumen de la música
    [Range(0f, 1f)] public float sfxVolume = 1f; // Volumen del efecto de sonido

    private AudioSource audioSource;

    private void Start()
    {
        audioSource = gameObject.AddComponent<AudioSource>();
        audioSource.loop = true;
        audioSource.volume = musicVolume;
        
        if (musicClip != null)
        {
            audioSource.clip = musicClip;
            audioSource.Play();
        }
    }

    public void PlayExplosion()
    {
        if (explosionClip != null)
        {
            audioSource.PlayOneShot(explosionClip, sfxVolume);
        }
    }
}
