# Audio Preprocessing Pipeline for ASR

## Overview
This project was developed as part of the VIH Labs AI Intern Assignment (Track A – Automatic Speech Recognition).
The main objective of this project is to preprocess raw audio files before using them by an ASR model like Whisper. Since audio recordings can come from different devices and formats, the pipeline converts them into a consistent format suitable for speech recognition.

For every audio file, the pipeline:
reads basic audio information such as duration, sample rate, channels and file size.
removes recordings shorter than 2 seconds.
converts stereo audio to mono.
resamples audio to 16 kHz.
saves the processed audio in WAV format.
generates a metadata CSV containing details of every processed file.

## Project Structure
```
.
├── README.md
├── requirements.txt
├── Dockerfile
├── research/
│   └── research_outline.md      # final research.pdf written separately
├── design/
│   └── scalable_pipeline.md     # system design for 1M recordings/month
├── src/
│   ├── generate_test_audio.py   # creates synthetic test audio (demo/testing only)
│   ├── preprocess.py            # main preprocessing pipeline
│   └── test_preprocess.py       # unit tests (bonus)
├── data/
│   └── raw/                     # 10-20 audio files are here
└── results/
    ├── metadata.csv             # generated output
    └── processed/               # generated output (converted WAVs)
```
---

## Installation

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Project

### 1. Adding the audio files

Place the audio files inside `data/raw/` folder.

Supported formats
wav
mp3
flac
m4a
ogg

If real audio files are not available, the synthetic audio generator can be used to test the pipeline.

### 2. Run 
```bash
python src/preprocess.py --input data/raw --output results/processed --metadata results/metadata.csv --min-duration 2.0
```

Optional flags:
- `--min-duration` — minimum duration in seconds (default 2.0)
- `--target-sr` — target sample rate (default 16000)

### 3. Output
After execution,
processed audio files are saved inside `results/processed/`.

A metadata.csv file is also generated containing
filename
duration
sample rate
channels
processing status
reason for removal (if any)

### 4. Run tests (bonus)
```bash
python -m pytest src/test_preprocess.py -v
```

### 5. Run with Docker (bonus)
```bash
docker build -t asr-preprocess .
docker run -v $(pwd)/results:/app/results asr-preprocess
```

## Assumptions
Audio shorter than 2 seconds is not processed but is still included in the metadata CSV.
Stereo recordings are converted to mono before resampling.
All processed audio is saved as 16 kHz PCM WAV.
Audio files which are exactly 2 seconds long are kept.

## Observations
While testing the pipeline, I found that the audio files had different sample rates and channel configurations, as I took 19 audio file samples in which only 16 were accepted and 3 were removed according to their duration then, after preprocessing, all accepted files were converted into a uniform format (mono, 16 kHz WAV), making them ready for transcription.
The metadata CSV also made it easier to identify removed files and verify that preprocessing worked correctly.

## References
OpenAI Whisper paper: https://arxiv.org/abs/2212.04356
Whisper GitHub repo: https://github.com/openai/whisper
Librosa Documentation: https://librosa.org/doc/latest/

## Why this preprocessing?
Speech recordings collected from different sources often have different formats, sampling rates and channel configurations. Instead of sending every file directly to an ASR model, converting them into a common format makes preprocessing consistent and reduces issues during transcription.
This pipeline prepares the audio in a format that can be directly used by speech recognition models such as "Whisper".

## Pipeline Workflow
```
Raw Audio
    │
    ▼
Read Metadata
    │
    ▼
Duration Check
    │
    ▼
Mono Conversion
    │
    ▼
16 kHz Resampling
    │
    ▼
Save Processed Audio
    │
    ▼
Generate Metadata CSV
```

# Author
  **Arushi**
  B.Tech Civil Engineering, IIT Guwahati
  Aspiring AI Engineer | Data Science Enthusiast
