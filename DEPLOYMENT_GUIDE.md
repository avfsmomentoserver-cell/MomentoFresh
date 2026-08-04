
#### 2.4 Install Azure CLI (Optional)
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

---

### Step 3: Clone the Repository

```bash
git clone https://github.com/avfsmomentoserver-cell/MomentoFresh.git
cd MomentoFresh
git checkout feature/stride-integration
```

---

### Step 4: Set Up Environment

#### 4.1 Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4.2 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 4.3 Configure Environment Variables
```bash
nano backend/.env
```
Add:
```ini
MOMENTO_API_KEY=your-momento-api-key
MOMENTO_ENDPOINT=your-cache-endpoint.momentohq.com
GEMINI_API_KEY=your-gemini-api-key
```

---

### Step 5: Run STRIDE Locally

#### 5.1 Test the Forecasting Engine
Create test_stride.py:
```python
from momento.stride import ForecastEngine
import os
from dotenv import load_dotenv

load_dotenv()

engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

X = [1.25, 1.30, 1.28, 1.35, 1.40]
E = {"source": "aviator"}

print("Generating forecast with STRIDE...")
Y_hat, R_hat = engine.forecast(X, E=E, use_reasoning=True)
print(f"Forecast: {Y_hat}")
print(f"Reasoning: {R_hat}")
```
Run:
```bash
python test_stride.py
```

#### 5.2 Test with Momento
Create test_momento.py:
```python
from momento.store import MomentoStore
from momento.stride import ForecastEngine
import os
from dotenv import load_dotenv

load_dotenv()

store = MomentoStore(
    endpoint=os.getenv("MOMENTO_ENDPOINT"),
    api_key=os.getenv("MOMENTO_API_KEY"),
)

aviator_data = {
    "source": "aviator",
    "collectedAt": "2026-08-04T12:00:00.000Z",
    "rounds": [
        {"timestamp": "2026-08-04T12:00:00.000Z", "multiplier": 1.25},
        {"timestamp": "2026-08-04T13:00:00.000Z", "multiplier": 1.30},
    ]
}
store.store_raw_data("aviator_test", aviator_data)

engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

result = engine.forecast_from_momento("aviator_test", use_reasoning=True)
print(f"Forecast: {result["forecast"]}")
print(f"Reasoning: {result["reasoning"]}")
```
Run:
```bash
python test_momento.py
```
