#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_report.py

Usage:
  python3 generate_report.py \
    --input ./session-output-<timestamp>/final-summary.meta.json \
    --report-data ./session-output-<timestamp>/performance-data/report-data.json \
    --out ./session-output-<timestamp>/report.html

  python3 generate_report.py \
    --input ./session-output-<timestamp>/analysis-output.json \
    --out ./session-output-<timestamp>/report.html

What it does:
1) Reads a JSON input: either a `final-summary.meta.json` sidecar (with
   `topic_outputs[].file`) or a bundled `analysis-output.json`
   (with a top-level `analysis_topics` array).
2) Reads the HTML template (default: ../templates/pico-perf-report-template.html).
3) When topic outputs are listed, reads each topic sidecar + its Markdown body
   and assembles the `analysisTopics` array; otherwise injects the bundled
   `analysis_topics` / `analysis_report` directly.
4) If the input has a `header`, overrides the key `reportData.header` fields.
5) If `--report-data` is provided, merges the trace-derived metrics into
   `reportData.quickDiagnosis` / `reportData.details` / `reportData.findings`.
6) Writes the final HTML atomically to `--out`.

This script no longer supports YAML inputs or Markdown front matter; all
machine-readable fields come from the JSON sidecar (`.meta.json`) that lives
next to the Markdown body.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "pico-perf-report-template.html"
DETAILS_KEYS = {
    "app_frame_buckets",
    "app_frame_durations_ms",
    "mesh_draw_call_count_series",
    "mesh_draw_call_count_stats",
    "render_load_counter_groups",
    "spr_frame_buckets",
    "spr_frame_types",
    "spr_cpu_buckets",
    "spr_gpu_buckets",
    "spr_stats",
}


def _load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON file whose top level MUST be an object/map."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON: {path}: {e}") from e

    if not isinstance(data, dict):
        raise SystemExit(f"JSON root must be an object/map: {path}")
    return data


def _read_markdown_body(path: Path) -> str:
    """Read a Markdown body file; reject legacy YAML front matter.

    The new output protocol stores machine-readable fields in a sidecar
    `.meta.json`. Markdown bodies are plain Markdown; a leading `---` block
    is treated as a hard error so legacy producers are caught early.
    """
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        raise SystemExit(
            f"Markdown file {path} starts with '---' and appears to retain YAML front matter."
            " The current contract requires a plain Markdown body; place machine-readable fields in the colocated .meta.json."
        )
    return text


def _normalize_heading(text: str) -> str:
    """Normalize a section heading for tolerant matching.

    Strips a leading section marker (circled number like ``①``, an arabic
    ``1.``/``1)``, or a letter ``A.``/``A)``) and removes all whitespace, so
    that headings differing only by marker style or spacing (e.g. the contract's
    ``① Symptom`` vs a real topic's ``1. Symptom``, or ``Actions
    (Optimization/Troubleshooting)`` vs ``Actions (Optimization /
    Troubleshooting)``) compare as equal.
    """
    t = text.strip()
    t = re.sub(r"^[\u2460-\u2473]\s*", "", t)  # circled digits ①-⑳
    t = re.sub(r"^[0-9]+[.)]\s*", "", t)  # 1. or 1)
    t = re.sub(r"^[A-Za-z][.)]\s*", "", t)  # A. or A)
    t = re.sub(r"\s+", "", t)  # drop all whitespace (handles ` / ` vs `/`)
    return t.lower()


def _extract_section(body: str, title: str) -> str:
    want = _normalize_heading(title)
    for match in re.finditer(
        r"(?ms)^##\s+(.*?)\s*\n(.*?)(?=^##\s+|\Z)", body
    ):
        heading, content = match.group(1), match.group(2)
        if _normalize_heading(heading) == want:
            return content.strip()
    return ""


def _extract_one_line_root_cause(body: str) -> str:
    root_cause_section = _extract_section(body, "④ Root Cause Judgment")
    if not root_cause_section:
        return ""
    for line in root_cause_section.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _build_analysis_report_from_summary(
    summary_header: dict[str, Any], summary_body: str
) -> dict[str, Any]:
    return {
        "symptom": _extract_section(summary_body, "A. Topic Output Index"),
        "evidence": _extract_section(summary_body, "B. Cross-Topic Evidence-Chain Analysis"),
        "investigation": _extract_section(summary_body, "C. Directions to Extend"),
        "rootCause": summary_header.get("root_cause", ""),
        "actions": _extract_section(summary_body, "D. Final Action Plan"),
        "limitations": "\n".join(summary_header.get("limitations", []))
        if isinstance(summary_header.get("limitations"), list)
        else "",
    }


