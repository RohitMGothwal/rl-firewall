import numpy as np
from src.features.extractor import FeatureExtractor, NUM_FEATURES


def make_record(length=500, dst_port=80, protocol=6, tcp_flags=2,
                pkt_rate=10.0, byte_rate=5000.0):
    return {
        "timestamp": 0.0, "src_ip": "1.2.3.4", "dst_ip": "5.6.7.8",
        "length": length, "dst_port": dst_port, "protocol": protocol,
        "tcp_flags": tcp_flags, "src_port": 12345,
        "pkt_rate": pkt_rate, "byte_rate": byte_rate,
    }


def test_output_shape():
    ext = FeatureExtractor()
    state = ext.extract(make_record())
    assert state.shape == (NUM_FEATURES,)


def test_output_range():
    ext = FeatureExtractor()
    state = ext.extract(make_record())
    assert np.all(state >= 0.0) and np.all(state <= 1.0)


def test_syn_flag_detected():
    ext = FeatureExtractor()
    state_syn   = ext.extract(make_record(tcp_flags=0x02))
    state_no    = ext.extract(make_record(tcp_flags=0x10))
    assert state_syn[6] == 1.0
    assert state_no[6]  == 0.0


def test_window_state():
    ext = FeatureExtractor(window=3)
    for _ in range(5):
        ext.push(make_record())
    ws = ext.window_state()
    assert ws.shape == (NUM_FEATURES,)
