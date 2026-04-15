# 🚀 RL-Based Dynamic Firewall

## ✨ Features

- 🧠 **Reinforcement Learning**: DQN agent learns optimal policies from network traffic  
- 📊 **Real-time Dashboard**: WebSocket-based live monitoring with FastAPI  
- 🔴 **Live Packet Capture**: Scapy-based traffic analysis with session tracking  
- 🛡️ **iptables Integration**: Real firewall rule enforcement (BLOCK / RATE-LIMIT / ALLOW)  
- 📈 **Metrics & Logging**: Prometheus metrics, JSON audit trails, F1 tracking  
- 🐳 **Docker Ready**: Full observability stack with Grafana + Prometheus  
- 🧪 **Fully Tested**: Comprehensive pytest suite  

---

## 🏗️ Architecture

### 📌 State Vector (7 Features)

| Index | Feature           | Description                          | Range   |
|------|------------------|--------------------------------------|--------|
| 0    | Packet Size       | Normalized packet length             | [0,1]  |
| 1    | Destination Port  | Normalized port number               | [0,1]  |
| 2    | Protocol          | TCP=1.0, UDP=0.5, ICMP=0.25          | [0,1]  |
| 3    | TCP Flags         | Normalized flags byte                | [0,1]  |
| 4    | Packet Rate       | Packets/sec (max 1000)               | [0,1]  |
| 5    | Byte Rate         | Bytes/sec (max 10M)                  | [0,1]  |
| 6    | SYN Ratio         | SYN flag detected                    | {0,1}  |

---

### ⚡ Actions

| ID | Action        | iptables Rule              | Use Case             |
|----|--------------|---------------------------|----------------------|
| 0  | ALLOW         | No rule                   | Legitimate traffic   |
| 1  | BLOCK         | `-j DROP`                 | Confirmed attacks    |
| 2  | RATE-LIMIT    | `-m limit --limit 5/s`    | Suspicious traffic   |

---

### 🎯 Reward Structure

- ✅ **Block Attack**: +10  
- ✅ **Allow Legit**: +1  
- ⚖️ **Rate-limit Attack**: +3  
- ❌ **Block Legit (False Positive)**: -20  
- ❌❌ **Allow Attack (Miss)**: -50  
- ⚠️ **Rate-limit Legit**: -5  

---

## 🚀 Installation

### 📋 Prerequisites

#### 🅰️ Option A: Standard Python
- Python 3.11+  
- macOS/Linux (iptables support) or Windows (WSL recommended)  
- Root access (optional for live firewall mode)  

#### 🅱️ Option B: Docker
- Docker Desktop 4.0+  
- Docker Compose v2.0+  

---

## ⚙️ 1. Setup & Installation

### 🔹 Option 1: Python Virtual Environment (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/RohitMGothwal/rl-firewall.git
cd rl-firewall

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest tests/ -v
```

###🐳 Option 2: Docker (Recommended for Production)

```bash
# Clone repository
git clone https://github.com/RohitMGothwal/rl-firewall.git
cd rl-firewall

# Build and start all services
docker compose up --build -d

# Services available at:
# - Dashboard: http://localhost:8080
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)

# View logs
docker compose logs -f dashboard

# Stop all services
docker compose down
```

###⚡ 2. Quick Start

  ###🐍 Python Mode:

  ```bash
  # Terminal 1: Start Dashboard
  python src/dashboard/app_complete.py
  # Open http://localhost:8080

  # Terminal 2: Run demo traffic
  python demo_traffic.py

  # Terminal 3: Train model (optional)
  python train.py --data data/processed/cicids_processed.csv
  ```

###🐳 Docker Mode:

```bash
# Everything runs automatically
docker compose up --build

# Access dashboard at http://localhost:8080

```

###🛠️ 3. Troubleshooting

  ###⚠️ Port already in use?

  ```bash
  # Kill process on port 8080
  lsof -ti:8080 | xargs kill -9

  ```

  ###🔐 Permission denied (macOS)?
	-	Go to:
  System Settings → Privacy & Security → Full Disk Access
	-	Grant access to your terminal

  ###📦 Module not found errors?

  ```bash
  # Ensure you're in the correct directory
  pwd  # Should show .../rl-firewall

  # Reinstall in editable mode
  pip install -e .

  ```