def _default_section_titles() -> dict[str, str]:
    return {
        "symptom": "① Symptom",
        "existing_evidence": "② Existing Evidence",
        "investigation_process": "③ Investigation Process",
        "root_cause_judgment": "④ Root Cause Judgment",
        "actions": "⑤ Actions (Optimization/Troubleshooting)",
        "limitations_and_next_validation": "⑥ Limitations and Next Validation",
    }


def _section_title(meta: dict[str, Any], key: str) -> str:
    defaults = _default_section_titles()
    section_map = meta.get("sections_in_body")
    if isinstance(section_map, dict):
        v = section_map.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return defaults[key]


def _resolve_topic_body_path(meta: dict[str, Any], topic_meta_path: Path) -> Path:
    """Resolve the Markdown body path from a topic meta JSON.

    Preference order: meta.sections_file -> sibling file sharing the basename.
    """
    sections_file = meta.get("sections_file")
    if isinstance(sections_file, str) and sections_file.strip():
        return (topic_meta_path.parent / sections_file).resolve()
    name = topic_meta_path.name
    if name.endswith(".meta.json"):
        md_name = name[: -len(".meta.json")] + ".md"
        return (topic_meta_path.parent / md_name).resolve()
    return topic_meta_path.with_suffix(".md").resolve()


def _build_topic_payload_from_meta(
    meta: dict[str, Any], body_text: str, topic_meta_path: Path
) -> dict[str, Any]:
    """Build a topic payload from a topic meta JSON + its sibling Markdown body."""

    # Evidence: prefer the structured sidecar list; keep only the fields the
    # report topic body shows.
    existing_evidence: list[dict[str, Any]] = []
    meta_evidence = meta.get("evidence")
    if isinstance(meta_evidence, list):
        for item in meta_evidence:
            if not isinstance(item, dict):
                continue
            existing_evidence.append(
                {
                    "type": str(item.get("type", "") or ""),
                    "finding": str(
                        item.get("one_line_finding", item.get("finding", "")) or ""
                    ),
                }
            )

    # Actions: prefer the structured sidecar `next_actions` list; each entry
    # may be a plain string or an object with an "action" field.
    actions: list[str] = []
    meta_actions = meta.get("next_actions")
    if isinstance(meta_actions, list):
        for item in meta_actions:
            if isinstance(item, str):
                actions.append(item)
            elif isinstance(item, dict) and item.get("action"):
                actions.append(str(item["action"]))

    one_line = meta.get("root_cause", "") or _extract_one_line_root_cause(body_text)
    limitations = meta.get("limitations")
    limitations_text = (
        "\n".join(str(x) for x in limitations)
        if isinstance(limitations, list)
        else _extract_section(
            body_text, _section_title(meta, "limitations_and_next_validation")
        )
    )

    report = {
        "symptom": str(meta.get("symptoms", ""))
        or _extract_section(body_text, _section_title(meta, "symptom")),
        "existing_evidence": existing_evidence,
        "investigation_process": _extract_section(
            body_text, _section_title(meta, "investigation_process")
        ),
        "root_cause_judgment": {
            "one_line": one_line,
            "conclusion_level": meta.get("conclusion_level", ""),
            "reasoning": _extract_section(
                body_text, _section_title(meta, "root_cause_judgment")
            ),
        },
        "actions": actions
        or [_extract_section(body_text, _section_title(meta, "actions"))],
        "limitations_and_next_validation": limitations_text,
    }

    stem = topic_meta_path.name
    fallback_topic = (
        stem[: -len(".meta.json")] if stem.endswith(".meta.json") else topic_meta_path.stem
    )
    return {
        "topic": meta.get("protocol", fallback_topic),
        "conclusion_level": meta.get("conclusion_level", ""),
        "report": report,
    }


