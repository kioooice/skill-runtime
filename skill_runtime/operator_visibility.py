from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


OPERATOR_SUMMARY_STALE_AFTER_SECONDS = 24 * 60 * 60
OPERATOR_QUALITY_GATE_STALE_AFTER_SECONDS = 3 * 24 * 60 * 60


def freshness_policy_export(stale_after_seconds: int) -> dict[str, Any]:
    return {
        "basis": "generated_at",
        "stale_after_seconds": int(stale_after_seconds),
    }


def coerce_freshness_policy(payload: Any, *, default_stale_after_seconds: int) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return freshness_policy_export(default_stale_after_seconds)
    basis = payload.get("basis") if isinstance(payload.get("basis"), str) else "generated_at"
    stale_after_seconds = payload.get("stale_after_seconds")
    if not isinstance(stale_after_seconds, int) or stale_after_seconds <= 0:
        stale_after_seconds = default_stale_after_seconds
    return {
        "basis": basis,
        "stale_after_seconds": stale_after_seconds,
    }


def evaluate_freshness(generated_at: Any, policy: dict[str, Any]) -> dict[str, Any]:
    stale_after_seconds = policy.get("stale_after_seconds")
    stale_after_seconds = stale_after_seconds if isinstance(stale_after_seconds, int) else None
    parsed_generated_at = parse_timestamp(generated_at)
    if parsed_generated_at is None:
        return {
            "status": "unknown",
            "age_seconds": None,
            "stale_after_seconds": stale_after_seconds,
            "reason": "Freshness cannot be evaluated without a valid generated_at timestamp.",
        }
    if stale_after_seconds is None or stale_after_seconds <= 0:
        return {
            "status": "unknown",
            "age_seconds": None,
            "stale_after_seconds": None,
            "reason": "Freshness cannot be evaluated without a valid stale_after_seconds policy.",
        }
    age_seconds = max(0, int((datetime.now(timezone.utc) - parsed_generated_at).total_seconds()))
    if age_seconds > stale_after_seconds:
        return {
            "status": "stale",
            "age_seconds": age_seconds,
            "stale_after_seconds": stale_after_seconds,
            "reason": "Generated timestamp is older than the freshness policy threshold.",
        }
    return {
        "status": "fresh",
        "age_seconds": age_seconds,
        "stale_after_seconds": stale_after_seconds,
        "reason": "Generated timestamp is within the freshness policy threshold.",
    }


def enrich_operator_summary_freshness(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    enriched["freshness_policy"] = coerce_freshness_policy(
        enriched.get("freshness_policy"),
        default_stale_after_seconds=OPERATOR_SUMMARY_STALE_AFTER_SECONDS,
    )
    enriched["freshness"] = evaluate_freshness(
        enriched.get("generated_at"),
        enriched["freshness_policy"],
    )
    quality_gates = enriched.get("quality_gates")
    if not isinstance(quality_gates, dict):
        return enriched
    enriched_quality_gates: dict[str, Any] = {}
    for key, value in quality_gates.items():
        if not isinstance(value, dict):
            enriched_quality_gates[key] = value
            continue
        gate = dict(value)
        gate["freshness_policy"] = coerce_freshness_policy(
            gate.get("freshness_policy"),
            default_stale_after_seconds=OPERATOR_QUALITY_GATE_STALE_AFTER_SECONDS,
        )
        gate["freshness"] = evaluate_freshness(
            gate.get("generated_at"),
            gate["freshness_policy"],
        )
        enriched_quality_gates[key] = gate
    enriched["quality_gates"] = enriched_quality_gates
    return enriched


def parse_timestamp(raw_value: Any) -> datetime | None:
    if not isinstance(raw_value, str) or not raw_value.strip():
        return None
    normalized = raw_value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
