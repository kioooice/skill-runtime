from skill_runtime.execution.global_skill_adapter import run_global_skill_adapter


def run(tools, **kwargs):
    return run_global_skill_adapter(
        tools,
        runtime_skill_name="repo_impact_analysis",
        global_skill_name="repo-impact-analysis",
        **kwargs,
    )
