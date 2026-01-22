#!/usr/bin/env python3
"""
Audio Transcription Script using OpenAI Whisper
Transcribes an audio file and saves the transcript to a text file.
"""

import whisper
import sys
import os
from pathlib import Path


def transcribe_audio(audio_path, model_size="base"):
    """
    Transcribe an audio file using Whisper.
    
    Args:
        audio_path: Path to the audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        Transcript text
    """
    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path)
    
    return result["text"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [model_size]")
        print("Model sizes: tiny, base, small, medium, large (default: base)")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        sys.exit(1)
    
    # Get output filename
    audio_file = Path(audio_path)
    output_path = audio_file.with_suffix('.txt')
    
    try:
        # Transcribe
        transcript = transcribe_audio(audio_path, model_size)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        print(f"\nTranscription complete!")
        print(f"Saved to: {output_path}")
        print(f"\nTranscript preview:")
        print("-" * 50)
        print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()