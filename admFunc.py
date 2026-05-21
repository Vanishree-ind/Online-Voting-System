"""
admFunc.py
==========
Admin utility functions: showVotes, resetAll.
These are called from Admin.py dashboard panels.
"""

import tkinter as tk
from tkinter import *
from tkinter import messagebox
import dframe as df


# ─────────────────────────── palette ──────────────────────────────────
BG      = "#0a0f1e"
CARD    = "#131c31"
CARD2   = "#1a2744"
ACCENT  = "#3b82f6"
GREEN   = "#10b981"
RED     = "#ef4444"
ORANGE  = "#f97316"
TEXT    = "#f1f5f9"
MUTED   = "#64748b"
BORDER  = "#1e3a5f"
GOLD    = "#f59e0b"


# ─────────────────────────── showVotes ────────────────────────────────
def showVotes(root, frame1):
    """
    Display live vote count inside *frame1*.
    Also accepts being called with a standalone root window.
    """
    root.title("Live Vote Count")

    for w in frame1.winfo_children():
        w.destroy()

    frame1.configure(bg=CARD)
    frame1.pack(fill=BOTH, expand=True, padx=20, pady=20)

    Label(frame1, text="📊  Live Vote Count",
          font=("Segoe UI", 20, "bold"), bg=CARD, fg=TEXT).pack(pady=(0, 15))

    try:
        result = df.show_result()
    except Exception as ex:
        Label(frame1, text=f"Error reading results:\n{ex}",
              font=("Segoe UI", 11), bg=CARD, fg=RED).pack(pady=20)
        return

    parties = [
        ("bjp",  "BJP",          ORANGE),
        ("cong", "Congress",     ACCENT),
        ("aap",  "AAP",          "#6366f1"),
        ("ss",   "Shiv Sena",    "#6b7280"),
        ("nota", "NOTA",         MUTED),
    ]

    total = sum(result.values()) or 1

    # try to load party logos
    try:
        from PIL import ImageTk, Image
        import os
        logos = {}
        logo_files = {
            "bjp":  "img/bjp.png",
            "cong": "img/cong.jpg",
            "aap":  "img/aap.png",
            "ss":   "img/ss.png",
            "nota": "img/nota.jpg",
        }
        frame1._logo_refs = []   # keep alive
        for key, path in logo_files.items():
            if os.path.exists(path):
                img = Image.open(path).resize((36, 30), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                logos[key] = photo
                frame1._logo_refs.append(photo)
    except Exception:
        logos = {}

    for key, name, col in parties:
        votes = result.get(key, 0)
        pct   = votes / total * 100

        row = Frame(frame1, bg=CARD2, padx=16, pady=10,
                    highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill=X, pady=4, padx=20)

        # logo (if available)
        if key in logos:
            Label(row, image=logos[key], bg=CARD2).pack(side=LEFT, padx=(0, 10))

        Label(row, text=name,
              font=("Segoe UI", 12, "bold"), bg=CARD2, fg=TEXT, width=14, anchor=W).pack(side=LEFT)

        # bar
        bar_bg = Frame(row, bg=BORDER, height=14, width=260)
        bar_bg.pack(side=LEFT, padx=10)
        bar_bg.pack_propagate(False)
        fill_w = max(2, int(260 * pct / 100))
        Frame(bar_bg, bg=col, height=14, width=fill_w).place(x=0, y=0)

        Label(row, text=f"{votes}  ({pct:.1f}%)",
              font=("Segoe UI", 11, "bold"), bg=CARD2, fg=col, width=16).pack(side=LEFT)

    Label(frame1,
          text=f"Total Votes Cast: {sum(result.values())}",
          font=("Segoe UI", 13, "bold"), bg=CARD, fg=GOLD).pack(pady=14)


# ─────────────────────────── resetAll ─────────────────────────────────
def resetAll(root, frame1):
    """
    Reset all votes and voter 'hasVoted' flags.
    Asks for confirmation first.
    """
    if messagebox.askyesno("Confirm Reset",
                           "Reset ALL votes and voter statuses?\nThis cannot be undone."):
        try:
            df.count_reset()
            for w in frame1.winfo_children():
                w.destroy()
            Label(frame1,
                  text="✅  Election Reset Complete",
                  font=("Segoe UI", 16, "bold"), bg=CARD, fg=GREEN).pack(pady=40)
        except Exception as ex:
            messagebox.showerror("Reset Error", str(ex))
