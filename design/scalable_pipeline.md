# Scalable ASR Pipeline Design — 1 Million Recordings/Month

> **Note for candidate:** This is a starting draft to help you reason about the
> architecture. Read it, understand every component and *why* it's there, then
> rewrite the explanations in your own words before submitting — you'll be asked
> to defend these choices in the interview.

## 1. Scale, in concrete numbers

- 1,000,000 recordings/month → ~33,000/day → ~1,400/hour → ~23/minute on average.
- Real traffic is bursty (peak hours, campaigns), so design for **5-10x average
  burst** (~150-230 recordings/minute at peak), not just the average.
- Assume average clip length ~30-60 seconds → roughly 8,000-16,000 hours of
  audio/month to store and transcribe.

## 2. High-level architecture

```
[Upload Sources]        [Ingestion Layer]         [Processing]              [Storage/Serving]
  Mobile/Web App    →    API Gateway/LB      →   Preprocessing Workers  →   Object Storage (raw + processed)
  Batch Uploads      →    Message Queue        →   Transcription Workers  →   Metadata DB (Postgres)
  IVR/Call Center    →    (Kafka/SQS)           →   (Whisper on GPU pool)   →   Search/Index (Elasticsearch)
                                                                            →   Downstream apps / analytics
```

### Components and why

| Stage | Component | Purpose |
|---|---|---|
| Ingestion | API Gateway + Load Balancer | Accepts uploads, auth, rate limiting |
| Ingestion | Message Queue (Kafka / AWS SQS) | Decouples ingestion from processing; absorbs bursts; enables retries |
| Storage (raw) | Object storage (S3 / GCS) | Cheap, durable storage for original audio files |
| Preprocessing | Autoscaling worker pool (Kubernetes/ECS) | Runs the same validation/conversion pipeline (mono, 16kHz, min-duration filter, metadata extraction) at scale |
| Preprocessing | Dead-letter queue | Captures corrupt/failed files for manual review instead of blocking the pipeline |
| Transcription | GPU worker pool running Whisper (batched inference) | The actual ASR step; GPU pool autoscales based on queue depth |
| Storage (processed) | Object storage + CDN | Stores 16kHz mono WAVs and transcripts |
| Metadata | Relational DB (Postgres) | Tracks file status, durations, sample rates, processing timestamps, transcript IDs |
| Search | Elasticsearch/OpenSearch | Enables full-text search over transcripts |
| Monitoring | Prometheus/Grafana + alerting | Queue depth, worker failure rate, latency SLOs |

## 3. Key design decisions

**Queue-based decoupling.** Ingestion and processing are separated by a message
queue so a traffic spike doesn't overwhelm transcription workers — the queue
buffers the backlog and workers autoscale to drain it.

**Batch inference for cost efficiency.** Whisper (and most modern ASR models)
benefit significantly from batched GPU inference. Group incoming files into
batches (e.g. by queue polling window) rather than processing one at a time,
which improves GPU utilization and reduces cost-per-minute-of-audio.

**Model size trade-off per use case.** Use a smaller/faster Whisper variant
(e.g. `base`/`small`) for near-real-time needs, and larger variants
(`medium`/`large`) for offline/batch jobs where latency matters less but
accuracy does. This can be tier-based on the customer/use case.

**Idempotent, stateless workers.** Each preprocessing/transcription worker
should be stateless and idempotent (safe to retry) — critical at this scale
where some fraction of jobs will always fail transiently.

**Cost control.** At 8,000-16,000 hours/month of audio, GPU transcription
cost dominates. Spot/preemptible GPU instances for the worker pool, combined
with autoscaling to zero during low-traffic hours, meaningfully cuts cost.

**Data lifecycle.** Raw audio can move to cold/archival storage after
processing (e.g. after 30-90 days) since the processed WAV + transcript is
what most downstream consumers need day-to-day.

## 4. Handling failure and edge cases

- Corrupt or unsupported files → routed to a dead-letter queue, logged, and
  optionally alerted rather than crashing the worker.
- Duplicate uploads → deduplicate via content hash (e.g. SHA-256 of the audio)
  before reprocessing.
- Multilingual content → language ID step before transcription to route to
  the right model/config (Whisper supports this natively via language
  detection).
- Backpressure → if queue depth exceeds a threshold, autoscaler adds more
  workers up to a cap; beyond the cap, new uploads are queued with an SLA
  communicated to the client (e.g. "processing within 2 hours").

## 5. Rough monthly cost drivers (things to reason about, not exact numbers)

1. GPU inference hours (transcription) — largest cost, drop with batching + spot instances.
2. Object storage — cheap per GB, but at scale (thousands of hours of audio/month) still worth lifecycle policies.
3. Queue/orchestration infra — typically low relative to compute.
4. Data egress — if transcripts/audio are served to end users frequently, factor in CDN costs.

## 6. What you should be ready to explain in the interview

- Why a queue instead of direct synchronous processing.
- Why batch GPU inference matters for cost/throughput.
- How you'd monitor pipeline health and catch failures early.
- Trade-offs between accuracy (larger Whisper model) and latency/cost
  (smaller model), and how you'd decide which to use where.
- How this design would change if the requirement were real-time streaming
  instead of batch (this connects directly to the offline vs streaming ASR
  research question).
