using UnityEngine;

public class MusicManager : MonoBehaviour
{
    public AudioClip musicClip; // Clip de música
    public AudioClip explosionClip; // Clip de sonido para explosiones
    public AudioClip policeSirenClip; // Clip de sonido para la sirena de policía
    public AudioClip ticketIssuedClip; // Clip de sonido para emisión de multas
    public AudioClip congestionResolvedClip; // Clip de sonido para resolver congestión
    public AudioClip droneRequestClip; // Clip de sonido para solicitud de dron

    // Nuevos sonidos para el dron
    public AudioClip droneSirenClip; // Clip de sonido para el dron (sirena o presencia)
    public AudioClip droneResolveCongestionClip; // Clip de sonido para cuando el dron resuelve una congestión
    public AudioClip droneResolveCollisionClip; // Clip de sonido para cuando el dron resuelve una colisión

    [Range(1f, 100f)] public float musicVolume = 100f; // Volumen de la música (1-100)
    [Range(1f, 100f)] public float sfxVolume = 100f; // Volumen general de efectos de sonido (1-100)

    private AudioSource musicSource;
    private AudioSource sfxSource;

    private void Start()
    {
        musicSource = gameObject.AddComponent<AudioSource>();
        musicSource.loop = true;
        musicSource.volume = NormalizeVolume(musicVolume);
        
        if (musicClip != null)
        {
            musicSource.clip = musicClip;
            musicSource.Play();
        }

        sfxSource = gameObject.AddComponent<AudioSource>();
        sfxSource.volume = NormalizeVolume(sfxVolume);
    }

    private float NormalizeVolume(float value)
    {
        return Mathf.Clamp(value / 100f, 0f, 1f); // Convierte el rango de 1-100 a 0-1
    }

    public void SetMusicVolume(float value)
    {
        musicVolume = Mathf.Clamp(value, 1f, 100f);
        musicSource.volume = NormalizeVolume(musicVolume);
    }

    public void SetSFXVolume(float value)
    {
        sfxVolume = Mathf.Clamp(value, 1f, 100f);
        sfxSource.volume = NormalizeVolume(sfxVolume);
    }

    private void PlaySound(AudioClip clip)
    {
        if (clip != null)
        {
            sfxSource.PlayOneShot(clip, NormalizeVolume(sfxVolume));
        }
    }

    public void PlayExplosion() => PlaySound(explosionClip);
    public void PlayPoliceSiren() => PlaySound(policeSirenClip);
    public void PlayTicketIssued() => PlaySound(ticketIssuedClip);
    public void PlayCongestionResolved() => PlaySound(congestionResolvedClip);
    public void PlayDroneRequest() => PlaySound(droneRequestClip);

    // Métodos para el dron
    public void PlayDroneSiren() => PlaySound(droneSirenClip);
    public void PlayDroneResolveCongestion() => PlaySound(droneResolveCongestionClip);
    public void PlayDroneResolveCollision() => PlaySound(droneResolveCollisionClip);
}
