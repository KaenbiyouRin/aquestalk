#!/usr/bin/env python3
"""
Complete text-to-speech pipeline example.
Combines AqKanji2Koe (text → phoneme) and AquesTalk (phoneme → speech).
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from aqkanji2koe import AqKanji2Koe as TextToPhoneme
    from aquestalk import AquesTalk as PhonemeToSpeech
    HAS_FULL_PIPELINE = True
except ImportError:
    HAS_FULL_PIPELINE = False
    print("Note: Install aqkanji2koe for full text-to-speech pipeline")

def full_text_to_speech():
    """Demonstrate complete text-to-speech pipeline."""
    
    # Configuration
    K2K_DICT_DIR = r"D:\aqk2k_win\aq_dic"
    K2K_DLL_PATH = r"D:\aqk2k_win\lib64\AqKanji2Koe.dll"
    AT_DLL_PATH = r"D:\aqtk1_win\lib64\f1\AquesTalk.dll"
    
    # Japanese texts to synthesize
    japanese_texts = [
        "こんにちは、世界！",
        "ゆっくりしていってね",
        "今日はいい天気ですね",
        "ありがとうございました",
    ]
    
    print("=" * 60)
    print("Complete Text-to-Speech Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Initialize text-to-phoneme converter
        print("\n1. Initializing text-to-phoneme converter...")
        k2k = TextToPhoneme(K2K_DICT_DIR, K2K_DLL_PATH)
        print("   ✓ AqKanji2Koe initialized")
        
        # Step 2: Initialize speech synthesizer
        print("\n2. Initializing speech synthesizer...")
        synth = PhonemeToSpeech(AT_DLL_PATH)
        print("   ✓ AquesTalk initialized")
        
        # Process each text
        for i, text in enumerate(japanese_texts, 1):
            print(f"\n{'='*40}")
            print(f"Processing text {i}: {text}")
            print(f"{'='*40}")
            
            try:
                # Convert text to phonemes
                print("   Converting text to phonemes...")
                phonemes = k2k.convert(text, encoding='utf-8')
                print(f"   Phonemes: {phonemes}")
                
                # Synthesize phonemes to speech
                print("   Synthesizing speech...")
                audio = synth.synthesize(phonemes, speed=100)
                print(f"   Audio: {audio.duration:.2f}s, {len(audio.data):,} bytes")
                
                # Save result
                filename = f"output_{i}.wav"
                from aquestalk import save_wav
                save_wav(filename, audio)
                print(f"   ✓ Saved as: {filename}")
                
                # Optional: Play the audio
                # print("   Playing audio...")
                # from aquestalk import play_audio
                # play_audio(audio)
                
            except Exception as e:
                print(f"   ✗ Failed: {e}")
        
        # Cleanup
        print(f"\n{'='*40}")
        print("Cleaning up resources...")
        k2k.release()
        print("✓ All resources released")
        print(f"{'='*40}")
        
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

def standalone_synthesis():
    """Standalone phoneme-to-speech example."""
    print("\n" + "="*60)
    print("Standalone Phoneme-to-Speech Example")
    print("="*60)
    
    AT_DLL_PATH = r"D:\aqtk1_win\lib64\f1\AquesTalk.dll"
    
    try:
        synth = PhonemeToSpeech(AT_DLL_PATH)
        
        # Common phoneme strings
        phoneme_examples = [
            ("kon'nichiwa", "Hello"),
            ("ohayou", "Good morning"),
            ("konbanwa", "Good evening"),
            ("oyasumi", "Good night"),
        ]
        
        for phonemes, description in phoneme_examples:
            print(f"\n{description}: {phonemes}")
            audio = synth.synthesize(phonemes)
            print(f"  Duration: {audio.duration:.2f}s")
            
            filename = f"{description.replace(' ', '_')}.wav"
            from aquestalk import save_wav
            save_wav(filename, audio)
            print(f"  ✓ Saved: {filename}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    if HAS_FULL_PIPELINE:
        full_text_to_speech()
    else:
        print("Running standalone synthesis demo only")
        standalone_synthesis()