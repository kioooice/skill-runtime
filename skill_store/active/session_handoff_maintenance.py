from skill_runtime.execution.global_skill_adapter import run_global_skill_adapter


def run(tools, **kwargs):
    return run_global_skill_adapter(
        tools,
        runtime_skill_name="session_handoff_maintenance",
        global_skill_name="session-handoff-maintenance",
        **kwargs,
    )
