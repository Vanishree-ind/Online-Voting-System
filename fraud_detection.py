"""
fraud_detection.py
==================
Fraud Detection Engine for the Online Voting System.
Analyses vote_log.csv and voterList.csv to detect anomalies.
"""

import pandas as pd
from pathlib import Path
import datetime

path = Path("database")
VOTE_LOG   = path / "vote_log.csv"
VOTER_FILE = path / "voterList.csv"
FRAUD_LOG  = path / "fraud_alerts.csv"

FRAUD_LOG_COLS = ["detected_at", "severity", "type", "voter_id", "detail"]


# ──────────────────────────── helpers ─────────────────────────────────
def _load_vote_log() -> pd.DataFrame:
    if not VOTE_LOG.exists():
        return pd.DataFrame(columns=["voter_id", "timestamp", "candidate"])
    df = pd.read_csv(VOTE_LOG)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def _load_voters() -> pd.DataFrame:
    if not VOTER_FILE.exists():
        return pd.DataFrame(columns=["voter_id", "Name", "Gender",
                                      "Zone", "City", "Passw", "hasVoted"])
    return pd.read_csv(VOTER_FILE)


def _save_fraud_log(alerts: list):
    """Persist fraud alerts to CSV."""
    if not alerts:
        return
    new_df = pd.DataFrame(alerts, columns=FRAUD_LOG_COLS)
    if FRAUD_LOG.exists():
        existing = pd.read_csv(FRAUD_LOG)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(FRAUD_LOG, index=False)


# ──────────────────────────── detection rules ─────────────────────────
def _check_duplicate_votes(log: pd.DataFrame) -> list:
    """
    Rule 1 — Duplicate vote: same voter_id appears more than once in the log.
    """
    alerts = []
    if log.empty:
        return alerts
    counts = log.groupby("voter_id").size()
    dupes = counts[counts > 1]
    for vid, cnt in dupes.items():
        alerts.append({
            "detected_at": datetime.datetime.now().isoformat(),
            "severity":    "HIGH",
            "type":        "Duplicate Vote",
            "voter_id":    int(vid),
            "detail":      f"Voter {vid} has {cnt} vote entries in log.",
        })
    return alerts


def _check_rapid_voting(log: pd.DataFrame, threshold_seconds: int = 5) -> list:
    """
    Rule 2 — Rapid / bot voting: votes cast within `threshold_seconds` of each other.
    """
    alerts = []
    if log.empty or "timestamp" not in log.columns:
        return alerts
    sorted_log = log.dropna(subset=["timestamp"]).sort_values("timestamp")
    if len(sorted_log) < 2:
        return alerts
    diffs = sorted_log["timestamp"].diff().dt.total_seconds()
    rapid = sorted_log[diffs < threshold_seconds]
    for _, row in rapid.iterrows():
        alerts.append({
            "detected_at": datetime.datetime.now().isoformat(),
            "severity":    "MEDIUM",
            "type":        "Rapid Voting",
            "voter_id":    int(row["voter_id"]),
            "detail":      f"Vote cast within {threshold_seconds}s of previous vote at {row['timestamp']}.",
        })
    return alerts


def _check_unregistered_votes(log: pd.DataFrame, voters: pd.DataFrame) -> list:
    """
    Rule 3 — Ghost vote: voter_id in log is not in the registered voter list.
    """
    alerts = []
    if log.empty or voters.empty:
        return alerts
    registered_ids = set(voters["voter_id"].astype(int))
    for _, row in log.iterrows():
        vid = int(row["voter_id"])
        if vid not in registered_ids:
            alerts.append({
                "detected_at": datetime.datetime.now().isoformat(),
                "severity":    "HIGH",
                "type":        "Unregistered Voter",
                "voter_id":    vid,
                "detail":      f"Voter ID {vid} cast a vote but is NOT in voterList.csv.",
            })
    return alerts


def _check_voted_flag_mismatch(log: pd.DataFrame, voters: pd.DataFrame) -> list:
    """
    Rule 4 — Flag mismatch: voter_id is in log but hasVoted == 0 in the database,
    or hasVoted == 1 but no log entry.
    """
    alerts = []
    if voters.empty:
        return alerts
    log_ids  = set(log["voter_id"].astype(int)) if not log.empty else set()
    for _, row in voters.iterrows():
        vid       = int(row["voter_id"])
        has_voted = int(row.get("hasVoted", 0))
        in_log    = vid in log_ids
        if in_log and has_voted == 0:
            alerts.append({
                "detected_at": datetime.datetime.now().isoformat(),
                "severity":    "HIGH",
                "type":        "Flag Mismatch",
                "voter_id":    vid,
                "detail":      f"Voter {vid} has log entry but hasVoted=0 in database.",
            })
        elif not in_log and has_voted == 1:
            alerts.append({
                "detected_at": datetime.datetime.now().isoformat(),
                "severity":    "MEDIUM",
                "type":        "Missing Log Entry",
                "voter_id":    vid,
                "detail":      f"Voter {vid} marked as voted but has no log entry.",
            })
    return alerts


def _check_off_hours_voting(log: pd.DataFrame,
                             start_hour: int = 8,
                             end_hour: int = 20) -> list:
    """
    Rule 5 — Off-hours vote: votes cast outside allowed window.
    """
    alerts = []
    if log.empty or "timestamp" not in log.columns:
        return alerts
    for _, row in log.dropna(subset=["timestamp"]).iterrows():
        h = row["timestamp"].hour
        if not (start_hour <= h < end_hour):
            alerts.append({
                "detected_at": datetime.datetime.now().isoformat(),
                "severity":    "LOW",
                "type":        "Off-Hours Vote",
                "voter_id":    int(row["voter_id"]),
                "detail":      f"Vote cast at {row['timestamp']} — outside {start_hour:02d}:00–{end_hour:02d}:00 window.",
            })
    return alerts


# ──────────────────────────── public API ──────────────────────────────
def run_scan() -> dict:
    """
    Execute all fraud checks. Returns a summary dict:
    {
        "alerts": [...],         # list of alert dicts
        "summary": {...},        # counts by severity / type
        "scanned_at": "...",
    }
    """
    log     = _load_vote_log()
    voters  = _load_voters()

    all_alerts = []
    all_alerts += _check_duplicate_votes(log)
    all_alerts += _check_rapid_voting(log)
    all_alerts += _check_unregistered_votes(log, voters)
    all_alerts += _check_voted_flag_mismatch(log, voters)
    all_alerts += _check_off_hours_voting(log)

    # persist new alerts
    _save_fraud_log(all_alerts)

    severity_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    type_count     = {}
    for a in all_alerts:
        severity_count[a["severity"]] = severity_count.get(a["severity"], 0) + 1
        type_count[a["type"]]          = type_count.get(a["type"], 0) + 1

    return {
        "alerts":     all_alerts,
        "summary":    {"severity": severity_count, "by_type": type_count},
        "total":      len(all_alerts),
        "scanned_at": datetime.datetime.now().isoformat(),
    }


def load_saved_alerts() -> pd.DataFrame:
    """Load all previously-persisted fraud alerts."""
    if not FRAUD_LOG.exists():
        return pd.DataFrame(columns=FRAUD_LOG_COLS)
    return pd.read_csv(FRAUD_LOG)


def clear_fraud_log():
    """Wipe persisted fraud log."""
    if FRAUD_LOG.exists():
        FRAUD_LOG.unlink()
