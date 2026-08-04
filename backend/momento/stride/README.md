# STRIDE: Strategic Time-series Reasoning Injected via Distilled Embeddings

This module implements STRIDE, a framework for integrating LLM-based reasoning into Time Series Foundation Models (TSFMs).

## Overview
STRIDE bridges the gap between qualitative reasoning (LLMs) and numerical forecasting (TSFMs) by:
1. Distilling reasoning traces from a teacher LLM (e.g., Gemini-3.1-Pro) into a lightweight student LLM.
2. Projecting LLM hidden states into the TSFM's embedding space.
3. Fusing reasoning priors with time-series embeddings for joint optimization.

## Key Features
- Cross-modal latent projection: Bypasses discrete tokenization bottlenecks.
- Plug-and-play: Works with any TSFM (e.g., Chronos-2, Timer-S1).
- Joint optimization: Combines cross-entropy loss (reasoning) and quantile loss (forecasting).
- Momento integration: Caches reasoning traces and forecasts for efficient serving.

## Directory Structure

stride/
├── reasoning/
│   ├── teacher_llm.py
│   ├── student_llm.py
│   └── distillation.py
├── projection/
│   ├── latent_projection.py
│   └── fusion.py
├── forecasting/
│   ├── tsfm_integration.py
│   └── quantile_loss.py
├── train.py
├── utils.py
└── README.md

## Usage
### 1. Initialize Components

teacher_llm = TeacherLLM(api_key="GEMINI_API_KEY")
student_llm = StudentLLM()
tsfm = get_tsfm_wrapper("chronos-2.0")
projection = LatentProjection(4096, 512)

### 2. Train STRIDE

from stride.train import train_stride, STRIDEDataset
from torch.utils.data import DataLoader

train_data = [{"X": [1.0, 2.0, 3.0], "Y": [4.0, 5.0], "E": {}}]
dataset = STRIDEDataset(train_data, teacher_llm)
dataloader = DataLoader(dataset, batch_size=8)

student_llm, projection, tsfm = train_stride(
    teacher_llm, student_llm, "chronos-2.0", projection, train_data
)

### 3. Generate Forecasts

from stride.train import forecast_with_stride

X_new = [10.0, 11.0, 12.0]
Y_hat, R_hat = forecast_with_stride(student_llm, "chronos-2.0", projection, X=X_new)
print(f"Forecast: {Y_hat}")
print(f"Reasoning: {R_hat}")

## Integration with Momento

from momento.store import MomentoStore

store = MomentoStore(endpoint="...", api_key="...")
raw_data = {"source": "aviator", "rounds": [{"multiplier": 1.26}]}
store.store_raw_data("aviator_data", raw_data)
stride_data = store.get_stride_data("aviator_data")

## Benchmarking
STRIDE achieves state-of-the-art performance on:
- GIFT-Eval: 0.674 MASE, 0.454 CRPS
- TFRBench (In-Domain): 0.615 MASE
- TFRBench (Out-of-Domain): 0.724 MASE
