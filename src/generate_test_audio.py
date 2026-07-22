"""
generate_test_audio.py
-----------------------
Generates a folder of synthetic .wav files that mimic a raw, messy dataset
(different sample rates, channels, durations, some too short) so the
preprocessing pipeline can be tested end-to-end without needing to source
real audio first.

This is a TESTING/DEMO utility only. Replace `data/raw/` with your real
10-20 audio files before final submission.

Usage:
    python src/generate_test_audio.py
"""

import os
import numpy as np
import soundfile as sf

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# (filename, duration_seconds, sample_rate, num_channels)
# Includes a mix of "normal" files and edge cases (too short, unusual SR, stereo)
SPECS = [
    ("sample_01.wav", 4.5, 16000, 1),
    ("sample_02.wav", 6.2, 44100, 2),   # stereo, needs mono conversion
    ("sample_03.wav", 1.3, 16000, 1),   # < 2s, should be filtered out
    ("sample_04.wav", 8.0, 22050, 1),   # different sample rate
    ("sample_05.wav", 3.1, 48000, 2),
    ("sample_06.wav", 0.8, 16000, 1),   # < 2s, should be filtered out
    ("sample_07.wav", 5.5, 16000, 1),
    ("sample_08.wav", 7.9, 44100, 1),
    ("sample_09.wav", 2.0, 16000, 1),   # exactly 2s boundary
    ("sample_10.wav", 10.4, 48000, 2),
    ("sample_11.wav", 4.0, 22050, 2),
    ("sample_12.wav", 1.9, 16000, 1),   # just under 2s, should be filtered
    ("sample_13.wav", 6.7, 44100, 1),
    ("sample_14.wav", 3.3, 16000, 1),
    ("sample_15.wav", 9.1, 22050, 2),
]


def make_tone(duration, sr, channels, freq=220.0):
    """Generate a simple sine tone with a touch of noise, like a synthetic 'voice' clip."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    tone = 0.3 * np.sin(2 * np.pi * freq * t)
    noise = 0.02 * np.random.randn(len(t))
    signal = tone + noise
    if channels == 2:
        signal = np.stack([signal, signal * 0.9], axis=1)
    return signal.astype(np.float32)


def main():
    print(f"Generating {len(SPECS)} synthetic test audio files in '{RAW_DIR}/' ...")
    for fname, dur, sr, ch in SPECS:
        audio = make_tone(dur, sr, ch, freq=200 + np.random.randint(0, 200))
        path = os.path.join(RAW_DIR, fname)
        sf.write(path, audio, sr)
        print(f"  {fname:15s}  dur={dur:5.1f}s  sr={sr:6d}Hz  channels={ch}")
    print("\nDone. These are synthetic placeholders — replace data/raw/ with your")
    print("real 10-20 audio files before final submission.")


if __name__ == "__main__":
    main()
