"""
Feature Extraction Engine
"""
import numpy as np
from collections import deque

NUM_FEATURES = 7
SYN_FLAG = 0x02


class FeatureExtractor:
    def __init__(self, window: int = 10):
        self.window = window
        self.buffer = deque(maxlen=window)

    def push(self, record: dict):
        self.buffer.append(record)

    def extract(self, record: dict) -> np.ndarray:
        proto = record.get("protocol", 0)
        proto_norm = {6: 1.0, 17: 0.5, 1: 0.25}.get(proto, 0.0)

        flags = record.get("tcp_flags", 0)
        syn_ratio = 1.0 if (flags & SYN_FLAG) else 0.0
        pkt_rate = min(record.get("pkt_rate", 0.0), 1000.0) / 1000.0
        byte_rate = min(record.get("byte_rate", 0.0), 1e7) / 1e7

        state = np.array([
            min(record.get("length", 0), 65535) / 65535.0,
            record.get("dst_port", 0) / 65535.0,
            proto_norm,
            flags / 255.0,
            pkt_rate,
            byte_rate,
            syn_ratio,
        ], dtype=np.float32)
        return state

    def window_state(self) -> np.ndarray:
        if not self.buffer:
            return np.zeros(NUM_FEATURES, dtype=np.float32)
        states = [self.extract(r) for r in self.buffer]
        return np.mean(states, axis=0).astype(np.float32)
