FROM python:3.11-slim

# System dependency needed by librosa/soundfile for audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

# Default: generate synthetic test audio, then run the preprocessing pipeline
CMD ["sh", "-c", "python src/generate_test_audio.py && python src/preprocess.py --input data/raw --output results/processed --metadata results/metadata.csv"]
