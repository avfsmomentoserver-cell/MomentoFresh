# MomentoFresh

> **Advanced Analytics & Forecasting Platform for Crash Games**

A clean, fresh implementation of the Momento Core platform with enhanced features for professional analysis, backtesting, and predictive modeling.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (with Bun recommended)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/avfsmomentoserver-cell/MomentoFresh.git
cd MomentoFresh

# Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../web
bun install

# Start the system
# Terminal 1: Backend
cd backend
python3 run_api.py

# Terminal 2: Frontend
cd web
bun run dev
```

Access the dashboard at: http://localhost:8080