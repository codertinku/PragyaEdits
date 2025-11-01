"""
Background Music Generation Module
Generates copyright-free background music with mood-based selection and auto-sync
"""

import subprocess
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
import json


def generate_tone_sequence(duration_sec: float, mood: str, sample_rate: int = 44100) -> np.ndarray:
    """
    Generate a simple tone sequence based on mood
    
    Args:
        duration_sec: Duration in seconds
        mood: Mood type (energetic, calm, happy, sad, neutral)
        sample_rate: Audio sample rate
    
    Returns:
        Audio samples as numpy array
    """
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    
    # Define chord progressions and rhythms based on mood
    if mood == "energetic":
        # Fast tempo, major chords
        freqs = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C
        tempo = 2.0  # Fast
    elif mood == "calm":
        # Slow tempo, ambient tones
        freqs = [220.00, 261.63, 329.63, 440.00]  # A, C, E, A
        tempo = 0.5  # Slow
    elif mood == "happy":
        # Medium-fast tempo, major chords
        freqs = [293.66, 369.99, 440.00, 587.33]  # D, F#, A, D
        tempo = 1.5
    elif mood == "sad":
        # Slow tempo, minor chords
        freqs = [220.00, 261.63, 311.13, 440.00]  # A, C, Eb, A
        tempo = 0.6
    else:  # neutral
        freqs = [261.63, 293.66, 329.63, 392.00]  # C, D, E, G
        tempo = 1.0
    
    # Generate music with simple oscillator
    audio = np.zeros_like(t)
    for i, freq in enumerate(freqs):
        phase = (t * tempo + i * duration_sec / len(freqs)) % duration_sec
        weight = np.sin(2 * np.pi * phase / duration_sec)
        audio += 0.25 * np.sin(2 * np.pi * freq * t) * (weight ** 2)
    
    # Add gentle envelope
    envelope = np.exp(-t / (duration_sec * 0.8))
    envelope = np.minimum(envelope, 1.0)
    fade_in = np.linspace(0, 1, int(sample_rate * 0.5))
    envelope[:len(fade_in)] *= fade_in
    
    audio *= envelope
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.3
    
    return audio.astype(np.float32)


def generate_background_music(output_path: str, duration_sec: float, 
                             mood: str = "neutral", style: str = "ambient") -> str:
    """
    Generate copyright-free background music
    
    Args:
        output_path: Path to save generated music
        duration_sec: Duration in seconds
        mood: Music mood (energetic, calm, happy, sad, neutral)
        style: Music style (ambient, rhythmic, melodic)
    
    Returns:
        Path to generated music file
    """
    # Generate audio samples
    audio = generate_tone_sequence(duration_sec, mood)
    
    # Save as temporary WAV file
    import soundfile as sf
    temp_wav = str(Path(output_path).with_suffix('.wav'))
    sf.write(temp_wav, audio, 44100)
    
    # Apply audio effects based on style
    if style == "ambient":
        effect_filter = "aecho=0.8:0.9:1000|1800:0.3|0.25,equalizer=f=2000:t=h:w=500:g=-5"
    elif style == "rhythmic":
        effect_filter = "acompressor=threshold=0.05:ratio=4:attack=5:release=50,equalizer=f=100:t=h:w=200:g=5"
    elif style == "melodic":
        effect_filter = "chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3,equalizer=f=1000:t=h:w=1000:g=3"
    else:
        effect_filter = "aecho=0.8:0.9:1000:0.3"
    
    # Convert to final format with effects
    cmd = [
        "ffmpeg", "-y", "-i", temp_wav,
        "-af", effect_filter,
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    # Cleanup temp file
    Path(temp_wav).unlink(missing_ok=True)
    
    return str(output_path)


def detect_beats(video_path: str, audio_path: Optional[str] = None) -> List[float]:
    """
    Detect beats in video/audio for synchronization
    
    Args:
        video_path: Path to video file
        audio_path: Optional separate audio path
    
    Returns:
        List of beat timestamps in seconds
    """
    import librosa
    
    # Extract audio if needed
    if audio_path is None:
        temp_audio = "/tmp/temp_beat_audio.wav"
        cmd = ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le", temp_audio]
        subprocess.run(cmd, check=True, capture_output=True)
        audio_path = temp_audio
    
    # Load audio and detect beats
    y, sr = librosa.load(audio_path, sr=None)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Cleanup temp file if created
    if audio_path == "/tmp/temp_beat_audio.wav":
        Path(audio_path).unlink(missing_ok=True)
    
    return beat_times.tolist()


def sync_music_to_beats(video_path: str, music_path: str, output_path: str,
                       beat_sync: bool = True, volume_level: float = 0.3) -> str:
    """
    Sync background music to video beats and mix with original audio
    
    Args:
        video_path: Path to input video
        music_path: Path to background music
        output_path: Path to save output video
        beat_sync: Enable beat synchronization
        volume_level: Background music volume (0.0 to 1.0)
    
    Returns:
        Path to output video with synced music
    """
    if beat_sync:
        # Detect beats in original video
        beats = detect_beats(video_path)
        
        # For now, we'll use a simple mixing approach
        # In a more advanced version, this could time-stretch music to match beats
        pass
    
    # Mix background music with original audio
    filter_complex = f"[0:a]volume=0.7[orig];[1:a]volume={volume_level}[music];[orig][music]amix=inputs=2:duration=first:dropout_transition=2[a]"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(music_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output_path)


def get_mood_music_config(mood: str) -> Dict:
    """
    Get music generation configuration for a given mood
    
    Args:
        mood: Mood type
    
    Returns:
        Configuration dictionary
    """
    configs = {
        "energetic": {"style": "rhythmic", "tempo": "fast", "volume": 0.25},
        "calm": {"style": "ambient", "tempo": "slow", "volume": 0.20},
        "happy": {"style": "melodic", "tempo": "medium", "volume": 0.30},
        "sad": {"style": "ambient", "tempo": "slow", "volume": 0.20},
        "neutral": {"style": "ambient", "tempo": "medium", "volume": 0.25},
        "surprised": {"style": "rhythmic", "tempo": "fast", "volume": 0.30},
    }
    return configs.get(mood, configs["neutral"])
