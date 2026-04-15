import time
import random
import numpy as np
from src.dashboard.database import db
from src.rl_agent.reward import compute_reward, ACTIONS
from src.features.extractor import FeatureExtractor

print("🔥 RL Firewall Demo Mode")
print("Generating synthetic network traffic...\n")

extractor = FeatureExtractor()

# Simulate 20 network events
for i in range(20):
    # Randomly decide if this is an attack (30% chance)
    is_attack = random.random() < 0.3
    
    # Generate realistic features
    if is_attack:
        # Attack pattern: High packet rate, SYN flood
        record = {
            "src_ip": f"192.168.1.{random.randint(10,50)}",
            "dst_port": random.choice([22, 80, 443, 3389]),
            "protocol": 6,  # TCP
            "length": random.randint(40, 100),
            "tcp_flags": 0x02,  # SYN
            "pkt_rate": random.uniform(800, 1000),  # High rate
            "byte_rate": random.uniform(8e6, 1e7)
        }
    else:
        # Legitimate traffic: Normal browsing
        record = {
            "src_ip": f"10.0.0.{random.randint(1,20)}",
            "dst_port": random.choice([80, 443, 53]),
            "protocol": random.choice([6, 17]),
            "length": random.randint(200, 1500),
            "tcp_flags": 0x18,  # PSH+ACK
            "pkt_rate": random.uniform(10, 100),  # Normal rate
            "byte_rate": random.uniform(1e4, 1e5)
        }
    
    # Extract features (what the RL agent sees)
    state = extractor.extract(record)
    
    # Simulate RL Agent decision (simple heuristic for demo)
    if state[4] > 0.7 and state[6] > 0.5:  # High pkt_rate + SYN
        action = 1  # BLOCK
    elif state[4] > 0.5:
        action = 2  # RATE-LIMIT
    else:
        action = 0  # ALLOW
    
    # Calculate reward
    reward, reason = compute_reward(action, is_attack)
    
    # Log to dashboard database
    db.log_event(
        src_ip=record["src_ip"],
        dst_port=record["dst_port"],
        action=ACTIONS[action],
        is_attack=is_attack,
        reward=float(reward),
        reason=reason
    )
    
    # Print to console (like iptables logs)
    icon = "🛑" if action == 1 else ("⚠️" if action == 2 else "✅")
    attack_icon = "🔴 ATTACK" if is_attack else "🟢 LEGIT"
    print(f"{icon} [{attack_icon}] {record['src_ip']}:{record['dst_port']} -> {ACTIONS[action]} (Reward: {reward:+.0f})")
    print(f"   Features: pkt_rate={state[4]:.2f}, syn={state[6]:.0f}")
    print(f"   Reason: {reason}\n")
    
    time.sleep(1.5)  # Slow enough to watch

print("\n✅ Demo complete! Check the dashboard for analytics.")
