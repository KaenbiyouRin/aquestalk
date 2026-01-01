#!/usr/bin/env python3
"""
Basic AquesTalk speech synthesis example.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aquestalk import AquesTalk, save_wav, play_audio

def main():
    """Demonstrate basic speech synthesis."""
    
    # Configuration
    LIB_PATH = r"D:\aqk2k_win\lib64\AquesTalk.dll"  # Update this path
    
    # Phoneme strings for testing
    test_phonemes = [
        ("utf-8", "kon'nichiwa"),  # こんにちは
        ("utf-8", "arigatou"),     # ありがとう
        ("utf-8", "sayounara"),    # さようなら
        ("sjis", "おはよう"),        # おはよう (Shift-JIS)
    ]
    
    try:
        print("=" * 60)
        print("AquesTalk Speech Synthesis Demo")
        print("=" * 60)
        
        # Initialize synthesizer
        synth = AquesTalk(LIB_PATH)
        print(f"✓ Synthesizer initialized: {synth.is_initialized}")
        
        # Test different speeds
        speeds = [80, 100, 150, 200]
        
        for encoding, phonemes in test_phonemes:
            print(f"\n{'='*40}")
            print(f"Phonemes: {phonemes} ({encoding})")
            print(f"{'='*40}")
            
            for speed in speeds:
                try:
                    print(f"\n  Speed: {speed}%")
                    
                    # Synthesize
                    audio = synth.synthesize(phonemes, encoding=encoding, speed=speed)
                    
                    # Display info
                    info = {
                        'Duration': f"{audio.duration:.2f}s",
                        'Data size': f"{len(audio.data):,} bytes",
                        'Sample rate': f"{audio.sample_rate} Hz",
                    }
                    
                    for key, value in info.items():
                        print(f"    {key}: {value}")
                    
                    # Save to file
                    filename = f"output_{encoding}_{speed}.wav"
                    save_wav(filename, audio)
                    print(f"    Saved: {filename}")
                    
                    # Optional: Play audio
                    # if speed == 100:  # Only play normal speed
                    #     print("    Playing...")
                    #     play_audio(audio, block=True)
                    
                except Exception as e:
                    print(f"    ✗ Failed: {e}")
        
        # Direct save example
        print(f"\n{'='*40}")
        print("Direct file save example")
        print(f"{'='*40}")
        
        output_file = "direct_output.wav"
        if synth.synthesize_to_file("konbanwa", output_file, speed=120):
            print(f"✓ Direct save successful: {output_file}")
        
        print(f"\n{'='*40}")
        print("Demo completed successfully!")
        print(f"{'='*40}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()