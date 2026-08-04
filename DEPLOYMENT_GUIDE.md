# STRIDE + Momento Deployment Guide

## 📋 Overview

This guide provides **step-by-step instructions** for deploying the **STRIDE + Momento** integration in two environments:

1. **☁️ Cloud Deployment** (Recommended for production)
2. **🖥️ Debian VM on Azure** (For development/testing)

---

## 🎯 Prerequisites

### **1. Required Accounts & Keys**
| Service | Purpose | How to Get |
|---------|---------|------------|
| **GitHub** | Code repository | [Sign Up](https://github.com/) |
| **Momento** | Caching platform | [Sign Up](https://console.gomomento.com/) |
| **Google Cloud (Gemini API)** | Teacher LLM (Gemini-3.1-Pro) | [Get API Key](https://ai.google.dev/) |
| **Azure** | Cloud deployment | [Sign Up](https://azure.microsoft.com/) |

### **2. Required Tools**
| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **Git** | Version control | `sudo apt install git` |
| **Python 3.10+** | Runtime | `sudo apt install python3.10` |
| **pip** | Python package manager | `sudo apt install python3-pip` |
| **Docker** | Containerization | [Install Docker](https://docs.docker.com/engine/install/) |
| **Azure CLI** | Azure management | `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash` |
| **Terraform (Optional)** | Infrastructure as Code | [Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) |

---

---

## 🚀 Option 1: Cloud Deployment (Recommended)

Deploy STRIDE + Momento on **Azure Kubernetes Service (AKS)** or **Azure Container Instances (ACI)** for scalability and reliability.

---

### **📌 Step 1: Set Up Azure Resources**

#### **1.1 Install Azure CLI**
```bash
# For Debian/Ubuntu
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version
```

#### **1.2 Log in to Azure**
```bash
az login
# Follow the prompts to authenticate in your browser
```

#### **1.3 Create a Resource Group**
```bash
az group create --name stride-resources --location eastus
```

#### **1.4 Create a Container Registry (ACR)**
```bash
az acr create --resource-group stride-resources --name strideAcr --sku Basic
```

---

### **📌 Step 2: Build and Push Docker Image**

#### **2.1 Create a Dockerfile**
Create `Dockerfile` in the `backend/` directory:
```dockerfile
# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables (for development)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (if running an API)
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "momento.forecast"]
```

#### **2.2 Build the Docker Image**
```bash
cd backend
az acr build --registry strideAcr --image stride-app:latest .
```

#### **2.3 Verify the Image**
```bash
az acr repository list --name strideAcr --output table
```

---

### **📌 Step 3: Deploy to Azure Container Instances (ACI)**

#### **3.1 Deploy the Container**
```bash
az container create \
  --resource-group stride-resources \
  --name stride-container \
  --image strideAcr.azurecr.io/stride-app:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    MOMENTO_API_KEY="your-momento-api-key" \
    MOMENTO_ENDPOINT="your-cache-endpoint" \
    GEMINI_API_KEY="your-gemini-api-key" \
  --dns-name-label stride-app-$(date +%s) \
  --restart-policy Always
```

#### **3.2 Check Deployment Status**
```bash
az container show --resource-group stride-resources --name stride-container --output table
```

#### **3.3 Get the Public IP**
```bash
az container show --resource-group stride-resources --name stride-container --query ipAddress.ip --output tsv
```

---

### **📌 Step 4: Deploy to Azure Kubernetes Service (AKS) (Advanced)**

#### **4.1 Create an AKS Cluster**
```bash
az aks create \
  --resource-group stride-resources \
  --name stride-aks \
  --node-count 2 \
  --generate-ssh-keys \
  --attach-acr strideAcr
```

#### **4.2 Get Kubernetes Credentials**
```bash
az aks get-credentials --resource-group stride-resources --name stride-aks
```

#### **4.3 Deploy STRIDE with Kubernetes**
Create `stride-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stride-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: stride
  template:
    metadata:
      labels:
        app: stride
    spec:
      containers:
      - name: stride
        image: strideAcr.azurecr.io/stride-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: MOMENTO_API_KEY
          value: "your-momento-api-key"
        - name: MOMENTO_ENDPOINT
          value: "your-cache-endpoint"
        - name: GEMINI_API_KEY
          value: "your-gemini-api-key"
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: stride-service
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: stride
```

Apply the deployment:
```bash
kubectl apply -f stride-deployment.yaml
```

#### **4.4 Check Deployment Status**
```bash
kubectl get pods
kubectl get services
```

#### **4.5 Access the Application**
```bash
kubectl get service stride-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

### **📌 Step 5: Set Up Monitoring (Optional)**

#### **5.1 Install Prometheus and Grafana**
```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus -n monitoring --create-namespace

# Install Grafana
helm install grafana grafana/grafana -n monitoring
```

#### **5.2 Access Grafana Dashboard**
```bash
kubectl port-forward svc/grafana 3000:80 -n monitoring &# Open http://localhost:3000 in your browser (default creds: admin/admin)
```

---

### **📌 Step 6: Set Up CI/CD (GitHub Actions)**

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy STRIDE to Azure

on:
  push:
    branches: [ main, feature/stride-integration ]
  pull_request:
    branches: [ main ]

env:
  AZURE_RESOURCE_GROUP: stride-resources
  AZURE_ACR_NAME: strideAcr
  AZURE_CONTAINER_NAME: stride-container

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Build and push Docker image
      run: |        cd backend
        az acr build --registry ${{ env.AZURE_ACR_NAME }} --image stride-app:${{ github.sha }} .

    - name: Deploy to ACI
      run: |        az container create \
          --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
          --name ${{ env.AZURE_CONTAINER_NAME }} \
          --image ${{ env.AZURE_ACR_NAME }}.azurecr.io/stride-app:${{ github.sha }} \
          --cpu 2 \
          --memory 4 \
          --ports 8000 \
          --environment-variables \
            MOMENTO_API_KEY="${{ secrets.MOMENTO_API_KEY }}" \
            MOMENTO_ENDPOINT="${{ secrets.MOMENTO_ENDPOINT }}" \
            GEMINI_API_KEY="${{ secrets.GEMINI_API_KEY }}" \
          --dns-name-label stride-app-${{ github.sha }} \
          --restart-policy Always
```

#### **6.1 Set Up GitHub Secrets**
1. Go to **GitHub Repository → Settings → Secrets → Actions**.
2. Add the following secrets:
   - `AZURE_CREDENTIALS`: JSON output from `az ad sp create-for-rbac --name stride-sp --role Contributor --scopes /subscriptions/your-sub-id --sdk-auth`
   - `MOMENTO_API_KEY`: Your Momento API key.
   - `MOMENTO_ENDPOINT`: Your Momento cache endpoint.
   - `GEMINI_API_KEY`: Your Google Gemini API key.

---

---

## 🖥️ Option 2: Debian VM on Azure (Development/Testing)

Deploy STRIDE + Momento on a **Debian VM** on Azure for development and testing.

---

### **📌 Step 1: Create a Debian VM on Azure**

#### **1.1 Create the VM**
```bash
az vm create \
  --resource-group stride-resources \
  --name stride-vm \
  --image Debian:debian-12:12-gen2:latest \
  --admin-username azureuser \
  --generate-ssh-keys \
  --size Standard_D4s_v3 \
  --public-ip-sku Standard
```

#### **1.2 Connect to the VM**
```bash
ssh azureuser@<VM_PUBLIC_IP>
```

#### **1.3 Update the System**
```bash
sudo apt update && sudo apt upgrade -y
```

---

### **📌 Step 2: Install Dependencies**

#### **2.1 Install Python and pip**
```bash
sudo apt install -y python3.10 python3-pip python3-venv
```

#### **2.2 Install Git**
```bash
sudo apt install -y git
```

#### **2.3 Install Docker (Optional)**
```bash
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker azureuser
```

#### **2.4 Install Azure CLI (Optional)**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

---

### **📌 Step 3: Clone the Repository**

```bash
git clone https://github.com/avfsmomentoserver-cell/MomentoFresh.git
cd MomentoFresh
git checkout feature/stride-integration
```

---

### **📌 Step 4: Set Up Environment**

#### **4.1 Create a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### **4.2 Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

#### **4.3 Configure Environment Variables**
```bash
# Create .env file
nano backend/.env
```
Add the following (replace with your actual keys):
```ini
MOMENTO_API_KEY=your-momento-api-key
MOMENTO_ENDPOINT=your-cache-endpoint.momentohq.com
GEMINI_API_KEY=your-gemini-api-key
```

---

### **📌 Step 5: Run STRIDE Locally**

#### **5.1 Test the Forecasting Engine**
Create `test_stride.py` in the `backend/` directory:
```python
from momento.stride import ForecastEngine
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize engine
engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

# Test with sample data
X = [1.25, 1.30, 1.28, 1.35, 1.40]
E = {"source": "aviator"}

print("🔮 Generating forecast with STRIDE...")
Y_hat, R_hat = engine.forecast(X, E=E, use_reasoning=True)

print(f"Forecast: {Y_hat}")
print(f"Reasoning: {R_hat}")
```

Run the test:
```bash
cd backend
python test_stride.py
```

#### **5.2 Test with Momento**
Create `test_momento.py`:
```python
from momento.store import MomentoStore
from momento.stride import ForecastEngine
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Momento store
store = MomentoStore(
    endpoint=os.getenv("MOMENTO_ENDPOINT"),
    api_key=os.getenv("MOMENTO_API_KEY"),
)

# Store sample data
aviator_data = {
    "source": "aviator",
    "collectedAt": "2026-08-04T12:00:00.000Z",
    "rounds": [
        {"timestamp": "2026-08-04T12:00:00.000Z", "multiplier": 1.25},
        {"timestamp": "2026-08-04T13:00:00.000Z", "multiplier": 1.30},
    ]
}
store.store_raw_data("aviator_test", aviator_data)

# Initialize engine
engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

# Forecast from Momento
result = engine.forecast_from_momento("aviator_test", use_reasoning=True)
print(f"Forecast: {result['forecast']}")
print(f"Reasoning: {result['reasoning']}")
```

Run the test:
```bash
python test_momento.py
```

---

### **📌 Step 6: Run as a Service (Optional)**

#### **6.1 Create a FastAPI App**
Create `main.py` in the `backend/` directory:
```python
from fastapi import FastAPI
from momento.stride import ForecastEngine
from momento.store import MomentoStore
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize engine
engine = ForecastEngine(
    tsfm_name="chronos-2.0",
    use_stride=True,
    teacher_llm_api_key=os.getenv("GEMINI_API_KEY"),
    momento_endpoint=os.getenv("MOMENTO_ENDPOINT"),
    momento_api_key=os.getenv("MOMENTO_API_KEY"),
)

class ForecastRequest(BaseModel):
    X: list[float]
    E: dict = {}
    use_reasoning: bool = True

@app.post("/forecast")
def forecast(request: ForecastRequest):
    Y_hat, R_hat = engine.forecast(
        request.X,
        E=request.E,
        use_reasoning=request.use_reasoning
    )
    return {
        "forecast": Y_hat.tolist() if hasattr(Y_hat, 'tolist') else Y_hat,
        "reasoning": R_hat
    }

@app.post("/forecast/momento")
def forecast_from_momento(key: str, use_reasoning: bool = True):
    result = engine.forecast_from_momento(key, use_reasoning)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **6.2 Run the FastAPI App**
```bash
pip install fastapi uvicorn python-dotenv
python main.py
```

#### **6.3 Test the API**
```bash
# Forecast directly
curl -X POST http://localhost:8000/forecast \
  -H "Content-Type: application/json" \
  -d '{"X": [1.25, 1.30, 1.28], "E": {"source": "aviator"}, "use_reasoning": true}'

# Forecast from Momento
curl -X POST http://localhost:8000/forecast/momento?key=aviator_test&use_reasoning=true
```

#### **6.4 Run as a Systemd Service (Production)**
Create `/etc/systemd/system/stride.service`:
```ini
[Unit]
Description=STRIDE Forecasting API
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/MomentoFresh/backend
Environment="PATH=/home/azureuser/MomentoFresh/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/azureuser/MomentoFresh/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stride.service
sudo systemctl start stride.service
sudo systemctl status stride.service
```

---

---

## 📊 Deployment Comparison

| Feature | Cloud (AKS/ACI) | Debian VM |
|---------|------------------|-----------|
| **Scalability** | ✅ Auto-scaling | ❌ Manual scaling |
| **Cost** | ⚠️ Pay per use | ✅ Fixed (VM cost) |
| **Maintenance** | ⚠️ Managed by Azure | ❌ Self-managed |
| **Setup Time** | ⚠️ 30-60 mins | ✅ 15-30 mins |
| **Best For** | Production | Development/Testing |
| **High Availability** | ✅ Yes | ❌ No |
| **Monitoring** | ✅ Built-in (Azure Monitor) | ⚠️ Manual (Prometheus) |
| **CI/CD** | ✅ Easy (GitHub Actions) | ⚠️ Manual |

---

---

## 🔧 Troubleshooting

### **❌ Common Issues & Fixes**

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: momento` | Momento SDK not installed | `pip install momento` |
| `AuthenticationError: Invalid API key` | Wrong Momento API key | Verify `MOMENTO_API_KEY` in `.env` |
| `ConnectionError: Failed to connect` | Wrong Momento endpoint | Verify `MOMENTO_ENDPOINT` in `.env` |
| `ImportError: torch` | PyTorch not installed | `pip install torch` |
| `CUDA not available` | No GPU support | Use CPU (`device="cpu"`) or install CUDA |
| `Docker: Permission denied` | User not in Docker group | `sudo usermod -aG docker $USER` + logout/login |
| `az: command not found` | Azure CLI not installed | `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash` |
| `Port 8000 already in use` | Another service running | `sudo lsof -i :8000` + kill the process |

---

### **🐛 Debugging Tips**

#### **1. Check Logs**
```bash
# For Docker containers
docker logs <container_id>

# For Systemd services
sudo journalctl -u stride.service -f

# For FastAPI
uvicorn main:app --reload --log-level debug
```

#### **2. Test Momento Connection**
```python
from momento import CacheClient, Configurations

client = CacheClient.create(
    Configurations.Laptop.latest(
        api_key="your-api-key",
        endpoint="your-endpoint"
    )
)

# Test set/get
client.set("test_key", "test_value")
print(client.get("test_key"))  # Should print "test_value"
```

#### **3. Test STRIDE Locally**
```python
from momento.stride import ForecastEngine

engine = ForecastEngine(use_stride=False)  # Disable STRIDE for testing
X = [1.0, 2.0, 3.0]
Y_hat = engine.forecast(X, use_reasoning=False)
print(Y_hat)  # Should return a forecast
```

---

---

## 📚 Best Practices

### **🔐 Security**
1. **Never commit secrets** to Git. Use `.env` files and `.gitignore`.
2. **Use Azure Key Vault** for production secrets.
3. **Rotate API keys** every 90 days.
4. **Restrict network access** to Momento cache (use VNet or private endpoints).

### **⚡ Performance**
1. **Use GPU** for STRIDE training (e.g., `device="cuda"`).
2. **Cache reasoning traces** in Momento to avoid recomputation.
3. **Batch requests** to Momento for high throughput.
4. **Monitor latency** with Prometheus + Grafana.

### **📦 Dependency Management**
1. **Pin versions** in `requirements.txt` (e.g., `torch==2.2.0`).
2. **Use virtual environments** (`python -m venv venv`).
3. **Update dependencies** regularly (`pip list --outdated`).

### **🚀 CI/CD**
1. **Test in CI** before deploying (GitHub Actions).
2. **Use multi-stage Docker builds** to reduce image size.
3. **Roll back** quickly if deployment fails.

---

---

## 📖 Additional Resources

### **📚 Documentation**
- [STRIDE Paper (arXiv)](https://arxiv.org/abs/2605.08625)
- [Momento Docs](https://docs.momentohq.com/)
- [Azure Docs](https://docs.microsoft.com/en-us/azure/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Docs](https://docs.docker.com/)

### **🎥 Tutorials**
- [Deploy Python App to Azure](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [Dockerize a Python App](https://docs.docker.com/language/python/build-images/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Momento Quickstart](https://docs.momentohq.com/getting-started)

### **💬 Support**
- **Momento Slack**: [Join Slack](https://join.slack.com/t/momentohq/shared_invite/zt-12345678-abcdefghijklmnopqrstuvwx)
- **Azure Support**: [Azure Support](https://azure.microsoft.com/en-us/support/)
- **GitHub Discussions**: [MomentoFresh Discussions](https://github.com/avfsmomentoserver-cell/MomentoFresh/discussions)

---

---

## 📜 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-04 | [Your Name] | Initial version |

---

---

**📌 Note**: Replace placeholders (e.g., `your-api-key`, `your-endpoint`) with your actual values.