def _resolve_summary_meta(path: Path) -> dict[str, Any]:
    """Resolve the summary report data from a `final-summary.meta.json` sidecar.

    The sidecar carries all machine-readable fields that used to live in the
    `final-summary.md` YAML front matter. The sibling Markdown body (resolved
    via `meta.sections_file` or the default `final-summary.md`) is only used
    as a fallback source for narrative text when a specific field is missing.
    """
    meta = _load_json_file(path)

    # Locate the summary Markdown body for fallback narrative extraction.
    sections_file = meta.get("sections_file")
    if isinstance(sections_file, str) and sections_file.strip():
        body_path = (path.parent / sections_file).resolve()
    else:
        default_name = (
            path.name[: -len(".meta.json")] + ".md"
            if path.name.endswith(".meta.json")
            else path.stem + ".md"
        )
        body_path = (path.parent / default_name).resolve()
    body = _read_markdown_body(body_path) if body_path.exists() else ""

    # Topic outputs are referenced via their `.meta.json` sidecar paths; the
    # legacy `file: output-*.md` form is no longer accepted.
    topic_outputs = meta.get("topic_outputs")
    analysis_topics: list[dict[str, Any]] = []
    if isinstance(topic_outputs, list):
        for item in topic_outputs:
            if not isinstance(item, dict):
                raise SystemExit("Each topic_outputs item must be an object/map")
            file_value = item.get("file")
            if not isinstance(file_value, str) or not file_value.strip():
                raise SystemExit("Each topic_outputs item must contain a non-empty file")
            if not file_value.endswith(".meta.json"):
                raise SystemExit(
                    f"topic_outputs.file must point to a .meta.json sidecar (received: {file_value})"
                )
            topic_meta_path = (path.parent / file_value).resolve()
            if not topic_meta_path.exists():
                raise SystemExit(f"Topic meta file does not exist: {topic_meta_path}")
            topic_meta = _load_json_file(topic_meta_path)
            topic_body_path = _resolve_topic_body_path(topic_meta, topic_meta_path)
            topic_body = (
                _read_markdown_body(topic_body_path) if topic_body_path.exists() else ""
            )
            analysis_topics.append(
                _build_topic_payload_from_meta(topic_meta, topic_body, topic_meta_path)
            )
        if not analysis_topics:
            raise SystemExit("topic_outputs cannot be empty; generate at least one topic output first")

    # Pass through a header block if the summary meta provides one, so the
    # report shows the real app package / name / time / trace instead of the
    # template's placeholder defaults. Fall back to empty fields otherwise.
    fm_header = meta.get("header") if isinstance(meta.get("header"), dict) else {}
    result: dict[str, Any] = {
        "header": {
            "app_package": str(fm_header.get("app_package", "") or ""),
            "app_name": str(fm_header.get("app_name", "") or ""),
            "analysis_time": str(fm_header.get("analysis_time", "") or ""),
            "trace_file": str(fm_header.get("trace_file", "") or ""),
        }
    }

    if analysis_topics:
        result["analysis_topics"] = analysis_topics
    else:
        result["analysis_report"] = _build_analysis_report_from_summary(meta, body)

    # Recommendations: map the summary meta's `limitations` and `next_actions`
    # to the template's recommendations.{limitations,nextSteps} lists, so the
    # The limitations and next-steps panel shows real data instead of mock placeholders.
    limitations = meta.get("limitations")
    limitations_list = (
        [str(x) for x in limitations] if isinstance(limitations, list) else []
    )
    next_actions = meta.get("next_actions")
    next_steps_list: list[str] = []
    if isinstance(next_actions, list):
        for item in next_actions:
            if isinstance(item, str):
                next_steps_list.append(item)
            elif isinstance(item, dict) and item.get("action"):
                next_steps_list.append(str(item["action"]))
    if limitations_list or next_steps_list:
        result["recommendations"] = {
            "limitations": limitations_list,
            "nextSteps": next_steps_list,
        }

    # Findings: root cause + evidence for the key-findings panel, derived from
    # the summary meta and the referenced topics (not from mock template data).
    findings: dict[str, Any] = {}
    root_cause = meta.get("root_cause")
    if isinstance(root_cause, str) and root_cause.strip():
        conclusion = str(meta.get("conclusion_level", "") or "")
        confidence_map = {
            "confirmed": "High",
            "likely": "Medium",
            "candidate": "Medium",
            "insufficient_evidence": "Medium",
        }
        findings["rootCause"] = {
            "description": root_cause,
            "confidence": confidence_map.get(conclusion, "Medium"),
        }

    # Evidence: pull each topic's structured evidence into flat findings.evidence
    # entries ({type, window, description}).
    evidence_entries: list[dict[str, Any]] = []
    for topic in analysis_topics:
        topic_name = str(topic.get("topic", "") or "")
        for ev in topic.get("report", {}).get("existing_evidence", []):
            if not isinstance(ev, dict):
                continue
            finding = str(ev.get("finding", "") or "")
            if not finding:
                continue
            evidence_entries.append(
                {
                    "type": topic_name or str(ev.get("type", "") or ""),
                    "window": str(ev.get("location", "") or ""),
                    "description": finding,
                }
            )
    if evidence_entries:
        findings["evidence"] = evidence_entries

    if findings:
        result["findings"] = findings

    # Header extras: report summary + active protocols for the top banner.
    # deviceModel/osVersion are blanked unless the summary supplies them, so
    # the banner never shows the template's mock device string.
    header_extras: dict[str, Any] = {
        "deviceModel": str(fm_header.get("device_model", "") or ""),
        "osVersion": str(fm_header.get("os_version", "") or ""),
    }
    summary_text = fm_header.get("summary")
    if isinstance(summary_text, str) and summary_text.strip():
        header_extras["summary"] = summary_text
    active = meta.get("activated_subprotocols")
    if isinstance(active, list) and active:
        header_extras["activeProtocols"] = [str(x) for x in active]
    result["header_extras"] = header_extras

    return result


