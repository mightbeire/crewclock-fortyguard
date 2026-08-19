from fortyguard_agent.evals import run_fixture_spikes


def test_all_three_fixture_spikes_improve_and_require_approval() -> None:
    results = run_fixture_spikes()
    assert len(results) == 3
    assert all(result.passed for result in results)
    assert all(result.improvement > 0 for result in results)
    assert all(result.agent_termination == "awaiting_human_approval" for result in results)
