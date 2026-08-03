# MomentoFresh with STRIDE Integration

This repository implements **STRIDE (Strategic Time-series Reasoning Injected via Distilled Embeddings)** on the **Momento platform** for reasoning-aware time-series forecasting.

## Overview

**STRIDE** enhances Time Series Foundation Models (TSFMs) with **LLM-based reasoning** to improve forecasting accuracy and interpretability. This implementation integrates STRIDE with the **Momento caching platform** for efficient data storage and retrieval.

### Key Features
- Cross-modal latent projection: Injects LLM reasoning into TSFM embeddings.
- Plug-and-play: Works with multiple TSFMs (Chronos-2, Timer-S1).
- Joint optimization: Combines reasoning and numerical forecasting losses.
- Momento integration: Caches reasoning traces and forecasts for low-latency serving.

## Repository Structure

MomentoFresh/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   └── momento/
│       ├── __init__.py
│       ├── store.py
│       ├── forecast.py
│       └── stride/
│           ├── __init__.py
│           ├── utils.py
│           ├── reasoning/
│           │   ├── __init__.py
│           │   ├── teacher_llm.py
│           │   ├── student_llm.py
│           │   └── distillation.py
│           ├── projection/
│           │   ├── __init__.py
│           │   ├── latent_projection.py
│           │   └── fusion.py
│           ├── forecasting/
│           │   ├── __init__.py
│           │   ├── tsfm_integration.py
│           │   └── quantile_loss.py
│           ├── train.py
│           └── README.md

## Installation

### 1. Clone the Repository

git clone https://github.com/avfsmomentoserver-cell/MomentoFresh.git
cd MomentoFresh

### 2. Install Dependencies

cd backend
pip install -r requirements.txt

## Quick Start

### 1. Set Up API Keys
Create a .env file in the backend/ directory:

GEMINI_API_KEY="your-gemini-api-key"
MOMENTO_API_KEY="your-momento-api-key"
MOMENTO_ENDPOINT="your-momento-endpoint"

### 2. Run a Forecast with STRIDE

from momento.stride import ForecastEngine
import os

engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

X = [1.0, 2.0, 3.0, 4.0, 5.0]
E = {"holiday": "Christmas"}
Y_hat, R_hat = engine.forecast(X, E=E, use_reasoning=True)
print(f"Forecast: {Y_hat}")
print(f"Reasoning: {R_hat}")

## Momento Data Integration

### Example Data Format

{
  "source": "aviator",
  "collectedAt": "2026-08-02T19:42:22.096Z",
  "rounds": [
    {
      "timestamp": "2026-08-02T19:42:22.096Z",
      "multiplier": 1.26,
      "color": "rgb(52, 180, 255)",
      "source": "aviator"
    }
  ]
}

### Usage with Momento

from momento.store import MomentoStore
from momento.stride import ForecastEngine

store = MomentoStore(
    endpoint=os.getenv("MOMENTO_ENDPOINT"),
    api_key=os.getenv("MOMENTO_API_KEY"),
)

raw_data = {
    "source": "aviator",
    "collectedAt": "2026-08-02T19:42:22.096Z",
    "rounds": [{"timestamp": "...", "multiplier": 1.26, "source": "aviator"}]
}
store.store_raw_data("aviator_data", raw_data)

engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

result = engine.forecast_from_momento("aviator_data", use_reasoning=True)
print(f"Forecast: {result['forecast']}")
print(f"Reasoning: {result['reasoning']}")

## Training STRIDE

### 1. Prepare Training Data

train_data = [
    {"X": [1.0, 2.0, 3.0], "Y": [4.0, 5.0], "E": {"holiday": "Christmas"}},
    {"X": [5.0, 6.0, 7.0], "Y": [8.0, 9.0], "E": {}},
]

### 2. Train the Model

engine.train(
    train_data=train_data,
    epochs=10,
    alpha=0.5,
    beta=0.5,
    learning_rate=1e-4,
    batch_size=8,
)

engine.save_model("stride_model")

## Benchmarking

| Dataset | Metric | STRIDE (+Chronos-2) | Baseline | Improvement |
|---------|--------|---------------------|----------|-------------|
| GIFT-Eval | MASE | 0.674 | 0.693 | +2.7% |
| GIFT-Eval | CRPS | 0.454 | 0.485 | +6.4% |
| TFRBench (In-Domain) | MASE | 0.615 | 0.765 | +20% |
| TFRBench (Out-of-Domain) | MASE | 0.724 | 0.778 | +7% |

## Contributing
1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Commit your changes (git commit -m "Add your feature").
4. Push to the branch (git push origin feature/your-feature).
5. Open a Pull Request.

## License
This project is licensed under the MIT License.