def _load_input(path: Path) -> dict[str, Any]:
    """Load the top-level analysis input.

    Accepted inputs:
      - `final-summary.meta.json`  : summary sidecar with topic references.
      - `analysis-output.json`     : single-topic analysis output.

    Legacy YAML (`.yaml`/`.yml`) and raw Markdown summaries are no longer
    accepted; the caller is directed to the matching JSON sidecar.
    """
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        raise SystemExit(
            f"YAML input is no longer supported (received: {path}); "
            "use the corresponding JSON (analysis-output.json / final-summary.meta.json)."
        )
    if suffix == ".md":
        raise SystemExit(
            f"Markdown summary is no longer accepted as --input (received: {path}); "
            "use the colocated final-summary.meta.json sidecar."
        )
    if suffix != ".json":
        raise SystemExit(
            f"--input only supports .json (received: {path.suffix or '<no suffix>'})"
        )

    name = path.name
    # A `*.meta.json` sidecar is treated as a summary sidecar; a plain
    # `analysis-output.json` (or other single-topic payloads) is loaded as-is.
    if name.endswith(".meta.json") or name == "final-summary.meta.json":
        return _resolve_summary_meta(path)
    return _load_json_file(path)



def _indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.splitlines())



def _replace_between_anchors(html: str, field_name: str, next_field_name: str, new_value: Any, indent: int = 6) -> str:
    json_text = _indent_block(json.dumps(new_value, ensure_ascii=False, indent=2), indent)
    opening = r"\[" if isinstance(new_value, list) else r"\{"
    closing = r"\]" if isinstance(new_value, list) else r"\}"
    pattern = re.compile(
        rf"(?s)({re.escape(field_name)}\s*:\s*){opening}.*?{closing}(\s*,\s*\n\s*\n\s*{re.escape(next_field_name)}\s*:)"
    )

    match = pattern.search(html)
    if not match:
        raise SystemExit(
            f"Could not find reportData.{field_name} or the {next_field_name} field anchor in the template."
        )

    return pattern.sub(lambda m: m.group(1) + json_text + m.group(2), html, count=1)



def _replace_analysis_report(html: str, analysis_report: dict) -> str:
    return _replace_between_anchors(
        html=html,
        field_name="analysisReport",
        next_field_name="details",
        new_value=analysis_report,
        indent=6,
    )



def _replace_analysis_topics(html: str, analysis_topics: list) -> str:
    return _replace_between_anchors(
        html=html,
        field_name="analysisTopics",
        next_field_name="analysisReport",
        new_value=analysis_topics,
        indent=6,
    )



