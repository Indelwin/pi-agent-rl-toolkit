from pi_agent_env import load_environment


def test_pi_agent_env_still_loads_without_judge():
    env = load_environment(use_judge=False, max_turns=1)

    assert env is not None
