from fortyguard_agent.evals import evaluate_window_baselines, run_fixture_spikes


def test_all_three_fixture_spikes_improve_and_require_approval() -> None:
    results = run_fixture_spikes()
    assert len(results) == 3
    assert all(result.passed for result in results)
    assert all(result.improvement > 0 for result in results)
    assert all(result.agent_termination == "awaiting_human_approval" for result in results)


def test_baselines_are_reported_separately() -> None:
    profile = [20.0, 35.0, 40.0, 25.0]
    result = evaluate_window_baselines(profile, [{"start_hour": 1, "end_hour": 3}, {"start_hour": 0, "end_hour": 2}], threshold_c=30.0)
    assert set(result) == {"no_assistance", "static_threshold_rule", "naive_first_choice", "agent_verified_proxy", "candidates"}
    assert result["agent_verified_proxy"]["contextual_temperature_exceedance_degree_hours"] <= result["naive_first_choice"]["contextual_temperature_exceedance_degree_hours"]
