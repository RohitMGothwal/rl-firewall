# rl-firewall
Dynamic Reinforcement Learning Firewall — DQN-based adaptive packet filtering

## ✨ Features

- **🧠 Reinforcement Learning**: DQN agent learns optimal policies from network traffic
- **📊 Real-time Dashboard**: WebSocket-based live monitoring with FastAPI
- **🔴 Live Packet Capture**: Scapy-based traffic analysis with session tracking
- **🛡️ iptables Integration**: Real firewall rule enforcement (BLOCK/RATE-LIMIT/ALLOW)
- **📈 Metrics & Logging**: Prometheus metrics, JSON audit trails, F1 tracking
- **🐳 Docker Ready**: Complete stack with Grafana + Prometheus
- **🧪 Tested**: Full pytest suite for all components

## 🏗️ Architecture
rl-firewall/
├── src/
│   ├── capture/         # Packet capture (scapy)
│   ├── features/        # Feature extraction
│   ├── rl_agent/        # DQN agent (SB3)
│   ├── enforcer/        # iptables rules
│   ├── monitor/         # Metrics & logging
│   └── dashboard/       # Web UI (FastAPI)
├── tests/               # Pytest suite
├── data/                # Datasets
├── models/              # Saved checkpoints
├── logs/                # Audit trails
├── train.py             # Training entry point
├── main.py              # Live firewall
└── evaluate.py          # Evaluation script

### State Vector (7 Features)
| Index | Feature | Description | Range |
|-------|---------|-------------|-------|
| 0 | Packet Size | Normalized packet length | [0,1] |
| 1 | Destination Port | Normalized port number | [0,1] |
| 2 | Protocol | TCP=1.0, UDP=0.5, ICMP=0.25 | [0,1] |
| 3 | TCP Flags | Normalized flags byte | [0,1] |
| 4 | Packet Rate | Packets/sec (max 1000) | [0,1] |
| 5 | Byte Rate | Bytes/sec (max 10M) | [0,1] |
| 6 | SYN Ratio | SYN flag detected (0 or 1) | {0,1} |

### Actions
| ID | Action | iptables Rule | Use Case |
|----|--------|--------------|----------|
| 0 | ALLOW | No rule | Legitimate traffic |
| 1 | BLOCK | `-j DROP` | Confirmed attacks |
| 2 | RATE-LIMIT | `-m limit --limit 5/s` | Suspicious traffic |

### Reward Structure
- **Block Attack**: +10 ✅
- **Allow Legit**: +1 ✅
- **Rate-limit Attack**: +3 (partial credit)
- **Block Legit (False Positive)**: -20 ❌
- **Allow Attack (Miss)**: -50 ❌❌
- **Rate-limit Legit**: -5

## 🚀 Installation

### Prerequisites
- Python 3.11+
- macOS/Linux (for iptables support)
- Root access (for live firewall mode)

### 1. Clone & Setup
```bash
git clone https://github.com/RohitMGothwal/rl-firewall.git
cd rl-firewall

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
