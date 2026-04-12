"""
Core video analyzer.

Extracts real video frames using ffmpeg and sends them to the Claude vision API
so the model *literally watches* the footage — not just reads the filename.

Findings are stored in the persistent database for the case.
"""

import os
import base64
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
import anthropic

from config import config
from database import (
    update_analysis, save_violation, new_id
)
from knowledge_base.maine_laws import get_maine_laws_for_date
from knowledge_base.federal_laws import FEDERAL_LAWS
from knowledge_base.violation_patterns import VIOLATION_PATTERNS


# ── Frame extraction ──────────────────────────────────────────────────────────

def get_video_duration(video_path: str) -> float:
    """Return video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def extract_frames(
    video_path: str,
    interval: int = None,
    max_frames: int = 120,
    progress_callback: Optional[Callable] = None,
) -> List[Dict]:
    """
    Extract frames from video using ffmpeg.

    Returns a list of dicts:
      { "timestamp": float (seconds), "data": base64_string, "mime": "image/jpeg" }

    Automatically limits frame count for very long videos so API costs stay reasonable.
    """
    if interval is None:
        interval = config.VIDEO_FRAME_INTERVAL

    duration = get_video_duration(video_path)
    if duration > 0:
        # Compute interval to stay under max_frames
        min_interval = max(1, int(duration / max_frames))
        interval = max(interval, min_interval)

    frames = []
    max_dim = config.MAX_FRAME_SIZE

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pattern = os.path.join(tmpdir, "frame_%06d.jpg")
        # -q:v 3 = good JPEG quality; scale to max_dim without upscaling
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", (
                f"fps=1/{interval},"
                f"scale='if(gt(iw,{max_dim}),{max_dim},iw)':"
                f"'if(gt(ih,{max_dim}),{max_dim},ih)':force_original_aspect_ratio=decrease"
            ),
            "-q:v", "3",
            out_pattern,
            "-hide_banner", "-loglevel", "error"
        ]
        try:
            subprocess.run(cmd, check=True, timeout=600)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg frame extraction failed: {e}")
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Run setup.sh to install it, or install manually: "
                "sudo apt-get install ffmpeg"
            )

        frame_files = sorted(f for f in os.listdir(tmpdir) if f.endswith(".jpg"))
        total = len(frame_files)

        for idx, fname in enumerate(frame_files):
            frame_path = os.path.join(tmpdir, fname)
            with open(frame_path, "rb") as fh:
                b64 = base64.standard_b64encode(fh.read()).decode("utf-8")

            # Frame index (1-based) → timestamp
            frame_num = int(fname.split("_")[1].split(".")[0])
            timestamp = (frame_num - 1) * interval

            frames.append({
                "timestamp": timestamp,
                "timestamp_label": _fmt_timestamp(timestamp),
                "data": b64,
                "mime": "image/jpeg",
            })

            if progress_callback:
                progress_callback(idx + 1, total, "extracting_frames")

    return frames


def _fmt_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string."""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


# ── Claude vision analysis ────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a forensic legal video analyst specializing in police misconduct and civil rights violations. You are assisting a pro se defendant (self-represented person) who cannot afford a lawyer. Your job is to look at each video frame with extreme care and report ONLY what you actually see — no speculation, no invented details.

Your analysis must be:
1. FACTUAL — describe only visible elements
2. PRECISE — include exact timestamp
3. LEGALLY GROUNDED — cite the specific statute or case law
4. HONEST about uncertainty — if you cannot tell, say so with confidence: "low"
5. STRUCTURED — return valid JSON every time

You will be shown frames from police dashcam, body camera, or other law enforcement video footage.

For each frame, check for:
• Officer identification (badge, name tag, uniform number visible?)
• Miranda warning given or clearly not given during custody
• Use of force (weapon drawn? physical contact? justified or disproportionate?)
• Search or seizure of person, vehicle, or property
• Consent given or withheld
• Evidence handling procedures
• Camera/recording manipulation (turning off camera, covering lens)
• Witness presence
• Subject demeanor and compliance level
• Any other legally significant observable detail

