def run(tools, **kwargs):
    """
    功能描述:
        Generate a report from mixed observations without a deterministic rule.

    输入参数:
            - report_name: str
            - topic: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    inputs = {"report_name": kwargs.get("report_name"), "topic": kwargs.get("topic")}

    missing = [key for key, value in inputs.items() if value is None]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    # Step 1: observe_state: Collected mixed observations.
    # Step 2: summarize_notes: Summarized notes into a draft.

    return {
        "status": "completed",
        "skill_name": "semantic_provider_fallback_test",
        "summary": "Generate a report from mixed observations without a deterministic rule.",
        "artifacts": ['demo/output/fallback_semantic.txt'],
        "steps_executed": 2,
        "inputs": inputs,
        "generated_by": "mock_fallback_provider",
    }
