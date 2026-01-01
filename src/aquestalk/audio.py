"""
Audio utilities for AquesTalk output.
"""

import wave
import struct
from typing import Optional
import numpy as np

from .core import AquesAudio, AquesTalkError

def save_wav(filepath: str, audio: AquesAudio) -> None:
    """
    Save AquesAudio to WAV file.
    
    Args:
        filepath: Path to save WAV file
        audio: AquesAudio object
    
    Raises:
        AquesTalkError: If save fails
    """
    try:
        # AquesTalk already returns complete WAV data
        with open(filepath, 'wb') as f:
            f.write(audio.data)
    except Exception as e:
        raise AquesTalkError(f"Failed to save WAV file: {e}")

def audio_to_numpy(audio: AquesAudio) -> np.ndarray:
    """
    Convert AquesAudio to NumPy array.
    
    Args:
        audio: AquesAudio object
    
    Returns:
        NumPy array of audio samples (int16)
    
    Raises:
        ImportError: If numpy is not installed
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy is required for this function. Install with: pip install numpy")
    
    # Skip WAV header (typically 44 bytes)
    # AquesTalk returns full WAV file
    wav_data = audio.data
    
    # Find data chunk
    data_start = wav_data.find(b'data')
    if data_start == -1:
        # Assume raw PCM data
        pcm_data = wav_data
    else:
        # Extract PCM data from WAV
        data_size = struct.unpack('<I', wav_data[data_start+4:data_start+8])[0]
        pcm_data = wav_data[data_start+8:data_start+8+data_size]
    
    # Convert to numpy array (16-bit signed)
    samples = np.frombuffer(pcm_data, dtype=np.int16)
    
    return samples

def play_audio(audio: AquesAudio, block: bool = True) -> bool:
    """
    Play AquesAudio using available audio backend.
    
    Args:
        audio: AquesAudio object
        block: If True, wait for playback to finish
    
    Returns:
        True if playback started successfully
    
    Note:
        Requires either sounddevice, pyaudio, or playsound
    """
    try:
        # Try sounddevice first
        import sounddevice as sd
        samples = audio_to_numpy(audio)
        sd.play(samples, audio.sample_rate, blocking=block)
        return True
        
    except ImportError:
        try:
            # Try pyaudio
            import pyaudio
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=audio.channels,
                rate=audio.sample_rate,
                output=True
            )
            
            stream.write(audio.data[44:])  # Skip WAV header
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True
            
        except ImportError:
            try:
                # Try playsound (simplest)
                import tempfile
                import playsound
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    save_wav(tmp.name, audio)
                    playsound.playsound(tmp.name, block=block)
                
                import os
                os.unlink(tmp.name)
                return True
                
            except ImportError:
                print("No audio backend found. Install one of: sounddevice, pyaudio, playsound")
                return False

def get_audio_info(audio: AquesAudio) -> dict:
    """
    Get information about audio data.
    
    Args:
        audio: AquesAudio object
    
    Returns:
        Dictionary with audio information
    """
    return {
        'sample_rate': audio.sample_rate,
        'bits_per_sample': audio.bits_per_sample,
        'channels': audio.channels,
        'duration_seconds': audio.duration,
        'data_size_bytes': len(audio.data),
        'num_samples': len(audio.data) // (audio.bits_per_sample // 8 * audio.channels)
    }