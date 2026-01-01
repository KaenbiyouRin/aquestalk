"""
AquesTalk - Python wrapper for AquesTalk speech synthesis engine.
"""

from .core import AquesTalk, AquesTalkError, AquesAudio
from .audio import save_wav, play_audio, audio_to_numpy

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "AquesTalk", 
    "AquesTalkError", 
    "AquesAudio",
    "save_wav", 
    "play_audio", 
    "audio_to_numpy"
]