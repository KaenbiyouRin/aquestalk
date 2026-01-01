"""
Core implementation of AquesTalk speech synthesis wrapper.
"""

import ctypes
import os
import sys
from typing import Optional, Tuple, Union
from dataclasses import dataclass

@dataclass
class AquesAudio:
    """Container for synthesized audio data."""
    data: bytes
    sample_rate: int = 8000
    bits_per_sample: int = 16
    channels: int = 1
    duration: float = 0.0
    
    def __post_init__(self):
        """Calculate duration after initialization."""
        if self.data:
            bytes_per_sample = self.bits_per_sample // 8
            num_samples = len(self.data) // (bytes_per_sample * self.channels)
            self.duration = num_samples / self.sample_rate

class AquesTalkError(Exception):
    """Exception for AquesTalk related errors."""
    def __init__(self, message: str, error_code: int = 0):
        self.error_code = error_code
        super().__init__(f"AquesTalk: {message} (Error: {error_code})")

class AquesTalk:
    """
    Main class for AquesTalk speech synthesis engine.
    
    Converts phoneme strings to speech audio in WAV format.
    """
    
    # Library file names for different platforms
    _LIB_NAMES = {
        'win32': ['AquesTalk.dll', 'AquesTalk1.dll'],
        'linux': ['libAquesTalk.so', 'libAquesTalk1.so'],
        'darwin': ['libAquesTalk.dylib', 'libAquesTalk1.dylib']
    }
    
    # Audio specifications (from header file)
    SAMPLE_RATE = 8000
    BITS_PER_SAMPLE = 16
    CHANNELS = 1
    
    # Speed limits
    MIN_SPEED = 50
    MAX_SPEED = 300
    DEFAULT_SPEED = 100
    
    def __init__(self, lib_path: Optional[str] = None):
        """
        Initialize the AquesTalk synthesizer.
        
        Args:
            lib_path: Optional explicit path to the AquesTalk library.
                     If None, will search in common locations.
        
        Raises:
            AquesTalkError: If initialization fails
        """
        self._lib = None
        self._is_initialized = False
        
        try:
            # Load the library
            self._lib = self._load_library(lib_path)
            
            # Configure function prototypes
            self._configure_functions()
            
            self._is_initialized = True
            
        except Exception as e:
            raise AquesTalkError(f"Failed to initialize: {e}")
    
    def _load_library(self, lib_path: Optional[str] = None) -> ctypes.CDLL:
        """Load the AquesTalk DLL/shared library."""
        if lib_path:
            paths = [lib_path]
        else:
            # Try platform-specific names
            platform = sys.platform
            lib_candidates = self._LIB_NAMES.get(platform, [])
            
            # Search in various locations
            paths = []
            for name in lib_candidates:
                paths.extend([
                    name,  # Current directory
                    os.path.join(os.path.dirname(__file__), name),
                    os.path.join(os.path.dirname(sys.executable), name),
                    os.path.join(os.path.dirname(sys.executable), "lib", name),
                ])
        
        last_error = None
        for path in paths:
            try:
                lib = ctypes.CDLL(path)
                print(f"✓ Loaded AquesTalk library: {path}")
                return lib
            except OSError as e:
                last_error = e
                continue
        
        raise AquesTalkError(
            f"Could not load AquesTalk library. "
            f"Tried: {', '.join(paths)}. "
            f"Last error: {last_error}"
        )
    
    def _configure_functions(self):
        """Configure the DLL function prototypes."""
        # AquesTalk_Synthe (Shift-JIS)
        self._lib.AquesTalk_Synthe.argtypes = [
            ctypes.c_char_p,  # koe (phoneme string, SJIS)
            ctypes.c_int,     # iSpeed
            ctypes.POINTER(ctypes.c_int)  # pSize
        ]
        self._lib.AquesTalk_Synthe.restype = ctypes.POINTER(ctypes.c_ubyte)
        
        # AquesTalk_Synthe_Utf8
        self._lib.AquesTalk_Synthe_Utf8.argtypes = [
            ctypes.c_char_p,  # koe (phoneme string, UTF-8)
            ctypes.c_int,     # iSpeed
            ctypes.POINTER(ctypes.c_int)  # pSize
        ]
        self._lib.AquesTalk_Synthe_Utf8.restype = ctypes.POINTER(ctypes.c_ubyte)
        
        # AquesTalk_Synthe_Utf16
        self._lib.AquesTalk_Synthe_Utf16.argtypes = [
            ctypes.POINTER(ctypes.c_uint16),  # koe (phoneme string, UTF-16)
            ctypes.c_int,     # iSpeed
            ctypes.POINTER(ctypes.c_int)  # pSize
        ]
        self._lib.AquesTalk_Synthe_Utf16.restype = ctypes.POINTER(ctypes.c_ubyte)
        
        # AquesTalk_FreeWave
        self._lib.AquesTalk_FreeWave.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        self._lib.AquesTalk_FreeWave.restype = None
        
        # AquesTalk_SetDevKey
        self._lib.AquesTalk_SetDevKey.argtypes = [ctypes.c_char_p]
        self._lib.AquesTalk_SetDevKey.restype = ctypes.c_int
        
        # AquesTalk_SetUsrKey
        self._lib.AquesTalk_SetUsrKey.argtypes = [ctypes.c_char_p]
        self._lib.AquesTalk_SetUsrKey.restype = ctypes.c_int
    
    def _validate_speed(self, speed: int) -> int:
        """Validate and clamp speed value."""
        if not self.MIN_SPEED <= speed <= self.MAX_SPEED:
            speed = max(self.MIN_SPEED, min(speed, self.MAX_SPEED))
            print(f"Warning: Speed clamped to {speed}%")
        return speed
    
    def _encode_phonemes(self, phonemes: str, encoding: str) -> Union[bytes, ctypes.Array]:
        """Encode phoneme string to specified encoding."""
        encoding = encoding.lower()
        
        if encoding == 'utf-8':
            return phonemes.encode('utf-8')
        
        elif encoding == 'sjis' or encoding == 'shift-jis':
            # Windows Japanese encoding
            try:
                return phonemes.encode('cp932')  # Windows Shift-JIS
            except UnicodeEncodeError:
                return phonemes.encode('shift_jis', errors='ignore')
        
        elif encoding == 'utf-16':
            # Create UTF-16LE array (Windows native)
            encoded = phonemes.encode('utf-16le')
            array_type = ctypes.c_uint16 * (len(encoded) // 2)
            return array_type.from_buffer_copy(encoded)
        
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
    
    def synthesize(self, phonemes: str, encoding: str = 'utf-8', 
                   speed: int = DEFAULT_SPEED) -> AquesAudio:
        """
        Synthesize phoneme string to speech audio.
        
        Args:
            phonemes: Phoneme string to synthesize
            encoding: Encoding of phoneme string ('utf-8', 'utf-16', or 'sjis')
            speed: Speech speed in percent (50-300, default 100)
        
        Returns:
            AquesAudio object containing WAV audio data
        
        Raises:
            AquesTalkError: If synthesis fails
            ValueError: If parameters are invalid
        """
        if not self._is_initialized:
            raise AquesTalkError("Synthesizer not initialized")
        
        if not phonemes:
            raise ValueError("Phoneme string cannot be empty")
        
        # Validate and adjust speed
        speed = self._validate_speed(speed)
        
        # Prepare encoded phonemes
        encoded_phonemes = self._encode_phonemes(phonemes, encoding)
        
        # Variable to receive audio size
        audio_size = ctypes.c_int(0)
        
        # Call appropriate synthesis function based on encoding
        if encoding.lower() == 'utf-8':
            func = self._lib.AquesTalk_Synthe_Utf8
            if isinstance(encoded_phonemes, bytes):
                c_phonemes = ctypes.c_char_p(encoded_phonemes)
            else:
                c_phonemes = ctypes.c_char_p(encoded_phonemes.tobytes())
        
        elif encoding.lower() == 'utf-16':
            func = self._lib.AquesTalk_Synthe_Utf16
            if isinstance(encoded_phonemes, ctypes.Array):
                c_phonemes = encoded_phonemes
            else:
                # Convert bytes to uint16 array
                arr_type = ctypes.c_uint16 * (len(encoded_phonemes) // 2)
                c_phonemes = arr_type.from_buffer_copy(encoded_phonemes)
        
        else:  # Shift-JIS
            func = self._lib.AquesTalk_Synthe
            if isinstance(encoded_phonemes, bytes):
                c_phonemes = ctypes.c_char_p(encoded_phonemes)
            else:
                c_phonemes = ctypes.c_char_p(encoded_phonemes.tobytes())
        
        # Perform synthesis
        audio_ptr = func(c_phonemes, speed, ctypes.byref(audio_size))
        
        # Check for errors
        if audio_ptr is None or audio_size.value <= 0:
            error_code = audio_size.value if audio_size.value < 0 else -1
            raise AquesTalkError("Synthesis failed", error_code)
        
        # Extract audio data
        try:
            # Copy data from C memory
            audio_data = bytes(ctypes.cast(audio_ptr, 
                ctypes.POINTER(ctypes.c_ubyte * audio_size.value)).contents)
            
            # Create audio object
            audio = AquesAudio(
                data=audio_data,
                sample_rate=self.SAMPLE_RATE,
                bits_per_sample=self.BITS_PER_SAMPLE,
                channels=self.CHANNELS
            )
            
            return audio
            
        finally:
            # Always free the memory allocated by C library
            if audio_ptr:
                self._lib.AquesTalk_FreeWave(audio_ptr)
    
    def synthesize_to_file(self, phonemes: str, output_path: str, 
                          encoding: str = 'utf-8', speed: int = DEFAULT_SPEED) -> bool:
        """
        Synthesize phoneme string and save directly to WAV file.
        
        Args:
            phonemes: Phoneme string to synthesize
            output_path: Path to save WAV file
            encoding: Encoding of phoneme string
            speed: Speech speed in percent
        
        Returns:
            True if successful
        
        Raises:
            AquesTalkError: If synthesis or file save fails
        """
        audio = self.synthesize(phonemes, encoding, speed)
        
        try:
            with open(output_path, 'wb') as f:
                # Note: AquesTalk returns raw WAV data including header
                f.write(audio.data)
            return True
            
        except IOError as e:
            raise AquesTalkError(f"Failed to save audio file: {e}")
    
    def set_developer_key(self, key: str) -> bool:
        """
        Set developer license key to remove evaluation limitations.
        
        Args:
            key: Developer license key string
        
        Returns:
            True if key was accepted (may still be invalid internally)
        """
        if not self._is_initialized:
            return False
        
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        result = self._lib.AquesTalk_SetDevKey(ctypes.c_char_p(key_bytes))
        return result == 0
    
    def set_user_key(self, key: str) -> bool:
        """
        Set user license key to change watermark status.
        
        Args:
            key: User license key string
        
        Returns:
            True if key was accepted (may still be invalid internally)
        """
        if not self._is_initialized:
            return False
        
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        result = self._lib.AquesTalk_SetUsrKey(ctypes.c_char_p(key_bytes))
        return result == 0
    
    @property
    def is_initialized(self) -> bool:
        """Check if synthesizer is properly initialized."""
        return self._is_initialized
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Nothing special to clean up
        pass