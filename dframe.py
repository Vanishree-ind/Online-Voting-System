"""
dframe.py
=========
Database layer for the Online Voting System.
Uses pandas + CSV files (backward-compatible with existing database/).
Adds vote timestamp tracking, improved safety, and DateOfBirth / age checks.
"""

import pandas as pd
from pathlib import Path
import datetime

# ── path to database folder ──────────────────────────────────────────
path = Path("database")
path.mkdir(exist_ok=True)

VOTER_FILE = path / "voterList.csv"
CAND_FILE  = path / "cand_list.csv"
VOTE_LOG   = path / "vote_log.csv"

# ── expected columns ─────────────────────────────────────────────────
VOTER_COLS = ["voter_id", "Name", "Gender", "Zone", "City", "Passw", "hasVoted", "DateOfBirth"]
CAND_COLS  = ["Sign", "Name", "Vote Count"]
LOG_COLS   = ["voter_id", "timestamp", "candidate"]


# ─────────────────────────── internal helpers ─────────────────────────
def _load_voters() -> pd.DataFrame:
    df = pd.read_csv(VOTER_FILE)
    # ensure all expected columns exist (backward-compat with old CSVs)
    for col in VOTER_COLS:
        if col not in df.columns:
            df[col] = 0 if col in ("voter_id", "hasVoted") else ""
    return df[VOTER_COLS]


def _save_voters(df: pd.DataFrame):
    df[VOTER_COLS].to_csv(VOTER_FILE, index=False)


def _load_cands() -> pd.DataFrame:
    df = pd.read_csv(CAND_FILE)
    for col in CAND_COLS:
        if col not in df.columns:
            df[col] = 0 if col == "Vote Count" else ""
    return df[CAND_COLS]


def _save_cands(df: pd.DataFrame):
    df[CAND_COLS].to_csv(CAND_FILE, index=False)


def _log_vote(voter_id: int, candidate: str):
    """Append a vote event to the audit log."""
    try:
        ts = datetime.datetime.now().isoformat()
        row = pd.DataFrame({"voter_id": [voter_id],
                            "timestamp": [ts],
                            "candidate": [candidate]})
        if VOTE_LOG.exists():
            existing = pd.read_csv(VOTE_LOG)
            combined = pd.concat([existing, row], ignore_index=True)
        else:
            combined = row
        combined[LOG_COLS].to_csv(VOTE_LOG, index=False)
    except Exception:
        pass   # logging failure must never break voting


# ─────────────────────────── age helpers ─────────────────────────────
def calculate_age(dob_str: str) -> int:
    """
    Calculate exact age in years from a date string (YYYY-MM-DD).
    Returns -1 if the string is invalid.
    """
    try:
        dob   = datetime.date.fromisoformat(str(dob_str).strip())
        today = datetime.date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
    except Exception:
        return -1


def is_eligible_age(dob_str: str) -> bool:
    """Return True only if the person is 18 years old or older."""
    return calculate_age(dob_str) >= 18


# ─────────────────────────── public API ───────────────────────────────
def verify(vid: int, passw: str) -> bool:
    """Return True if voter_id + password match a record."""
    try:
        df = _load_voters()
        match = df[(df["voter_id"] == vid) & (df["Passw"] == passw)]
        return not match.empty
    except Exception:
        return False


def isEligible(vid: int) -> bool:
    """Return True if the voter exists and has NOT yet voted."""
    try:
        df = _load_voters()
        match = df[(df["voter_id"] == vid) & (df["hasVoted"] == 0)]
        return not match.empty
    except Exception:
        return False


def vote_update(sign: str, vid: int) -> bool:
    """
    Record the vote:
    1. Increment the candidate's vote count.
    2. Mark the voter as having voted.
    3. Write an audit log entry.
    Returns True on success, False otherwise.
    """
    if not isEligible(vid):
        return False
    try:
        cands = _load_cands()
        idx = cands.index[cands["Sign"] == sign].tolist()
        if not idx:
            return False
        cands.loc[idx[0], "Vote Count"] += 1
        _save_cands(cands)

        voters = _load_voters()
        v_idx = voters.index[voters["voter_id"] == vid].tolist()
        if v_idx:
            voters.loc[v_idx[0], "hasVoted"] = 1
            _save_voters(voters)

        _log_vote(vid, sign)
        return True
    except Exception:
        return False


def show_result() -> dict:
    """Return {sign: vote_count} for all candidates."""
    try:
        df = _load_cands()
        return dict(zip(df["Sign"], df["Vote Count"].astype(int)))
    except Exception:
        return {}


def taking_data_voter(name: str, gender: str, zone: str,
                      city: str, passw: str, dob: str) -> int:
    """
    Add a new voter; returns the assigned voter_id.
    dob must be a YYYY-MM-DD string already validated by is_eligible_age().
    """
    df_voters = _load_voters()
    if df_voters.empty:
        vid = 10001
    else:
        vid = int(df_voters["voter_id"].max()) + 1

    new_row = pd.DataFrame({
        "voter_id":    [vid],
        "Name":        [name],
        "Gender":      [gender],
        "Zone":        [zone],
        "City":        [city],
        "Passw":       [passw],
        "hasVoted":    [0],
        "DateOfBirth": [dob],
    })
    combined = pd.concat([df_voters, new_row], ignore_index=True)
    _save_voters(combined)
    return vid


def count_reset():
    """Reset all vote counts and mark all voters as not-voted."""
    try:
        voters = _load_voters()
        voters["hasVoted"] = 0
        _save_voters(voters)

        cands = _load_cands()
        cands["Vote Count"] = 0
        _save_cands(cands)

        if VOTE_LOG.exists():
            VOTE_LOG.unlink()
    except Exception as ex:
        raise RuntimeError(f"Reset failed: {ex}") from ex


def reset_voter_list():
    """Delete all registered voters."""
    df = pd.DataFrame(columns=VOTER_COLS)
    df.to_csv(VOTER_FILE, index=False)


def reset_cand_list():
    """Reset candidate list to empty."""
    df = pd.DataFrame(columns=CAND_COLS)
    df.to_csv(CAND_FILE, index=False)
