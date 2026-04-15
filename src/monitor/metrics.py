"""
Metrics tracking for RL Firewall
"""

class MetricsTracker:
    def __init__(self):
        self.tp = self.fp = self.tn = self.fn = 0
        self.cumulative_reward = 0.0

    def update(self, action: int, is_attack: bool, reward: float):
        self.cumulative_reward += reward
        
        blocked = (action == 1)
        if is_attack and blocked:
            self.tp += 1
        elif not is_attack and blocked:
            self.fp += 1
        elif not is_attack and not blocked:
            self.tn += 1
        else:
            self.fn += 1

    def precision(self):
        d = self.tp + self.fp
        return self.tp / d if d else None

    def recall(self):
        d = self.tp + self.fn
        return self.tp / d if d else None

    def f1(self):
        p, r = self.precision(), self.recall()
        if p is None or r is None or (p + r) == 0:
            return None
        return 2 * p * r / (p + r)

    def report(self):
        return {
            "tp": self.tp, "fp": self.fp,
            "tn": self.tn, "fn": self.fn,
            "precision": round(self.precision() or 0, 4),
            "recall": round(self.recall() or 0, 4),
            "f1": round(self.f1() or 0, 4),
            "cumulative_reward": round(self.cumulative_reward, 2),
        }
