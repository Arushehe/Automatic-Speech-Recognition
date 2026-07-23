# Scalable ASR Pipeline Design — 1 Million Recordings/Month

## Overview
The preprocessing pipeline was specifically made for this project as it works well for a small number of audio files. However, processing around one million recordings every month requires a scalable architecture. Instead of relying on a single machine, the workload have to be distributed across multiple services so that uploading, preprocessing, and transcription can happen simultaneously.

### Estimated Workload
1,000,000 recordings per month
Around 33,000 recordings per day
Around 1,400 recordings per hour
Around 23 recordings per minute on average
Since traffic is not always uniform, the system should also be able to handle sudden spikes in uploads.

## Architecture

```
Users
   │
   ▼
Upload API
   │
   ▼
Load Balancer
   │
   ▼
Object Storage (Amazon S3)
   │
   ▼
Message Queue (Kafka / RabbitMQ / AWS SQS)
   │
   ▼
Preprocessing Workers
(Duration Check → Mono → 16 kHz → Metadata)
   │
   ▼
Processed Audio Storage
   │
   ▼
Whisper GPU Workers
   │
   ▼
PostgreSQL Database
   │
   ▼
Application / Dashboard
```
---

## Components

### 1. Upload API
The Upload API part receives audio files from users. It performs basic validation and uploads the files to cloud storage before further processing begins.

### 2. Load Balancer
A load balancer distributes incoming requests across multiple servers. This prevents a single server from becoming overloaded when many users upload files simultaneously.

### 3. Object Storage
The uploaded audio files are stored in object storage such as Amazon S3. Object storage is suitable because audio files are large, cost-effective to store, and can be accessed easily by different processing services whenever needed.

### 4. Message Queue
Instead of processing every uploaded file immediately, a message which contains the file's location is added to the queue. The queue temporarily stores incoming requests until a worker becomes available. This prevents the system from slowing down during periods of heavy traffic.

### 5. Preprocessing Workers
Multiple preprocessing workers process files from the queue simultaneously.
Each worker performs the following steps:
Read audio metadata
Check audio duration
Remove files shorter than 2 seconds
Convert stereo audio to mono
Resample audio to 16 kHz
Generate metadata
Save the processed WAV file
Since multiple workers can run at the same time, the overall processing speed increases significantly.

### 6. Processed Audio Storage
After preprocessing, all converted audio files are stored separately. Because every file now follows the same consistent format, they are ready to be sent to the ASR model for transcription.

### 7. Whisper GPU Workers
GPU-enabled servers load the Whisper model and perform speech to text transcription. Running multiple Whisper workers allows many recordings to be transcribed in parallel, reducing the overall processing time.

### 8. PostgreSQL Database
The database stores important information such as:
Filename
Processing status
Duration
Sample rate
Processing timestamp
Transcript
From this its easy to track each recording and retrieve the transcription later.

### 9. Dashboard / API
The dashboard allows users to check the processing status, view transcripts, and download transcription results.

## Key Design Decisions

### Queue-Based Processing
Instead of sending every uploaded file directly for preprocessing, the system first places the file information into a message queue. This allows the upload service and the processing service to work independently. Even if many users upload files at the same time, the queue stores the requests until workers are available, ny doing this it prevents the system from becoming overloaded.

### Multiple Preprocessing Workers
Instead of using a single preprocessing service, multiple workers process audio files simultaneously. Since each worker performs the same preprocessing steps independently, more workers can be added whenever the workload increases. This helps improve processing speed and makes the system more scalable.

### GPU-Based Whisper Inference
Speech recognition models like Whisper require significant computational power. Using GPU workers instead of CPUs allows multiple audio recordings to be transcribed much faster, reducing the overall processing time.

### Separate Storage for Audio and Metadata
Audio files are stored in object storage, while metadata and transcription details are stored in a relational database. This difference storage pattern makes it easier to manage large audio files while allowing quick access to information such as processing status, duration, timestamps, and transcripts.

### Independent Services
The upload service, preprocessing service, and transcription service are designed to work independently. If one service requires more resources, it can be scaled without affecting the others. This makes the system easier to maintain and better suited for handling a large number of recordings.

## Possible Challenges
Some common challenges that may occur are:
Corrupted or unsupported audio files
Duplicate uploads
Large traffic spikes
Long processing queues
GPU availability during peak hours

## Future Improvements
Basic improvements:
Voice Activity Detection (VAD) to remove silence before transcription.
Automatic language detection for multilingual audio.
Parallel preprocessing for faster execution.
Docker and Kubernetes for easier deployment and scaling.
Monitoring tools for tracking worker health and processing time.

## Conclusion
The proposed architecture separates uploading, preprocessing, storage, and transcription into different stages. Since each stage can be scaled independently, the system can efficiently process around one million recordings every month while maintaining reliable performance.
---
