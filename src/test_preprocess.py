"""
test_preprocess.py
-------------------
Basic unit tests for the preprocessing pipeline (bonus item requested in
the assignment). Uses synthetic in-memory audio so it doesn't depend on
any external files.

Usage:
    python -m pytest src/test_preprocess.py -v
"""

import os
import shutil
import tempfile

import numpy as np
import soundfile as sf
import pytest

from preprocess import process_file, run_pipeline, TARGET_SR


@pytest.fixture
def temp_dirs():
    input_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    yield input_dir, output_dir
    shutil.rmtree(input_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)


def make_wav(path, duration, sr, channels=1):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    signal = 0.3 * np.sin(2 * np.pi * 220 * t)
    if channels == 2:
        signal = np.stack([signal, signal], axis=1)
    sf.write(path, signal.astype(np.float32), sr)


def test_short_file_is_removed(temp_dirs):
    input_dir, output_dir = temp_dirs
    path = os.path.join(input_dir, "short.wav")
    make_wav(path, duration=1.0, sr=16000)  # below default 2s threshold

    result = process_file(path, output_dir, min_duration=2.0, target_sr=TARGET_SR)
    assert result["status"] == "removed"
    assert result["processed_filename"] == ""


def test_long_file_is_kept_and_converted(temp_dirs):
    input_dir, output_dir = temp_dirs
    path = os.path.join(input_dir, "long.wav")
    make_wav(path, duration=5.0, sr=44100, channels=2)  # stereo, non-target SR

    result = process_file(path, output_dir, min_duration=2.0, target_sr=TARGET_SR)
    assert result["status"] == "kept"
    assert result["processed_sample_rate"] == TARGET_SR
    assert result["processed_channels"] == 1

    out_path = os.path.join(output_dir, result["processed_filename"])
    info = sf.info(out_path)
    assert info.samplerate == TARGET_SR
    assert info.channels == 1


def test_boundary_duration_is_kept(temp_dirs):
    """A file exactly at the minimum duration should be kept (>=, not >)."""
    input_dir, output_dir = temp_dirs
    path = os.path.join(input_dir, "boundary.wav")
    make_wav(path, duration=2.0, sr=16000)

    result = process_file(path, output_dir, min_duration=2.0, target_sr=TARGET_SR)
    assert result["status"] == "kept"


def test_pipeline_writes_metadata_csv(temp_dirs):
    input_dir, output_dir = temp_dirs
    make_wav(os.path.join(input_dir, "a.wav"), duration=3.0, sr=16000)
    make_wav(os.path.join(input_dir, "b.wav"), duration=1.0, sr=16000)

    metadata_csv = os.path.join(output_dir, "metadata.csv")
    run_pipeline(input_dir, os.path.join(output_dir, "processed"),
                 metadata_csv, min_duration=2.0, target_sr=TARGET_SR)

    assert os.path.exists(metadata_csv)
    with open(metadata_csv) as f:
        content = f.read()
    assert "a.wav" in content and "b.wav" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
