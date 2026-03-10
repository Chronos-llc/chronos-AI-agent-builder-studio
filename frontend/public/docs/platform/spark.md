---
sidebar_position: 4
title: Spark Platform
---

# Spark Platform

Spark is Chronos Studio's high-performance compute platform designed for training custom models and running large-scale inference.

## Overview

Spark provides:
- Distributed training
- Large-scale inference
- Custom model fine-tuning
- Model registry

## Capabilities

### Training

- **Distributed Training**: Multi-GPU, multi-node
- **Fine-tuning**: Adapt base models
- **Hyperparameter Tuning**: Automated optimization
- **Experiment Tracking**: Full training history

### Inference

- **Batch Processing**: High throughput
- **Real-time**: Low latency
- **Streaming**: Continuous processing
- **Batching**: Cost optimization

## Getting Started

### Setup

```bash
# Install Spark CLI
pip install chronos-spark

# Configure
chronos-spark config \
  --project your-project \
  --region us-east-1
```

## Training Models

### Configuration

```yaml
# training.yaml
name: custom-support-model
base_model: gpt-4

training:
  dataset: s3://your-bucket/datasets/support/
  validation: s3://your-bucket/datasets/support-valid/
  
  compute:
    nodes: 4
    gpus_per_node: 8
    instance_type: p4d.24xlarge
    
  hyperparameters:
    learning_rate: 1e-5
    batch_size: 32
    epochs: 3
    warmup_steps: 100
    
  output:
    model: s3://your-bucket/models/support-v1/
    checkpoints: s3://your-bucket/checkpoints/
```

### Launch Training

```bash
chronos-spark train training.yaml
```

### Monitor Training

```bash
# View progress
chronos-spark status training-run-123

# Stream metrics
chronos-spark metrics training-run-123 --follow

# TensorBoard
chronos-spark tensorboard training-run-123
```

## Fine-tuning

### Quick Fine-tune

```bash
chronos-spark fine-tune \
  --base-model gpt-4 \
  --dataset s3://bucket/dataset.jsonl \
  --output-model s3://bucket/fine-tuned/
```

### Custom Configuration

```python
from chronos.spark import FineTuner

tuner = FineTuner(
    base_model="gpt-4",
    dataset="s3://bucket/training.jsonl",
    config={
        "learning_rate": 5e-6,
        "epochs": 2,
        "lora_r": 16,  # LoRA configuration
        "lora_alpha": 32
    }
)

job = tuner.launch()
job.wait()
```

## Inference

### Batch Inference

```bash
chronos-spark inference batch \
  --model s3://bucket/model/ \
  --input s3://bucket/input.jsonl \
  --output s3://bucket/output.jsonl \
  --batch_size 100
```

### Real-time Inference

```python
from chronos.spark import InferenceEndpoint

endpoint = InferenceEndpoint(
    model="s3://bucket/model/",
    instance_type="g4dn.xlarge",
    min_replicas=1,
    max_replicas=10,
    auto_scaling=True
)

endpoint.deploy()

# Query
response = endpoint.predict({
    "prompt": "Your question here"
})
```

## Model Registry

### Managing Models

```bash
# List models
chronos-spark models list

# Upload model
chronos-spark models upload ./model/ --name my-model

# Version model
chronos-spark models version my-model --version 2.0.0

# Set default
chronos-spark models set-default my-model --version 2.0.0
```

### Model Metadata

```yaml
# model.yaml
name: support-model-v2
version: 2.0.0
framework: pytorch
architecture: gpt
parameters: 7B
fine_tuned_from: gpt-4

metadata:
  training_data: support-corpus-v2
  accuracy: 0.94
  eval_scores:
    precision: 0.92
    recall: 0.91
    f1: 0.915
```

## Cost Optimization

### Spot Instances

```yaml
compute:
  instance_type: p4d.24xlarge
  capacity_type: spot  # 60-70% savings
  instance_distribution:
    - p4d.24xlarge
    - p3dn.24xlarge
```

### Spot Recovery

```yaml
spot:
  recovery_strategy: retry_then_spot
  max_retry_minutes: 10
  fallback_instance: on_demand
```

## Troubleshooting

### Training Issues

**Out of Memory**
- Reduce batch size
- Enable gradient checkpointing
- Use mixed precision

**Slow Training**
- Increase GPU count
- Optimize data loading
- Check data pipeline

### Inference Issues

**High Latency**
- Enable caching
- Optimize batch size
- Use smaller model

**Cost High**
- Enable auto-scaling
- Use spot instances
- Optimize batching
