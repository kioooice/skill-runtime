from skill_runtime.execution.global_skill_adapter import run_global_skill_adapter


def run(tools, **kwargs):
    return run_global_skill_adapter(
        tools,
        runtime_skill_name="auto_mode_stage_runner",
        global_skill_name="auto-mode-stage-runner",
        **kwargs,
    )
