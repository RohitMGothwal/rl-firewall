import numpy as np
from src.features.extractor import FeatureExtractor, NUM_FEATURES
from src.monitor.metrics import MetricsTracker


def test_metrics_f1_none_on_start():
    m = MetricsTracker()
    assert m.f1() is None


def test_metrics_updates_correctly():
    m = MetricsTracker()
    m.update(action=1, is_attack=True,  reward=10)   # TP
    m.update(action=0, is_attack=False, reward=1)    # TN
    assert m.tp == 1
    assert m.tn == 1


def test_f1_computed():
    m = MetricsTracker()
    for _ in range(5):
        m.update(1, True,  10)   # TP
        m.update(0, False, 1)    # TN
    f1 = m.f1()
    assert f1 is not None and 0.0 < f1 <= 1.0
