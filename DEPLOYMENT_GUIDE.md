
#### 4.4 Check Deployment Status
```bash
kubectl get pods
kubectl get services
```

#### 4.5 Access the Application
```bash
kubectl get service stride-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

### Step 5: Set Up Monitoring (Optional)

#### 5.1 Install Prometheus and Grafana
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -n monitoring --create-namespace
helm install grafana grafana/grafana -n monitoring
```

#### 5.2 Access Grafana Dashboard
```bash
kubectl port-forward svc/grafana 3000:80 -n monitoring &
# Open http://localhost:3000 in your browser (default creds: admin/admin)
```

---

### Step 6: Set Up CI/CD (GitHub Actions)

Create .github/workflows/deploy.yml:
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
      run: |
        cd backend
        az acr build --registry ${{ env.AZURE_ACR_NAME }} --image stride-app:${{ github.sha }} .
    - name: Deploy to ACI
      run: |
        az container create \
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

#### 6.1 Set Up GitHub Secrets
1. Go to GitHub Repository → Settings → Secrets → Actions.
2. Add: AZURE_CREDENTIALS, MOMENTO_API_KEY, MOMENTO_ENDPOINT, GEMINI_API_KEY.

---

---

## Option 2: Debian VM on Azure (Development/Testing)

Deploy STRIDE + Momento on a Debian VM on Azure for development and testing.

---

### Step 1: Create a Debian VM on Azure

#### 1.1 Create the VM
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

#### 1.2 Connect to the VM
```bash
ssh azureuser@<VM_PUBLIC_IP>
```

#### 1.3 Update the System
```bash
sudo apt update && sudo apt upgrade -y
```

---

### Step 2: Install Dependencies

#### 2.1 Install Python and pip
```bash
sudo apt install -y python3.10 python3-pip python3-venv
```

#### 2.2 Install Git
```bash
sudo apt install -y git
```

#### 2.3 Install Docker (Optional)
```bash
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker azureuser
```
