#!/usr/bin/env python3
"""Aggregate already-clustered behavioral spec review artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


VECTOR_FIELDS = ("impact", "reach", "reversibility", "exposure", "evidence")
SEVERITY_BY_IMPACT = {
    "catastrophic": "Critical",
    "major": "High",
    "moderate": "Medium",
    "minor": "Low",
}


def ratio(count: int, total: int) -> float:
    return count / total if total else 0.0


def modal(values: list[str]) -> tuple[str, float]:
    counts = Counter(values)
    value, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return value, ratio(count, len(values))


def load_input(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    units = data.get("review_units")
    if not isinstance(units, list) or not units:
        raise ValueError("review_units must be a non-empty list")
    unit_ids = [unit.get("id") for unit in units]
    if any(not unit_id for unit_id in unit_ids) or len(unit_ids) != len(set(unit_ids)):
        raise ValueError("review unit ids must be present and unique")
    return data


def tier(unit_support: float, run_count: int, total_runs: int) -> str:
    if unit_support >= 0.80 and run_count == total_runs:
        return "Core"
    if unit_support >= 0.50:
        return "Supported"
    return "Contested"


def aggregate(data: dict[str, Any]) -> dict[str, Any]:
    units = data["review_units"]
    unit_to_run = {unit["id"]: unit["run"] for unit in units}
    all_runs = sorted(set(unit_to_run.values()))
    total_units = len(units)
    total_runs = len(all_runs)

    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_memberships: set[tuple[str, str]] = set()
    for finding in data.get("findings", []):
        unit_id = finding.get("unit")
        cluster_id = finding.get("cluster_id")
        if unit_id not in unit_to_run:
            raise ValueError(f"unknown finding unit: {unit_id}")
        if not cluster_id:
            raise ValueError("every finding must have cluster_id")
        membership = (unit_id, cluster_id)
        if membership in seen_memberships:
            raise ValueError(f"duplicate unit membership in cluster: {membership}")
        seen_memberships.add(membership)
        vector = finding.get("vector", {})
        missing = [field for field in VECTOR_FIELDS if field not in vector]
        if missing:
            raise ValueError(f"finding {cluster_id} missing vector fields: {missing}")
        clusters[cluster_id].append(finding)

    cluster_rows = []
    for cluster_id, findings in sorted(clusters.items()):
        supporting_units = sorted({finding["unit"] for finding in findings})
        supporting_runs = sorted({unit_to_run[unit] for unit in supporting_units})
        support = ratio(len(supporting_units), total_units)
        finding_type, type_agreement = modal([finding["type"] for finding in findings])
        vector = {}
        vector_agreement = {}
        for field in VECTOR_FIELDS:
            value, agreement = modal([finding["vector"][field] for finding in findings])
            vector[field] = value
            vector_agreement[field] = agreement
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "tier": tier(support, len(supporting_runs), total_runs),
                "supporting_units": supporting_units,
                "supporting_runs": supporting_runs,
                "unit_support": support,
                "run_support": ratio(len(supporting_runs), total_runs),
                "type": finding_type,
                "type_agreement": type_agreement,
                "severity": SEVERITY_BY_IMPACT[vector["impact"]],
                "vector": vector,
                "vector_agreement": vector_agreement,
            }
        )

    scenario_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for result in data.get("scenario_results", []):
        unit_id = result.get("unit")
        if unit_id not in unit_to_run:
            raise ValueError(f"unknown scenario unit: {unit_id}")
        scenario_groups[(unit_to_run[unit_id], result["scenario"])].append(
            result["outcome"]
        )
    unanimous = sum(len(set(values)) == 1 for values in scenario_groups.values())

    tier_counts = Counter(row["tier"] for row in cluster_rows)
    retained = [row for row in cluster_rows if row["tier"] != "Contested"]
    if not retained:
        verdict = "Implementation-ready"
    elif any(
        row["severity"] == "Critical"
        or (row["severity"] == "High" and row["vector"]["reach"] == "core")
        for row in retained
    ):
        verdict = "Not implementable"
    else:
        verdict = "Implementable with caveats"
    return {
        "review_units": total_units,
        "runs": total_runs,
        "scenario_convergence": {
            "unanimous": unanimous,
            "total": len(scenario_groups),
        },
        "tier_counts": {
            "Core": tier_counts["Core"],
            "Supported": tier_counts["Supported"],
            "Contested": tier_counts["Contested"],
        },
        "verdict": verdict,
        "clusters": cluster_rows,
    }


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def render_markdown(result: dict[str, Any]) -> str:
    convergence = result["scenario_convergence"]
    tiers = result["tier_counts"]
    lines = [
        f"- Review units: `{result['review_units']}` across `{result['runs']}` runs",
        (
            "- Scenario-run convergence: "
            f"`{convergence['unanimous']}/{convergence['total']}`"
        ),
        (
            "- Finding tiers: "
            f"`Core={tiers['Core']}, Supported={tiers['Supported']}, "
            f"Contested={tiers['Contested']}`"
        ),
        f"- Verdict: `{result['verdict']}`",
        "",
        "| Cluster | Tier | Severity | Unit support | Run support | Type agreement | Vector agreement |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in result["clusters"]:
        vector_agreement = ", ".join(
            f"{field}={percent(row['vector_agreement'][field])}"
            for field in VECTOR_FIELDS
        )
        lines.append(
            f"| {row['cluster_id']} | {row['tier']} | {row['severity']} | "
            f"{percent(row['unit_support'])} | {percent(row['run_support'])} | "
            f"{percent(row['type_agreement'])} | {vector_agreement} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        result = aggregate(load_input(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
