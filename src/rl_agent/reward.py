"""
Reward shaping logic
"""

ACTIONS = {0: "ALLOW", 1: "BLOCK", 2: "RATE-LIMIT"}

DEFAULT_REWARDS = {
    "block_attack": 10,
    "allow_attack": -50,
    "block_legit": -20,
    "allow_legit": 1,
    "limit_attack": 3,
    "limit_legit": -5,
}


def compute_reward(action: int, is_attack: bool, cfg: dict = None) -> tuple:
    c = cfg or DEFAULT_REWARDS
    if is_attack:
        if action == 1:
            return c["block_attack"], "Correctly blocked attack"
        if action == 2:
            return c["limit_attack"], "Rate-limited attack"
        return c["allow_attack"], "MISSED ATTACK"
    else:
        if action == 0:
            return c["allow_legit"], "Correctly allowed legitimate"
        if action == 2:
            return c["limit_legit"], "Unnecessarily throttled"
        return c["block_legit"], "FALSE POSITIVE"