Return ONLY valid JSON (no prose before or after) in this exact schema:
{
  "timestamp": "<HH:MM:SS>",
  "scene_description": "<factual 1-2 sentence description of what is visible>",
  "officer_count": <integer or null>,
  "subject_count": <integer or null>,
  "observations": ["<factual observation 1>", "..."],
  "potential_violations": [
    {
      "type": "<violation_type_slug>",
      "description": "<what you see that raises this issue>",
      "law_reference": "<e.g. 4th Amendment / 42 U.S.C. §1983 / 17-A M.R.S.A. §107>",
      "law_title": "<short title>",
      "severity": <1-10>,
      "confidence": "<high|medium|low>",
      "is_illegal": <true|false>,
      "is_red_flag": <true|false>
    }
  ],
  "force_used": <true|false|null>,
  "search_conducted": <true|false|null>,
  "miranda_given": <true|false|null>,
  "camera_issues": <true|false>,
  "evidence_handling_visible": <true|false>,
  "notes": "<any additional important observations>"
}
If there are no violations or concerns, return an empty "potential_violations" array.
"""


def _build_law_context(incident_date: Optional[str]) -> str:
    """Compile a brief law reference for the AI prompt."""
    maine = get_maine_laws_for_date(incident_date or "2000-01-01")
    lines = ["APPLICABLE MAINE LAWS:"]
    for law in maine[:6]:  # Top 6 most relevant
        lines.append(f"• {law['title']}: {law['full_text'][:200]}…")
    lines.append("\nKEY FEDERAL LAWS:")
    for law in FEDERAL_LAWS[:4]:
        lines.append(f"• {law['title']}: {law['full_text'][:200]}…")
    return "\n".join(lines)


def analyze_frame_batch(
    frames: List[Dict],
    client: anthropic.Anthropic,
    incident_date: Optional[str] = None,
) -> List[Dict]:
    """
    Send a batch of frames to Claude and parse the JSON responses.
    Returns a list of parsed result dicts (one per frame).
    """
    law_context = _build_law_context(incident_date)
    results = []

    for frame in frames:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Analyze this police video frame at timestamp {frame['timestamp_label']}.\n\n"
                            f"VIDEO TIMESTAMP: {frame['timestamp_label']} "
                            f"({frame['timestamp']:.1f} seconds into video)\n\n"
                            f"{law_context}\n\n"
                            "Return ONLY valid JSON as specified. Be factual. "
                            "Only report what you literally see in this frame."
                        ),
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": frame["mime"],
                            "data": frame["data"],
                        },
                    },
                ],
            }
        ]

        try:
            response = client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            raw = response.content[0].text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            parsed = json.loads(raw)
            parsed["_timestamp"] = frame["timestamp"]
            parsed["_timestamp_label"] = frame["timestamp_label"]
            results.append(parsed)
        except json.JSONDecodeError:
            # If Claude doesn't return clean JSON, wrap it
            results.append({
                "_timestamp": frame["timestamp"],
                "_timestamp_label": frame["timestamp_label"],
                "parse_error": True,
                "raw_response": raw[:500] if 'raw' in dir() else "No response",
                "potential_violations": [],
                "observations": ["Frame could not be auto-parsed — review raw response."],
            })
        except anthropic.RateLimitError:
            time.sleep(10)
            results.append({
                "_timestamp": frame["timestamp"],
                "_timestamp_label": frame["timestamp_label"],
                "rate_limited": True,
                "potential_violations": [],
                "observations": ["Rate limited — this frame was skipped."],
            })
        except Exception as exc:
            results.append({
                "_timestamp": frame["timestamp"],
                "_timestamp_label": frame["timestamp_label"],
                "error": str(exc),
                "potential_violations": [],
                "observations": [],
            })

        # Brief pause between frames to respect rate limits
        time.sleep(0.5)

    return results


# ── Full video analysis pipeline ──────────────────────────────────────────────

def analyze_video(
    analysis_id: str,
    evidence_id: str,
    case_id: str,
    video_path: str,
    incident_date: Optional[str] = None,
    interval: int = None,
    progress_callback: Optional[Callable] = None,
) -> Dict:
    """
    Full pipeline:
    1. Extract frames
    2. Analyze each frame with Claude vision
    3. Aggregate violations
    4. Store in database
    5. Return summary

    progress_callback(step: int, total: int, phase: str) is called frequently.
    """
    if not config.is_configured:
        raise ValueError(
            "No API key configured. Add ANTHROPIC_API_KEY (from console.anthropic.com) "
            "or OPENROUTER_API_KEY (from openrouter.ai) to your .env file."
        )

    # Build Anthropic client — works for both direct Anthropic and OpenRouter
    client_kwargs = {"api_key": config.active_api_key}
    if config.api_base_url:
        client_kwargs["base_url"] = config.api_base_url
        client_kwargs["default_headers"] = {
            "HTTP-Referer": "https://github.com/legal-video-analyzer",
            "X-Title": "Legal Video Analyzer — Pro Se Defense Tool",
        }
    client = anthropic.Anthropic(**client_kwargs)

    update_analysis(analysis_id, status="running", progress=5)

    # ── Phase 1: Extract frames ────────────────────────────────────────────────
    def frame_progress(done, total, phase):
        pct = int(5 + (done / max(total, 1)) * 35)  # 5% → 40%
        update_analysis(analysis_id, progress=pct)
        if progress_callback:
            progress_callback(done, total, phase)

    try:
        frames = extract_frames(video_path, interval=interval, progress_callback=frame_progress)
    except Exception as exc:
        update_analysis(analysis_id, status="failed", error_message=str(exc))
        return {"error": str(exc)}

    total_frames = len(frames)
    if total_frames == 0:
        update_analysis(analysis_id, status="failed", error_message="No frames could be extracted from video.")
        return {"error": "No frames extracted"}

    update_analysis(analysis_id, progress=40)

    # ── Phase 2: Analyze each frame ───────────────────────────────────────────
    all_frame_results = []
    batch_size = config.FRAMES_PER_BATCH
    batches = [frames[i:i + batch_size] for i in range(0, len(frames), batch_size)]
    n_batches = len(batches)

    for b_idx, batch in enumerate(batches):
        batch_results = analyze_frame_batch(batch, client, incident_date)
        all_frame_results.extend(batch_results)
        pct = int(40 + ((b_idx + 1) / n_batches) * 45)  # 40% → 85%
        update_analysis(analysis_id, progress=pct)
        if progress_callback:
            progress_callback(b_idx + 1, n_batches, "analyzing_frames")
        # Respect API rate limits between batches
        if b_idx < n_batches - 1:
            time.sleep(1)

    update_analysis(analysis_id, progress=85)

    # ── Phase 3: Aggregate violations ─────────────────────────────────────────
    all_violations = []
    timeline = []

    for frame_result in all_frame_results:
        ts = frame_result.get("_timestamp", 0)
        ts_label = frame_result.get("_timestamp_label", _fmt_timestamp(ts))

        # Build timeline entry
        scene = frame_result.get("scene_description", "")
        obs = frame_result.get("observations", [])
        flags = frame_result.get("potential_violations", [])

        timeline.append({
            "timestamp": ts,
            "timestamp_label": ts_label,
            "scene_description": scene,
            "observations": obs,
            "violation_count": len(flags),
            "force_used": frame_result.get("force_used"),
            "search_conducted": frame_result.get("search_conducted"),
            "miranda_given": frame_result.get("miranda_given"),
            "camera_issues": frame_result.get("camera_issues", False),
        })

        # Persist each violation
        for v in flags:
            v_data = {
                "violation_type": v.get("type"),
                "category": v.get("type", "").split("_")[0] if v.get("type") else None,
                "severity": v.get("severity", 5),
                "confidence": v.get("confidence", "low"),
                "description": v.get("description"),
                "timestamp_secs": ts,
                "timestamp_label": ts_label,
                "law_reference": v.get("law_reference"),
                "law_title": v.get("law_title"),
                "recommendation": _get_recommendation(v.get("type", "")),
                "is_illegal": v.get("is_illegal", False),
                "is_red_flag": v.get("is_red_flag", True),
            }
            save_violation(analysis_id, case_id, v_data)
            all_violations.append(v_data)

    # ── Phase 4: Compute summary metrics ──────────────────────────────────────
    win_prob = _calculate_win_probability(all_violations)
    miranda_events = [f for f in all_frame_results if f.get("miranda_given") is False]
    force_events = [f for f in all_frame_results if f.get("force_used") is True]
    search_events = [f for f in all_frame_results if f.get("search_conducted") is True]
    camera_issue_events = [f for f in all_frame_results if f.get("camera_issues") is True]

    summary = {
        "total_frames_analyzed": total_frames,
        "total_violations_found": len(all_violations),
        "illegal_violations": sum(1 for v in all_violations if v.get("is_illegal")),
        "red_flags": sum(1 for v in all_violations if v.get("is_red_flag")),
        "win_probability": win_prob["probability"],
        "win_probability_pct": win_prob["percentage"],
        "win_probability_factors": win_prob["factors"],
        "win_probability_disclaimer": win_prob["disclaimer"],
        "miranda_concern": len(miranda_events) > 0,
        "force_used": len(force_events) > 0,
        "search_conducted": len(search_events) > 0,
        "camera_issues_detected": len(camera_issue_events) > 0,
        "timeline": timeline,
        "violations_by_severity": _group_by_severity(all_violations),
        "recommendations": _generate_recommendations(all_violations),
    }

    # Persist
    update_analysis(
        analysis_id,
        status="complete",
        progress=100,
        results_json=summary,
        win_probability=win_prob["probability"],
        completed_at=__import__("datetime").datetime.utcnow().isoformat(),
    )

    return summary


# ── Win probability ───────────────────────────────────────────────────────────

def _calculate_win_probability(violations: List[Dict]) -> Dict:
    """
    Evidence-based win probability estimate.
    Transparent formula — every boost factor is reported.
    """
    base = 0.28  # Realistic base for unrepresented criminal defendant
    factors = []

    severity_boosts = {
        10: 0.18,
        9: 0.14,
        8: 0.10,
        7: 0.07,
        6: 0.05,
        5: 0.03,
    }
    confidence_mult = {"high": 1.0, "medium": 0.70, "low": 0.35}

    seen_types = set()
    for v in violations:
        sev = v.get("severity", 0)
        conf = v.get("confidence", "low")
        vtype = v.get("violation_type", "unknown")
        boost = severity_boosts.get(min(sev, 10), 0.02)
        boost *= confidence_mult.get(conf, 0.35)

        # Deduplicate violation type boosts (don't count same type 20 times)
        if vtype not in seen_types:
            base += boost
            seen_types.add(vtype)
            factors.append({
                "factor": v.get("description", vtype),
                "law": v.get("law_reference", ""),
                "impact": f"+{boost * 100:.1f}%",
                "confidence": conf,
            })

    # Special categorical bonuses
    vtypes = {v.get("violation_type", "") for v in violations}

    if any("miranda" in t for t in vtypes):
        base += 0.12
        factors.append({"factor": "Miranda violation documented", "impact": "+12.0%",
                         "law": "Miranda v. Arizona", "confidence": "high"})

    if any("search" in t or "seizure" in t for t in vtypes):
        base += 0.10
        factors.append({"factor": "4th Amendment search/seizure issue", "impact": "+10.0%",
                         "law": "4th Amendment", "confidence": "high"})

    if any("camera" in t or "tamper" in t for t in vtypes):
        base += 0.15
        factors.append({"factor": "Camera deactivation / tampering evidence", "impact": "+15.0%",
                         "law": "17-A M.R.S.A. §453", "confidence": "high"})

    if any("force" in t for t in vtypes):
        base += 0.08
        factors.append({"factor": "Excessive force indicators present", "impact": "+8.0%",
                         "law": "Graham v. Connor / 42 U.S.C. §1983", "confidence": "medium"})

    probability = round(min(base, 0.93), 4)

    return {
        "probability": probability,
        "percentage": f"{probability * 100:.1f}%",
        "factors": factors,
        "disclaimer": (
            "THIS IS AN AI-GENERATED ESTIMATE ONLY. It is NOT legal advice and NOT a "
            "guarantee of any outcome. Actual results depend on the specific judge, "
            "prosecutor, evidence admissibility, witness credibility, and many other "
            "factors. If at all possible, consult a licensed attorney or contact "
            "Maine Legal Services (207-622-4731) or Pine Tree Legal Assistance."
        ),
    }


def _group_by_severity(violations: List[Dict]) -> Dict:
    groups = {"critical": [], "serious": [], "moderate": [], "minor": []}
    for v in violations:
        sev = v.get("severity", 0)
        if sev >= 9:
            groups["critical"].append(v)
        elif sev >= 7:
            groups["serious"].append(v)
        elif sev >= 5:
            groups["moderate"].append(v)
        else:
            groups["minor"].append(v)
    return {k: len(v) for k, v in groups.items()}


def _get_recommendation(vtype: str) -> str:
    recs = {
        "miranda": "File a Motion to Suppress all statements made during custodial interrogation.",
        "search": "File a Motion to Suppress all evidence obtained from the illegal search.",
        "seizure": "File a Motion to Suppress the seized items; challenge probable cause.",
        "force": "Document all injuries with photographs. File 42 U.S.C. §1983 civil rights claim.",
        "camera": "Request all camera records in discovery; file adverse inference motion.",
        "tamper": "Report to state attorney general and FBI civil rights division immediately.",
        "arrest": "Challenge probable cause at arraignment. Request all body cam footage.",
        "discrimination": "File complaint with Maine Human Rights Commission and DOJ Civil Rights.",
    }
    for key, rec in recs.items():
        if key in vtype.lower():
            return rec
    return "Preserve evidence. Consult Maine Legal Services (207-622-4731)."


def _generate_recommendations(violations: List[Dict]) -> List[str]:
    """Return a deduplicated list of top recommendations."""
    seen = set()
    recs = []
    for v in sorted(violations, key=lambda x: x.get("severity", 0), reverse=True):
        rec = v.get("recommendation") or _get_recommendation(v.get("violation_type", ""))
        if rec and rec not in seen:
            seen.add(rec)
            recs.append(rec)
    # Always add these baseline items
    base_recs = [
        "Request ALL video footage (dashcam, body cam, dispatch recordings) via discovery request immediately.",
        "File a written demand for preservation of all evidence — do this TODAY to prevent deletion.",
        "Contact Maine Legal Services (1-800-750-5353) or Pine Tree Legal Assistance (207-774-8211) for free legal help.",
    ]
    for r in base_recs:
        if r not in seen:
            recs.append(r)
    return recs
