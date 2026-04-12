"""
Metadata analyzer — extracts all metadata from video files using ffprobe
and checks for red flags indicating tampering, missing police camera data,
and timestamp discrepancies.
"""

import json
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from database import save_metadata_finding, get_metadata_findings
from knowledge_base.violation_patterns import METADATA_RED_FLAGS


# ── ffprobe extraction ────────────────────────────────────────────────────────

def extract_metadata(video_path: str) -> Dict:
    """
    Run ffprobe to get full technical metadata for a video file.
    Returns a dict with 'format' and 'streams' sections.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {"error": f"ffprobe error: {result.stderr}"}
        return json.loads(result.stdout)
    except FileNotFoundError:
        return {"error": "ffprobe not found. Run setup.sh to install ffmpeg."}
    except json.JSONDecodeError:
        return {"error": "Failed to parse ffprobe output"}
    except subprocess.TimeoutExpired:
        return {"error": "ffprobe timed out"}


def get_file_timestamps(video_path: str) -> Dict:
    """Return filesystem creation and modification times."""
    try:
        stat = os.stat(video_path)
        return {
            "fs_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "fs_size_bytes": stat.st_size,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Red flag analysis ─────────────────────────────────────────────────────────

def analyze_metadata(
    evidence_id: str,
    case_id: str,
    video_path: str,
    incident_date: Optional[str] = None,
) -> Dict:
    """
    Full metadata analysis pipeline:
    1. Extract metadata with ffprobe
    2. Extract filesystem timestamps
    3. Check against known red-flag patterns
    4. Store findings in the database
    5. Return structured report
    """
    raw = extract_metadata(video_path)
    fs_info = get_file_timestamps(video_path)
    findings = []

    if "error" in raw:
        return {"error": raw["error"], "findings": []}

    fmt = raw.get("format", {})
    streams = raw.get("streams", [])
    tags = fmt.get("tags", {})

    # ── Collect all metadata values ────────────────────────────────────────
    metadata_report = {
        "filename": fmt.get("filename", video_path),
        "format_name": fmt.get("format_name", "unknown"),
        "format_long_name": fmt.get("format_long_name", ""),
        "duration_seconds": float(fmt.get("duration", 0)),
        "file_size_bytes": int(fmt.get("size", 0)),
        "bit_rate": fmt.get("bit_rate"),
        "creation_time": tags.get("creation_time"),
        "encoder": tags.get("encoder") or tags.get("ENCODER") or tags.get("Software"),
        "comment": tags.get("comment") or tags.get("COMMENT"),
        "streams": [],
    }

    for s in streams:
        stream_info = {
            "index": s.get("index"),
            "codec_type": s.get("codec_type"),
            "codec_name": s.get("codec_name"),
            "width": s.get("width"),
            "height": s.get("height"),
            "r_frame_rate": s.get("r_frame_rate"),
            "avg_frame_rate": s.get("avg_frame_rate"),
            "duration": s.get("duration"),
            "tags": s.get("tags", {}),
        }
        metadata_report["streams"].append(stream_info)

    metadata_report["filesystem"] = fs_info

    # ── Red flag checks ────────────────────────────────────────────────────
    findings.extend(_check_editing_software(evidence_id, case_id, metadata_report, tags))
    findings.extend(_check_timestamp_integrity(evidence_id, case_id, metadata_report, fs_info, incident_date))
    findings.extend(_check_missing_audio(evidence_id, case_id, metadata_report, streams))
    findings.extend(_check_gps_metadata(evidence_id, case_id, metadata_report, tags, streams))
    findings.extend(_check_codec_anomalies(evidence_id, case_id, metadata_report, streams))
    findings.extend(_check_duration(evidence_id, case_id, metadata_report))
    findings.extend(_check_stream_discontinuity(evidence_id, case_id, streams))

    # Save all general metadata entries to DB
    for key, value in {
        "format": fmt.get("format_name"),
        "codec": _get_video_codec(streams),
        "resolution": _get_resolution(streams),
        "duration": f"{metadata_report['duration_seconds']:.2f}s",
        "file_size": f"{metadata_report['file_size_bytes']:,} bytes",
        "creation_time": metadata_report.get("creation_time", "NOT FOUND"),
        "encoder": metadata_report.get("encoder", "NOT FOUND"),
        "fs_modified": fs_info.get("fs_modified"),
    }.items():
        if value:
            save_metadata_finding(
                evidence_id, case_id, key, str(value),
                flag=None, severity=0, note=None
            )

    return {
        "metadata": metadata_report,
        "findings": findings,
        "red_flag_count": sum(1 for f in findings if f["severity"] >= 5),
        "critical_flag_count": sum(1 for f in findings if f["severity"] >= 8),
    }


# ── Individual check functions ────────────────────────────────────────────────

def _check_editing_software(eid, cid, meta, tags) -> List[Dict]:
    findings = []
    encoder = (
        tags.get("encoder", "") or tags.get("ENCODER", "") or
        tags.get("Software", "") or tags.get("software", "") or
        meta.get("encoder", "") or ""
    ).lower()

    editing_keywords = [
        "adobe premiere", "final cut", "davinci resolve", "imovie",
        "vegas pro", "camtasia", "kdenlive", "openshot", "handbrake",
        "avisynth", "virtualdub", "resolve",
    ]

    flagged = [kw for kw in editing_keywords if kw in encoder]
    if flagged:
        note = (
            f"Encoder tag reads: '{encoder}'. "
            f"This is video editing software, suggesting the footage was processed "
            f"in a non-law-enforcement tool before disclosure. "
            f"This is a serious red flag for evidence tampering under 17-A M.R.S.A. §453."
        )
        save_metadata_finding(eid, cid, "encoder_software_flag", encoder,
                              flag="editing_software", severity=9, note=note)
        findings.append({
            "key": "encoder_software_flag",
            "value": encoder,
            "flag": "editing_software",
            "severity": 9,
            "note": note,
            "law": "17-A M.R.S.A. §453 — Tampering with Physical Evidence",
        })

    return findings


def _check_timestamp_integrity(eid, cid, meta, fs_info, incident_date) -> List[Dict]:
    findings = []
    creation_time = meta.get("creation_time")
    fs_modified = fs_info.get("fs_modified")

    if creation_time and fs_modified:
        try:
            ct = datetime.fromisoformat(creation_time.replace("Z", "+00:00"))
            fm = datetime.fromisoformat(fs_modified)
            delta_days = abs((fm.replace(tzinfo=None) - ct.replace(tzinfo=None)).days)
            if delta_days > 1:
                note = (
                    f"File creation metadata says {creation_time}, but the filesystem "
                    f"modification date is {fs_modified} — a {delta_days}-day discrepancy. "
                    f"This may indicate the file was re-encoded or re-saved after recording."
                )
                save_metadata_finding(eid, cid, "timestamp_discrepancy",
                                      f"delta={delta_days} days",
                                      flag="timestamp_gap", severity=7, note=note)
                findings.append({
                    "key": "timestamp_discrepancy",
                    "value": f"{delta_days} days apart",
                    "flag": "timestamp_gap",
                    "severity": 7,
                    "note": note,
                    "law": "17-A M.R.S.A. §453 — Tampering with Physical Evidence",
                })
        except Exception:
            pass

    # Check against incident date
    if incident_date and creation_time:
        try:
            inc = datetime.fromisoformat(incident_date)
            ct = datetime.fromisoformat(creation_time.replace("Z", "+00:00"))
            delta_days = abs((ct.replace(tzinfo=None) - inc.replace(tzinfo=None)).days)
            if delta_days > 30:
                note = (
                    f"Video creation time ({creation_time}) is {delta_days} days from "
                    f"the stated incident date ({incident_date}). This deserves scrutiny."
                )
                save_metadata_finding(eid, cid, "incident_date_mismatch",
                                      f"delta={delta_days} days",
                                      flag="timestamp_gap", severity=5, note=note)
                findings.append({
                    "key": "incident_date_mismatch",
                    "value": f"{delta_days} days",
                    "flag": "timestamp_gap",
                    "severity": 5,
                    "note": note,
                    "law": "Brady v. Maryland (disclosure obligations)",
                })
        except Exception:
            pass

    return findings


def _check_missing_audio(eid, cid, meta, streams) -> List[Dict]:
    findings = []
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    video_streams = [s for s in streams if s.get("codec_type") == "video"]

    if video_streams and not audio_streams:
        note = (
            "This video file contains NO audio track. Law enforcement body cameras "
            "and dashcams are required to record audio. Missing audio may mean it "
            "was stripped — a serious potential violation of evidence preservation duties."
        )
        save_metadata_finding(eid, cid, "missing_audio", "no_audio_stream",
                              flag="missing_audio", severity=7, note=note)
        findings.append({
            "key": "missing_audio",
            "value": "No audio stream found",
            "flag": "missing_audio",
            "severity": 7,
            "note": note,
            "law": "25 M.R.S.A. §2803-B / Brady v. Maryland",
        })

    return findings


def _check_gps_metadata(eid, cid, meta, tags, streams) -> List[Dict]:
    findings = []
    all_tags = dict(tags)
    for s in streams:
        all_tags.update(s.get("tags", {}))

    tag_keys_lower = {k.lower(): v for k, v in all_tags.items()}
    has_gps = any(
        "gps" in k or "location" in k or "geo" in k or "lat" in k or "lon" in k
        for k in tag_keys_lower
    )

    if not has_gps:
        note = (
            "No GPS/location metadata found. Modern police dashcams and body cameras "
            "commonly embed GPS. Absence may mean GPS was stripped, or the device did not "
            "record it. Note for discovery: request the original unprocessed file."
        )
        save_metadata_finding(eid, cid, "no_gps_metadata", "absent",
                              flag="missing_gps", severity=4, note=note)
        findings.append({
            "key": "no_gps_metadata",
            "value": "No GPS tags found",
            "flag": "missing_gps",
            "severity": 4,
            "note": note,
            "law": "25 M.R.S.A. §2803-B (agency recording policy requirements)",
        })

    return findings


def _check_codec_anomalies(eid, cid, meta, streams) -> List[Dict]:
    findings = []
    # Common police camera codecs: h264, hevc/h265
    # Transcoding to a different codec is a red flag
    for s in streams:
        if s.get("codec_type") == "video":
            codec = (s.get("codec_name") or "").lower()
            # Very unusual codecs for police cameras
            suspicious_codecs = ["vp8", "vp9", "av1", "theora", "wmv", "mpeg1video"]
            if codec in suspicious_codecs:
                note = (
                    f"Video uses '{codec}' codec — unusual for law enforcement recording systems. "
                    f"This may indicate the video was transcoded (re-encoded) before disclosure, "
                    f"which can alter or destroy original metadata and quality."
                )
                save_metadata_finding(eid, cid, "unusual_codec", codec,
                                      flag="codec_mismatch", severity=6, note=note)
                findings.append({
                    "key": "unusual_codec",
                    "value": codec,
                    "flag": "codec_mismatch",
                    "severity": 6,
                    "note": note,
                    "law": "17-A M.R.S.A. §453",
                })
    return findings


def _check_duration(eid, cid, meta) -> List[Dict]:
    findings = []
    duration = meta.get("duration_seconds", 0)
    if 0 < duration < 30:
        note = (
            f"Video is only {duration:.1f} seconds long. Police encounters typically last "
            f"several minutes. This extremely short duration may mean footage was truncated "
            f"or the full recording was not provided."
        )
        save_metadata_finding(eid, cid, "very_short_duration", f"{duration:.1f}s",
                              flag="short_duration", severity=6, note=note)
        findings.append({
            "key": "very_short_duration",
            "value": f"{duration:.1f} seconds",
            "flag": "short_duration",
            "severity": 6,
            "note": note,
            "law": "Brady v. Maryland / 25 M.R.S.A. §2803-B",
        })
    return findings


def _check_stream_discontinuity(eid, cid, streams) -> List[Dict]:
    """Check for frame-count vs duration mismatch suggesting cut frames."""
    findings = []
    for s in streams:
        if s.get("codec_type") == "video":
            nb_frames = s.get("nb_frames")
            r_frame_rate = s.get("r_frame_rate", "")
            duration = s.get("duration")
            if nb_frames and r_frame_rate and duration:
                try:
                    num, den = map(int, r_frame_rate.split("/"))
                    fps = num / den
                    expected = fps * float(duration)
                    actual = int(nb_frames)
                    pct_diff = abs(expected - actual) / max(expected, 1) * 100
                    if pct_diff > 10:
                        note = (
                            f"Expected ~{expected:.0f} frames at {fps:.2f} fps for {float(duration):.1f}s "
                            f"but found {actual} frames ({pct_diff:.1f}% discrepancy). "
                            f"This may indicate frames were removed from the video."
                        )
                        save_metadata_finding(eid, cid, "frame_count_anomaly",
                                              f"expected={expected:.0f} actual={actual}",
                                              flag="discontinuous_timestamps", severity=8, note=note)
                        findings.append({
                            "key": "frame_count_anomaly",
                            "value": f"expected≈{expected:.0f}, actual={actual}",
                            "flag": "discontinuous_timestamps",
                            "severity": 8,
                            "note": note,
                            "law": "17-A M.R.S.A. §453 — Tampering with Physical Evidence",
                        })
                except Exception:
                    pass
    return findings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_video_codec(streams: List[Dict]) -> Optional[str]:
    for s in streams:
        if s.get("codec_type") == "video":
            return s.get("codec_name")
    return None


def _get_resolution(streams: List[Dict]) -> Optional[str]:
    for s in streams:
        if s.get("codec_type") == "video":
            w, h = s.get("width"), s.get("height")
            if w and h:
                return f"{w}x{h}"
    return None


def format_metadata_for_display(metadata_report: Dict) -> List[Dict]:
    """Flatten metadata to a list of {label, value} for UI display."""
    items = []
    m = metadata_report
    for label, key in [
        ("File Format", "format_name"),
        ("Duration", None),
        ("File Size", None),
        ("Video Codec", None),
        ("Resolution", None),
        ("Bit Rate", "bit_rate"),
        ("Creation Time", "creation_time"),
        ("Encoder/Software", "encoder"),
        ("Comment", "comment"),
    ]:
        if key:
            val = m.get(key)
        elif label == "Duration":
            secs = m.get("duration_seconds", 0)
            h, r = divmod(int(secs), 3600)
            mi, s = divmod(r, 60)
            val = f"{h:02d}:{mi:02d}:{s:02d} ({secs:.1f}s)"
        elif label == "File Size":
            sz = m.get("file_size_bytes", 0)
            val = f"{sz / (1024*1024):.2f} MB ({sz:,} bytes)"
        elif label == "Video Codec":
            val = _get_video_codec(m.get("streams", []))
        elif label == "Resolution":
            val = _get_resolution(m.get("streams", []))
        else:
            val = None
        items.append({"label": label, "value": val or "N/A"})

    fs = m.get("filesystem", {})
    items.append({"label": "File Last Modified", "value": fs.get("fs_modified", "N/A")})
    return items
