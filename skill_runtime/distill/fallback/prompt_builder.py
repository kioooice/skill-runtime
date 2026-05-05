from skill_runtime.api.models import Trajectory


def build_provider_guidance(summary: str, trajectory: Trajectory) -> str:
    guidance_lines = [
        "- Generate executable workflow code, not a template summary.",
        "- Use runtime tools that match the successful trajectory when relevant, such as tools.read_json, tools.write_text, or tools.write_json.",
        "- Parameterize input/output paths through kwargs.",
        "- Avoid hardcoding demo artifact names from the trajectory.",
    ]

    context_text = f"{summary}\n{trajectory.task_description}".lower()
    if "review" in context_text and "cleanup" in context_text:
        guidance_lines.extend(
            [
                "- For review cleanup, write a cleanup plan artifact rather than modifying source code.",
                "- Do not auto-resolve review comments.",
                "- Do not infer merge approval.",
                "- Do not bypass maintainer judgment.",
            ]
        )

    return "\n".join(guidance_lines)


def build_fallback_prompt(
    skill_name: str,
    summary: str,
    docstring: str,
    trajectory: Trajectory,
    input_schema: dict[str, str],
    provider_guidance: str,
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
        f"Provider guidance:\n{provider_guidance}\n\n"
        f"Docstring target:\n{docstring}\n\n"
        f"Input schema:\n{input_lines}\n\n"
        f"Trajectory:\n{step_lines}\n"
    )
