"""
preprocess.py
-------------
ASR Data Preprocessing Pipeline (Track A - Practical, 40%)

For every audio file in the input directory, this script:
  1. Reads and reports duration, sample rate, and file size.
  2. Converts the file to mono, 16kHz WAV.
  3. Filters out (excludes) any file shorter than MIN_DURATION_SEC.
  4. Writes a metadata CSV summarizing every file (before/after stats).

Usage:
    python src/preprocess.py --input data/raw --output results/processed --min-duration 2.0

Author: <your name>
"""

import os
import argparse
import csv
from pathlib import Path

import librosa
import soundfile as sf

TARGET_SR = 16000
MIN_DURATION_SEC_DEFAULT = 2.0
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}


def get_file_size_kb(path: str) -> float:
    return round(os.path.getsize(path) / 1024, 2)


def process_file(filepath: str, output_dir: str, min_duration: float, target_sr: int):
    """
    Loads a single audio file, computes original stats, converts to mono/target_sr,
    filters by minimum duration, and writes the processed file if it passes.

    Returns a dict of metadata for the CSV row.
    """
    filename = os.path.basename(filepath)
    original_size_kb = get_file_size_kb(filepath)

    # sr=None preserves the original sample rate for reporting purposes
    audio, orig_sr = librosa.load(filepath, sr=None, mono=False)

    # Determine original channel count before forcing mono
    orig_channels = 1 if audio.ndim == 1 else audio.shape[0]
    orig_duration = librosa.get_duration(y=audio, sr=orig_sr)

    status = "kept"
    reason = ""
    processed_path = ""
    new_duration = orig_duration
    new_size_kb = None

    if orig_duration < min_duration:
        status = "removed"
        reason = f"duration {orig_duration:.2f}s < min {min_duration}s"
    else:
        # Convert to mono (average channels) then resample to target_sr
        mono_audio = librosa.to_mono(audio) if orig_channels > 1 else audio
        resampled = librosa.resample(mono_audio, orig_sr=orig_sr, target_sr=target_sr) \
            if orig_sr != target_sr else mono_audio

        os.makedirs(output_dir, exist_ok=True)
        out_name = Path(filename).stem + ".wav"
        processed_path = os.path.join(output_dir, out_name)
        sf.write(processed_path, resampled, target_sr, subtype="PCM_16")

        new_duration = librosa.get_duration(y=resampled, sr=target_sr)
        new_size_kb = get_file_size_kb(processed_path)

    return {
        "filename": filename,
        "original_duration_sec": round(orig_duration, 2),
        "original_sample_rate": orig_sr,
        "original_channels": orig_channels,
        "original_size_kb": original_size_kb,
        "status": status,
        "reason": reason,
        "processed_filename": os.path.basename(processed_path) if processed_path else "",
        "processed_duration_sec": round(new_duration, 2) if status == "kept" else "",
        "processed_sample_rate": target_sr if status == "kept" else "",
        "processed_channels": 1 if status == "kept" else "",
        "processed_size_kb": new_size_kb if new_size_kb else "",
    }


def run_pipeline(input_dir: str, output_dir: str, metadata_csv: str,
                  min_duration: float, target_sr: int):
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    audio_files = sorted([
        f for f in input_path.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not audio_files:
        print(f"No supported audio files found in {input_dir}")
        return

    print(f"Found {len(audio_files)} audio file(s). Processing...\n")

    rows = []
    kept, removed = 0, 0
    for f in audio_files:
        try:
            row = process_file(str(f), output_dir, min_duration, target_sr)
            rows.append(row)
            if row["status"] == "kept":
                kept += 1
                print(f"  [KEPT]    {row['filename']:20s} "
                      f"{row['original_duration_sec']:6.2f}s -> {row['processed_duration_sec']:6.2f}s  "
                      f"{row['original_sample_rate']:6d}Hz -> {row['processed_sample_rate']}Hz")
            else:
                removed += 1
                print(f"  [REMOVED] {row['filename']:20s} reason: {row['reason']}")
        except Exception as e:
            print(f"  [ERROR]   {f.name}: {e}")
            rows.append({
                "filename": f.name, "original_duration_sec": "", "original_sample_rate": "",
                "original_channels": "", "original_size_kb": "", "status": "error",
                "reason": str(e), "processed_filename": "", "processed_duration_sec": "",
                "processed_sample_rate": "", "processed_channels": "", "processed_size_kb": "",
            })

    os.makedirs(os.path.dirname(metadata_csv), exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(metadata_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSummary: {kept} kept, {removed} removed, {len(rows) - kept - removed} errors")
    print(f"Metadata written to: {metadata_csv}")
    print(f"Processed audio written to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="ASR audio preprocessing pipeline")
    parser.add_argument("--input", default="data/raw", help="Directory of raw audio files")
    parser.add_argument("--output", default="results/processed", help="Directory for processed WAVs")
    parser.add_argument("--metadata", default="results/metadata.csv", help="Path to output metadata CSV")
    parser.add_argument("--min-duration", type=float, default=MIN_DURATION_SEC_DEFAULT,
                         help="Minimum duration in seconds; shorter files are excluded")
    parser.add_argument("--target-sr", type=int, default=TARGET_SR,
                         help="Target sample rate for conversion")
    args = parser.parse_args()

    run_pipeline(args.input, args.output, args.metadata, args.min_duration, args.target_sr)


if __name__ == "__main__":
    main()