def _replace_injected_report_data(html: str, injected_report_data: dict) -> str:
    json_text = _indent_block(json.dumps(injected_report_data, ensure_ascii=False, indent=2), 4)
    pattern = re.compile(
        r"(?s)(const\s+injectedReportData\s*=\s*)\{.*?\}(\s*;\s*\n\s*\n\s*const\s+statusMap\s*=)"
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit("Could not find the injectedReportData constant or statusMap anchor in the template.")
    return pattern.sub(lambda m: m.group(1) + json_text + m.group(2), html, count=1)


def _replace_report_data_literal(html: str, report_data: dict[str, Any]) -> str:
    """Replace the complete reportData literal, not individual nested fields.

    The template intentionally contains a readable fallback skeleton, but it
    must never be allowed to leak example topics or numbers into a real report.
    The stable boundary is the next const declaration, rather than nested
    braces inside the JavaScript object.
    """
    json_text = _indent_block(json.dumps(report_data, ensure_ascii=False, indent=2), 6)
    pattern = re.compile(
        r"(?s)(const\s+reportData\s*=\s*)\{.*?(\n\s*\};\s*\n\s*const\s+injectedReportData\s*=)"
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit("Could not find the complete reportData block in the template.")
    suffix = re.sub(r"^(\n\s*)\}", r"\1", match.group(2), count=1)
    return html[: match.start()] + match.group(1) + json_text + suffix + html[match.end() :]


def _empty_report_data() -> dict[str, Any]:
    return {
        "header": {
            "appPackage": "",
            "appName": "Performance Report",
            "deviceModel": "",
            "osVersion": "",
            "analysisTime": "",
            "traceFileName": "",
            "activeProtocols": [],
            "summary": "",
        },
        "quickDiagnosis": {
            "metrics": [],
            "timeline": [],
            "fps": [],
            "appFps": [],
            "sprFps": [],
            "cpuLoad": [],
            "appCpuLoad": [],
            "systemCpuLoad": [],
            "gpuLoad": [],
            "gpuFreq": [],
            "gpuTemp": [],
        },
        "findings": {
            "frameSummary": {"late": 0, "miss": 0, "discard": 0},
            "evidence": [],
            "rootCause": {"description": "", "confidence": ""},
        },
        "analysisTopics": [],
        "analysisReport": {},
        "details": {
            "frameBudgetMs": 11.11,
            "frameDurations": [],
            "app_frame_buckets": {},
            "mesh_draw_call_count_series": [],
            "mesh_draw_call_count_stats": {},
            "render_load_counter_groups": [],
            "spr_frame_buckets": {},
            "spr_frame_types": {},
            "spr_cpu_buckets": {},
            "spr_gpu_buckets": {},
            "spr_stats": {},
        },
        "recommendations": {"limitations": [], "nextSteps": []},
        "footer": {
            "generatedBy": "spatial-app-performance-analysis Skill",
            "protocolVersion": "analysis-protocol v0.4.0 · report-template v0.2.0",
        },
    }


def _assemble_report_data(
    data: dict[str, Any], report_data: dict[str, Any] | None
) -> dict[str, Any]:
    result = _empty_report_data()
    analysis_topics = data.get("analysis_topics")
    if isinstance(analysis_topics, list) and analysis_topics:
        result["analysisTopics"] = analysis_topics
    else:
        analysis_report = data.get("analysis_report")
        if not isinstance(analysis_report, dict):
            raise SystemExit(
                "Input JSON is missing a required field: analysis_topics or analysis_report"
            )
        result["analysisReport"] = analysis_report

    header = data.get("header")
    if isinstance(header, dict):
        mapping = {
            "app_package": "appPackage",
            "app_name": "appName",
            "analysis_time": "analysisTime",
            "trace_file": "traceFileName",
        }
        for meta_key, js_key in mapping.items():
            value = header.get(meta_key)
            if isinstance(value, str):
                result["header"][js_key] = value

    recommendations = data.get("recommendations")
    if isinstance(recommendations, dict):
        result["recommendations"] = {
            "limitations": recommendations.get("limitations", []),
            "nextSteps": recommendations.get("nextSteps", []),
        }
    findings = data.get("findings")
    if isinstance(findings, dict):
        result["findings"].update(findings)
    header_extras = data.get("header_extras")
    if isinstance(header_extras, dict):
        result["header"].update(header_extras)

    if report_data is not None:
        built = _build_injected_report_data(report_data)
        report_meta = report_data.get("meta")
        if isinstance(report_meta, dict):
            app_package = report_meta.get("app_package")
            if isinstance(app_package, str) and app_package.strip():
                result["header"]["appPackage"] = app_package
        result["quickDiagnosis"].update(built["quickDiagnosis"])
        result["details"].update(built["details"])
        result["findings"].update(built["findings"])
    return result


def _validate_generated_html(
    html: str, report_data: dict[str, Any], output_path: Path
) -> None:
    if len(html.encode("utf-8")) == 0:
        raise SystemExit("Generated HTML is empty")
    for topic in report_data.get("analysisTopics", []):
        topic_name = str(topic.get("topic", "") or "")
        if topic_name and topic_name not in html:
            raise SystemExit(f"Generated HTML is missing topic: {topic_name}")
    if '"topic": "Spatial Engine"' in html and "trace_spatial_gallery_20260730_221508" in html:
        raise SystemExit("Generated HTML contains template example topic data")
    if output_path.suffix.lower() != ".html":
        raise SystemExit("HTML output path must end with .html")


def _validate_embedded_javascript(html: str) -> None:
    node = shutil.which("node")
    if node is None:
        raise SystemExit("Cannot validate embedded HTML JavaScript: node was not found")

    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE)
    inline_scripts = [script for script in scripts if script.strip()]
    if not inline_scripts:
        raise SystemExit("Generated HTML does not contain an embedded JavaScript initialization script")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as handle:
        handle.write("\n".join(inline_scripts))
        script_path = Path(handle.name)
    try:
        result = subprocess.run(
            [node, "--check", str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"Generated HTML contains invalid embedded JavaScript syntax: {detail}")



def _replace_recommendations(html: str, recommendations: dict) -> str:
    json_text = _indent_block(
        json.dumps(recommendations, ensure_ascii=False, indent=2), 6
    )
    pattern = re.compile(
        r"(?s)(recommendations\s*:\s*)\{.*?\}(\s*,\s*\n\s*footer\s*:)"
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit("Could not find reportData.recommendations or the footer field anchor in the template.")
    return pattern.sub(lambda m: m.group(1) + json_text + m.group(2), html, count=1)



def _replace_header_field(html: str, js_key: str, new_value: str) -> str:
    pattern = re.compile(
        rf"(?s)(header\s*:\s*\{{[\s\S]*?{re.escape(js_key)}\s*:\s*)\".*?\""
    )

    if not pattern.search(html):
        return html

    return pattern.sub(lambda m: m.group(1) + json.dumps(new_value, ensure_ascii=False), html, count=1)



def _avg(values: list) -> Optional[float]:
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 1)


def _summary_number(summary: dict[str, Any], key: str, stat: str) -> Optional[float]:
    item = summary.get(key)
    if not isinstance(item, dict):
        return None
    value = item.get(stat)
    if not isinstance(value, (int, float)):
        return None
    return round(float(value), 1)


def _series_min(values: list, fallback: float) -> float:
    return min((float(v) for v in values if isinstance(v, (int, float))), default=fallback)


def _series_max(values: list, fallback: float) -> float:
    return max((float(v) for v in values if isinstance(v, (int, float))), default=fallback)


def _build_injected_report_data(report_data: dict) -> dict:
    quick_diagnosis: dict[str, Any] = {}
    details: dict[str, Any] = {}
    findings: dict[str, Any] = {}
    fast_perf_summary = report_data.get("fast_perf_summary")
    if not isinstance(fast_perf_summary, dict):
        fast_perf_summary = {}

    fps_trend = report_data.get("fps_trend")
    app_fps_series: list = []
    spr_fps_series: list = []
    if isinstance(fps_trend, list) and fps_trend:
        quick_diagnosis["timeline"] = [item.get("time") for item in fps_trend]
        app_fps_series = [item.get("app_fps") for item in fps_trend]
        spr_fps_series = [item.get("spr_fps") for item in fps_trend]
        quick_diagnosis["fps"] = app_fps_series
        quick_diagnosis["appFps"] = app_fps_series
        quick_diagnosis["sprFps"] = spr_fps_series

    cpu_gpu_trend = report_data.get("cpu_gpu_trend")
    app_cpu_series: list = []
    system_cpu_series: list = []
    gpu_series: list = []
    gpu_freq_series: list = []
    gpu_temp_series: list = []
    if isinstance(cpu_gpu_trend, list) and cpu_gpu_trend:
        if "timeline" not in quick_diagnosis:
            quick_diagnosis["timeline"] = [item.get("time") for item in cpu_gpu_trend]
        app_cpu_series = [item.get("app_cpu") for item in cpu_gpu_trend]
        system_cpu_series = [item.get("system_cpu") for item in cpu_gpu_trend]
        gpu_series = [item.get("gpu_usage") for item in cpu_gpu_trend]
        gpu_freq_series = [item.get("gpu_freq") for item in cpu_gpu_trend]
        gpu_temp_series = [item.get("gpu_temp") for item in cpu_gpu_trend]
        quick_diagnosis["cpuLoad"] = system_cpu_series or app_cpu_series
        quick_diagnosis["appCpuLoad"] = app_cpu_series
        quick_diagnosis["systemCpuLoad"] = system_cpu_series
        quick_diagnosis["gpuLoad"] = gpu_series
        quick_diagnosis["gpuFreq"] = gpu_freq_series
        quick_diagnosis["gpuTemp"] = gpu_temp_series

    for key in DETAILS_KEYS:
        value = report_data.get(key)
        if isinstance(value, dict):
            details[key] = value
        elif key in {"mesh_draw_call_count_series", "render_load_counter_groups"} and isinstance(value, list):
            details[key] = [item for item in value if isinstance(item, dict)]
        elif key == "app_frame_durations_ms" and isinstance(value, list):
            details["frameDurations"] = [
                float(item) for item in value if isinstance(item, (int, float))
            ]

    # quickDiagnosis.metrics: derive the original seven fast-perf indicators.
    def _status(value: Optional[float], warn: float, bad: float, higher_is_worse: bool) -> str:
        if value is None:
            return "normal"
        if higher_is_worse:
            return "abnormal" if value >= bad else ("warning" if value >= warn else "normal")
        return "abnormal" if value <= bad else ("warning" if value <= warn else "normal")

    metrics: list[dict[str, Any]] = []
    avg_fps = _summary_number(fast_perf_summary, "appFps", "avg") or _avg(app_fps_series)
    if avg_fps is not None:
        min_fps = _summary_number(fast_perf_summary, "appFps", "min")
        if min_fps is None:
            min_fps = _series_min(app_fps_series, avg_fps)
        metrics.append({
            "key": "appFps", "label": "APP FPS", "value": avg_fps, "unit": "fps",
            "status": _status(avg_fps, 80, 60, higher_is_worse=False),
            "description": f"App-side average FPS is {avg_fps}, with a minimum of {min_fps}.",
        })
    avg_spr_fps = _summary_number(fast_perf_summary, "sysFps", "avg") or _avg(spr_fps_series)
    if avg_spr_fps is not None:
        min_spr_fps = _summary_number(fast_perf_summary, "sysFps", "min")
        if min_spr_fps is None:
            min_spr_fps = _series_min(spr_fps_series, avg_spr_fps)
        metrics.append({
            "key": "sprFps", "label": "SPR FPS", "value": avg_spr_fps, "unit": "fps",
            "status": _status(avg_spr_fps, 80, 60, higher_is_worse=False),
            "description": f"SPR-side average FPS is {avg_spr_fps}, with a minimum of {min_spr_fps}.",
        })
    avg_app_cpu = _summary_number(fast_perf_summary, "appCpu", "avg") or _avg(app_cpu_series)
    if avg_app_cpu is not None:
        max_app_cpu = _summary_number(fast_perf_summary, "appCpu", "max")
        if max_app_cpu is None:
            max_app_cpu = _series_max(app_cpu_series, avg_app_cpu)
        metrics.append({
            "key": "appCpu", "label": "APP CPU Load", "value": avg_app_cpu, "unit": "%",
            "status": _status(avg_app_cpu, 75, 90, higher_is_worse=True),
            "description": f"App CPU average load is {avg_app_cpu}%, with a peak of {max_app_cpu}%.",
        })
    avg_system_cpu = _summary_number(fast_perf_summary, "systemCpu", "avg") or _avg(system_cpu_series)
    if avg_system_cpu is not None:
        max_system_cpu = _summary_number(fast_perf_summary, "systemCpu", "max")
        if max_system_cpu is None:
            max_system_cpu = _series_max(system_cpu_series, avg_system_cpu)
        metrics.append({
            "key": "systemCpu", "label": "SPR CPU Load", "value": avg_system_cpu, "unit": "%",
            "status": _status(avg_system_cpu, 90, 150, higher_is_worse=True),
            "description": f"System CPU average load is {avg_system_cpu}%, with a peak of {max_system_cpu}%.",
        })
    avg_gpu = _avg(gpu_series)
    summary_gpu = _summary_number(fast_perf_summary, "gpuUsage", "avg")
    if summary_gpu is not None:
        avg_gpu = summary_gpu
    if avg_gpu is not None:
        max_gpu = _summary_number(fast_perf_summary, "gpuUsage", "max")
        if max_gpu is None:
            max_gpu = _series_max(gpu_series, avg_gpu)
        metrics.append({
            "key": "gpuUsage", "label": "SPR GPU Load", "value": avg_gpu, "unit": "%",
            "status": _status(avg_gpu, 75, 90, higher_is_worse=True),
            "description": f"GPU average load is {avg_gpu}%, with a peak of {max_gpu}%.",
        })
    avg_gpu_freq = _summary_number(fast_perf_summary, "gpuFreq", "avg") or _avg(gpu_freq_series)
    if avg_gpu_freq is not None:
        max_gpu_freq = _summary_number(fast_perf_summary, "gpuFreq", "max")
        if max_gpu_freq is None:
            max_gpu_freq = _series_max(gpu_freq_series, avg_gpu_freq)
        metrics.append({
            "key": "gpuFreq", "label": "GPU Freq", "value": avg_gpu_freq, "unit": "MHz",
            "status": _status(avg_gpu_freq, 800, 900, higher_is_worse=True),
            "description": f"GPU average frequency is {avg_gpu_freq} MHz, with a peak of {max_gpu_freq} MHz.",
        })
    avg_gpu_temp = _summary_number(fast_perf_summary, "gpuTemp", "avg") or _avg(gpu_temp_series)
    if avg_gpu_temp is None:
        end_gpu_temp = _summary_number(fast_perf_summary, "gpuTemp", "end")
        start_gpu_temp = _summary_number(fast_perf_summary, "gpuTemp", "start")
        if end_gpu_temp is not None and start_gpu_temp is not None:
            avg_gpu_temp = round((start_gpu_temp + end_gpu_temp) / 2, 1)
    if avg_gpu_temp is not None:
        max_gpu_temp = _summary_number(fast_perf_summary, "gpuTemp", "max")
        if max_gpu_temp is None:
            max_gpu_temp = _series_max(gpu_temp_series, avg_gpu_temp)
        metrics.append({
            "key": "gpuTemp", "label": "GPU Temp", "value": avg_gpu_temp, "unit": "°C",
            "status": _status(avg_gpu_temp, 72, 78, higher_is_worse=True),
            "description": f"GPU temperature is about {avg_gpu_temp}°C, with a maximum of {max_gpu_temp}°C.",
        })
    if metrics:
        quick_diagnosis["metrics"] = metrics

    # findings.frameSummary: real Late/Miss/Discard counts from spr_frame_types.
    frame_types = report_data.get("spr_frame_types")
    if isinstance(frame_types, dict):
        findings["frameSummary"] = {
            "late": int(frame_types.get("Late", 0) or 0),
            "miss": int(frame_types.get("Miss", 0) or 0),
            "discard": int(frame_types.get("Discard", 0) or 0),
        }

    return {
        "quickDiagnosis": quick_diagnosis,
        "details": details,
        "findings": findings,
    }



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate HTML report from a JSON meta sidecar and an HTML template"
    )
    parser.add_argument(
        "--input",
        required=True,
        help=(
            "JSON input: final-summary.meta.json (summary sidecar) or "
            "analysis-output.json (single-topic analysis output). "
            "Legacy --yaml / Markdown summaries are no longer accepted."
        ),
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE_PATH),
        help="HTML template path (default: ../templates/pico-perf-report-template.html)",
    )
    parser.add_argument("--report-data", help="Path to the JSON file produced by query_report_data.py")
    parser.add_argument("--out", required=True, help="Output HTML path")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    tpl_path = Path(args.template).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Input JSON does not exist: {input_path}")
    if not tpl_path.exists():
        raise SystemExit(f"HTML template does not exist: {tpl_path}")

    data = _load_input(input_path)

    html = tpl_path.read_text(encoding="utf-8")
    report_data: dict[str, Any] | None = None
    if args.report_data:
        report_data_path = Path(args.report_data).expanduser().resolve()
        if not report_data_path.exists():
            raise SystemExit(f"report-data JSON does not exist: {report_data_path}")
        report_data = _load_json_file(report_data_path)

    complete_report_data = _assemble_report_data(data, report_data)
    html = _replace_report_data_literal(html, complete_report_data)
    _validate_generated_html(html, complete_report_data, out_path)
    _validate_embedded_javascript(html)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = out_path.with_name(f".{out_path.name}.tmp-{os.getpid()}")
    try:
        temporary_path.write_text(html, encoding="utf-8")
        os.replace(temporary_path, out_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


if __name__ == "__main__":
    main()
