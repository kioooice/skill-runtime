from skill_runtime.distill.fallback.provider import FallbackRequest, FallbackResponse
from skill_runtime.distill.rules.common import compact_step, escape, indent_docstring


class MockFallbackProvider:
    provider_name = "mock_fallback_provider"

    def generate(self, request: FallbackRequest) -> FallbackResponse:
        param_defaults = ", ".join(
            f'"{name}": kwargs.get("{name}")' for name in request.input_schema.keys()
        )
        step_comments = "\n".join(
            f'    # Step {index}: {compact_step(step.tool_name, step.observation)}'
            for index, step in enumerate(request.trajectory.steps, start=1)
        )

        code = f'''def run(tools, **kwargs):
    """
{indent_docstring(request.docstring)}
    """
    inputs = {{{param_defaults}}}

    missing = [key for key, value in inputs.items() if value is None]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

{step_comments}

    return {{
        "status": "completed",
        "skill_name": "{escape(request.skill_name)}",
        "summary": "{escape(request.summary)}",
        "artifacts": {request.trajectory.artifacts!r},
        "steps_executed": {len(request.trajectory.steps)},
        "inputs": inputs,
        "generated_by": "{self.provider_name}",
    }}
'''
        return FallbackResponse(
            code=code,
            provider_name=self.provider_name,
            reason="No deterministic rule matched, so the mock fallback provider generated a parameterized candidate skill from the trajectory prompt.",
        )
