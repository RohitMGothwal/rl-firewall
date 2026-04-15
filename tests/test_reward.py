from src.rl_agent.reward import compute_reward


def test_block_attack_positive():
    reward, _ = compute_reward(action=1, is_attack=True)
    assert reward > 0


def test_allow_attack_severe_penalty():
    reward, _ = compute_reward(action=0, is_attack=True)
    assert reward <= -50


def test_block_legit_penalty():
    reward, _ = compute_reward(action=1, is_attack=False)
    assert reward < 0


def test_allow_legit_positive():
    reward, _ = compute_reward(action=0, is_attack=False)
    assert reward > 0


def test_reason_string_returned():
    _, reason = compute_reward(action=1, is_attack=True)
    assert isinstance(reason, str) and len(reason) > 0
