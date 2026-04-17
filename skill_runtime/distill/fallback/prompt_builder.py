from skill_runtime.api.models import Trajectory


def build_fallback_prompt(
    skill_name: str,
    summary: str,
    docstring: str,
    trajectory: Trajectory,
    input_schema: dict[str, str],
) -> str:
    step_lines = "\n".join(
        f"- Step {index}: tool={step.tool_name}, input={step.tool_input}, observation={step.observation}"
        for index, step in enumerate(trajectory.steps, start=1)
    )
    input_lines = "\n".join(f"- {name}: {type_name}" for name, type_name in input_schema.items())

    return (
        "You are generating a reusable Python skill.\n"
        f"Skill name: {skill_name}\n"
        f"Summary: {summary}\n"
        "Constraints:\n"
        "- Define run(tools, **kwargs)\n"
        "- Keep the code parameterized\n"
        "- Do not use dangerous shell commands\n"
        "- Return a structured dict\n\n"
        f"Docstring target:\n{docstring}\n\n"
        f"Input schema:\n{input_lines}\n\n"
        f"Trajectory:\n{step_lines}\n"
    )
