"""
Admin.py
========
Admin login page and full Admin Dashboard with all management features.
"""

import subprocess as sb_p
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import threading


# ─────────────────────────── palette ──────────────────────────────────
BG      = "#0a0f1e"
CARD    = "#131c31"
CARD2   = "#1a2744"
ACCENT  = "#3b82f6"
GREEN   = "#10b981"
RED     = "#ef4444"
ORANGE  = "#f97316"
GOLD    = "#f59e0b"
TEXT    = "#f1f5f9"
MUTED   = "#64748b"
BORDER  = "#1e3a5f"
ACCENT2 = "#06b6d4"


# ─────────────────────────── helpers ──────────────────────────────────
def _darken(hex_color, amount=20):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,r-amount):02x}{max(0,g-amount):02x}{max(0,b-amount):02x}"


def styled_btn(parent, text, cmd, color=ACCENT, width=22, pady=10, font_size=11):
    """Flat modern button with hover."""
    btn = Button(
        parent, text=text, command=cmd,
        bg=color, fg=TEXT, activebackground=_darken(color),
        activeforeground=TEXT,
        font=("Segoe UI", font_size, "bold"),
        width=width, pady=pady, bd=0, cursor="hand2", relief="flat"
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_darken(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def section_label(parent, text):
    Label(parent, text=text,
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(anchor=W, padx=5)


def _centre(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────── Admin Login ──────────────────────────────
def AdmLogin(root, frame1):
    """Render the admin login form inside *frame1*."""

    root.title("Admin Login — Online Voting System")
    root.geometry("1000x680")
    root.configure(bg=BG)
    _centre(root, 1000, 680)

    # clear
    for w in root.winfo_children():
        w.destroy()

    # top bar
    topbar = Frame(root, bg=CARD2, pady=8)
    topbar.pack(fill=X)
    Label(topbar, text="🗳️  Online Voting System  ›  Admin Login",
          font=("Segoe UI", 12, "bold"), bg=CARD2, fg=TEXT).pack(side=LEFT, padx=18)

    # centre card
    outer = Frame(root, bg=BG)
    outer.pack(expand=True)

    card = Frame(outer, bg=CARD, padx=60, pady=50,
                 highlightbackground=BORDER, highlightthickness=2)
    card.pack()

    Label(card, text="🔐", font=("Segoe UI Emoji", 40), bg=CARD).pack()
    Label(card, text="ADMIN LOGIN",
          font=("Segoe UI", 22, "bold"), bg=CARD, fg=TEXT).pack(pady=(8, 2))
    Label(card, text="Enter your credentials to continue",
          font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(pady=(0, 20))

    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=6)

    # form fields
    admin_ID = tk.StringVar()
    password = tk.StringVar()
    error_var = tk.StringVar()

    _form_field(card, "Username", admin_ID)
    _form_field(card, "Password", password, show="*")

    # error label
    err_lbl = Label(card, textvariable=error_var,
                    font=("Segoe UI", 10, "bold"), bg=CARD, fg=RED)
    err_lbl.pack(pady=(4, 0))

    def do_login():
        error_var.set("")
        uid = admin_ID.get().strip()
        pwd = password.get().strip()
        if not uid or not pwd:
            error_var.set("⚠  Please fill in both fields.")
            return
        log_admin(root, uid, pwd)

    styled_btn(card, "🔓  Login", do_login, color=ACCENT,
               width=24, font_size=12).pack(pady=18)
    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=4)
    styled_btn(card, "← Back to Home", lambda: _go_home(root),
               color=CARD2, width=24, font_size=10).pack(pady=6)


def _form_field(parent, label, var, show=None):
    """Label + styled Entry pair."""
    Label(parent, text=label,
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(anchor=W, pady=(10, 2))
    kw = dict(textvariable=var, font=("Segoe UI", 12),
              width=28, bg=CARD2, fg=TEXT,
              insertbackground=TEXT, relief="flat",
              highlightbackground=BORDER, highlightthickness=1)
    if show:
        kw["show"] = show
    Entry(parent, **kw).pack(ipady=8)


# ─────────────────────────── Auth ─────────────────────────────────────
def log_admin(root, admin_ID, password):
    """Validate credentials and open dashboard."""
    if admin_ID == "Admin" and password == "admin":
        AdminHome(root)
    else:
        messagebox.showerror("Login Failed",
                             "Invalid username or password.\n"
                             "Default: Admin / admin")


# ─────────────────────────── Dashboard ────────────────────────────────
_server_process = None      # track the server subprocess


def AdminHome(root):
    """Full admin dashboard."""
    root.title("Admin Dashboard — Online Voting System")
    root.geometry("1100x720")
    _centre(root, 1100, 720)
    root.configure(bg=BG)

    for w in root.winfo_children():
        w.destroy()

    # ── top bar ──────────────────────────────────────────────────────
    topbar = Frame(root, bg=CARD2, pady=10)
    topbar.pack(fill=X)
    Label(topbar, text="🗳️  Admin Dashboard",
          font=("Segoe UI", 14, "bold"), bg=CARD2, fg=TEXT).pack(side=LEFT, padx=18)
    styled_btn(topbar, "← Home", lambda: _go_home(root),
               color=MUTED, width=12, pady=4, font_size=10).pack(side=RIGHT, padx=12)

    # ── main body (sidebar + content) ────────────────────────────────
    body = Frame(root, bg=BG)
    body.pack(fill=BOTH, expand=True, padx=20, pady=18)

    sidebar = Frame(body, bg=CARD, width=220,
                    highlightbackground=BORDER, highlightthickness=1)
    sidebar.pack(side=LEFT, fill=Y, padx=(0, 18))
    sidebar.pack_propagate(False)

    content = Frame(body, bg=CARD,
                    highlightbackground=BORDER, highlightthickness=1)
    content.pack(side=LEFT, fill=BOTH, expand=True)

    # ── sidebar buttons ──────────────────────────────────────────────
    Label(sidebar, text="MENU",
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(pady=(20, 8))

    menus = [
        ("🟢  Run Server",         lambda: _run_server(content),        GREEN),
        ("🔴  Stop Server",        lambda: _stop_server(content),       RED),
        ("➕  Register Voter",     lambda: _open_register(root, content), ACCENT),
        ("📋  View Voters",        lambda: _view_voters(content),       ACCENT2),
        ("📊  Live Vote Count",    lambda: _show_votes(content),        GOLD),
        ("📈  Results Graph",      lambda: _show_graph(content),        ORANGE),
        ("🛡️  Fraud Detection",    lambda: _show_fraud(content),        "#a855f7"),
        ("🔄  Reset Election",     lambda: _reset_election(content),    RED),
        ("💾  Export Results",     lambda: _export_results(content),    GREEN),
    ]

    for txt, cmd, col in menus:
        b = Button(
            sidebar, text=txt, command=cmd,
            bg=CARD, fg=TEXT, activebackground=CARD2,
            font=("Segoe UI", 10, "bold"),
            anchor=W, padx=16, pady=9, bd=0, cursor="hand2", relief="flat", width=20
        )
        b.pack(fill=X, pady=1)
        b.bind("<Enter>", lambda e, btn=b, c=col: btn.config(bg=c, fg=TEXT))
        b.bind("<Leave>", lambda e, btn=b: btn.config(bg=CARD, fg=TEXT))

    # ── default content: welcome ──────────────────────────────────────
    _show_welcome(content)

    # ── status bar ───────────────────────────────────────────────────
    status = Frame(root, bg=CARD, pady=5)
    status.pack(fill=X, side=BOTTOM)
    Label(status, text="Admin Mode  |  Online Voting System v2.0",
          font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side=LEFT, padx=15)


# ─────────────────────────── content panels ───────────────────────────
def _clear(frame):
    for w in frame.winfo_children():
        w.destroy()


def _show_welcome(frame):
    _clear(frame)
    f = Frame(frame, bg=CARD)
    f.pack(expand=True)
    Label(f, text="👋", font=("Segoe UI Emoji", 48), bg=CARD).pack(pady=20)
    Label(f, text="Welcome, Admin!",
          font=("Segoe UI", 22, "bold"), bg=CARD, fg=TEXT).pack()
    Label(f, text="Select an option from the menu on the left.",
          font=("Segoe UI", 12), bg=CARD, fg=MUTED).pack(pady=8)


def _run_server(frame):
    global _server_process
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(expand=True)

    if _server_process and _server_process.poll() is None:
        Label(f, text="✅  Server Already Running",
              font=("Segoe UI", 16, "bold"), bg=CARD, fg=GREEN).pack(pady=20)
        Label(f, text="Listening on port 4001",
              font=("Segoe UI", 12), bg=CARD, fg=MUTED).pack()
        return

    try:
        import sys, os
        _server_process = sb_p.Popen(
            [sys.executable, "Server.py"],
            stdout=sb_p.PIPE, stderr=sb_p.PIPE
        )
        Label(f, text="🚀  Server Started!",
              font=("Segoe UI", 20, "bold"), bg=CARD, fg=GREEN).pack(pady=30)
        Label(f, text="Voting server is now running on port 4001.",
              font=("Segoe UI", 12), bg=CARD, fg=MUTED).pack()
        Label(f, text=f"PID: {_server_process.pid}",
              font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(pady=6)
    except Exception as ex:
        Label(f, text=f"❌  Failed to start server:\n{ex}",
              font=("Segoe UI", 12), bg=CARD, fg=RED).pack(pady=20)


def _stop_server(frame):
    global _server_process
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(expand=True)

    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process = None
        Label(f, text="🛑  Server Stopped",
              font=("Segoe UI", 20, "bold"), bg=CARD, fg=RED).pack(pady=30)
        Label(f, text="Voting server has been stopped.",
              font=("Segoe UI", 12), bg=CARD, fg=MUTED).pack()
    else:
        Label(f, text="ℹ️  Server is not running.",
              font=("Segoe UI", 16), bg=CARD, fg=MUTED).pack(pady=30)


def _open_register(root, frame):
    import registerVoter as regV
    _clear(frame)
    # build a sub-frame inside content area for the register form
    f = Frame(frame, bg=CARD)
    f.pack(fill=BOTH, expand=True)
    regV.Register(root, f, embedded=True)


def _view_voters(frame):
    import dframe as df
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(fill=BOTH, expand=True, padx=20, pady=20)

    Label(f, text="📋  Registered Voters",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=(0, 10))

    # table header
    cols = ["ID", "Name", "Gender", "Zone", "City", "Date of Birth", "Age", "Voted"]
    col_widths = [8, 14, 10, 8, 12, 14, 6, 8]
    header = Frame(f, bg=CARD2)
    header.pack(fill=X)
    for c, w in zip(cols, col_widths):
        Label(header, text=c, font=("Segoe UI", 10, "bold"),
              bg=CARD2, fg=ACCENT2, width=w, pady=6).pack(side=LEFT)

    # scrollable voter list
    import pandas as pd
    from pathlib import Path
    try:
        voters = pd.read_csv(Path("database") / "voterList.csv")
        scroll_frame = Frame(f, bg=CARD)
        scroll_frame.pack(fill=BOTH, expand=True)

        canvas  = Canvas(scroll_frame, bg=CARD, highlightthickness=0)
        scrollb = Scrollbar(scroll_frame, orient=VERTICAL, command=canvas.yview)
        inner   = Frame(canvas, bg=CARD)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollb.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollb.pack(side=RIGHT, fill=Y)

        for i, row in voters.iterrows():
            bg = CARD if i % 2 == 0 else CARD2
            r = Frame(inner, bg=bg)
            r.pack(fill=X)
            voted_txt = "✅ Yes" if int(row.get("hasVoted", 0)) == 1 else "⬜ No"
            voted_fg  = GREEN   if int(row.get("hasVoted", 0)) == 1 else MUTED

            # calculate age from DateOfBirth if present
            import dframe as _df
            dob_raw = str(row.get("DateOfBirth", "")).strip()
            if dob_raw and dob_raw not in ("", "nan"):
                try:
                    import datetime as _dt
                    dob_display = _dt.date.fromisoformat(dob_raw).strftime("%d-%m-%Y")
                except Exception:
                    dob_display = dob_raw
                age_val = _df.calculate_age(dob_raw)
                age_display = str(age_val) if age_val >= 0 else "—"
            else:
                dob_display = "—"
                age_display = "—"

            cell_data = [
                (str(row["voter_id"]), 8),
                (str(row["Name"]),     14),
                (str(row["Gender"]),   10),
                (str(row["Zone"]),      8),
                (str(row["City"]),     12),
                (dob_display,          14),
                (age_display,           6),
            ]
            for val, w in cell_data:
                Label(r, text=val, font=("Segoe UI", 10),
                      bg=bg, fg=TEXT, width=w, pady=5).pack(side=LEFT)
            Label(r, text=voted_txt, font=("Segoe UI", 10, "bold"),
                  bg=bg, fg=voted_fg, width=8, pady=5).pack(side=LEFT)

        total = len(voters)
        voted = int(voters["hasVoted"].sum()) if "hasVoted" in voters.columns else 0
        Label(f, text=f"Total: {total}  |  Voted: {voted}  |  Pending: {total-voted}",
              font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(pady=8)

    except Exception as ex:
        Label(f, text=f"Error loading voters:\n{ex}",
              font=("Segoe UI", 11), bg=CARD, fg=RED).pack(pady=20)


def _show_votes(frame):
    import dframe as df
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(expand=True)

    Label(f, text="📊  Live Vote Count",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=(20, 15))

    try:
        result = df.show_result()
        party_info = {
            "bjp":  ("BJP",          "🟠", ORANGE),
            "cong": ("Congress",     "🔵", ACCENT),
            "aap":  ("AAP",          "🔴", RED),
            "ss":   ("Shiv Sena",    "⚫", "#6b7280"),
            "nota": ("NOTA",         "⚪", MUTED),
        }

        total = sum(result.values()) or 1

        for key, (name, icon, col) in party_info.items():
            votes = result.get(key, 0)
            pct   = votes / total * 100

            row = Frame(f, bg=CARD2, padx=20, pady=10,
                        highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill=X, pady=4, padx=30)

            Label(row, text=f"{icon}  {name}",
                  font=("Segoe UI", 12, "bold"), bg=CARD2, fg=TEXT, width=18, anchor=W).pack(side=LEFT)

            # progress bar
            bar_bg = Frame(row, bg=BORDER, height=14, width=280)
            bar_bg.pack(side=LEFT, padx=10)
            bar_bg.pack_propagate(False)
            bar_fill = Frame(bar_bg, bg=col, height=14, width=max(1, int(280 * pct / 100)))
            bar_fill.place(x=0, y=0)

            Label(row, text=f"{votes} votes ({pct:.1f}%)",
                  font=("Segoe UI", 11, "bold"), bg=CARD2, fg=col, width=18).pack(side=LEFT)

        Label(f, text=f"Total Votes Cast: {sum(result.values())}",
              font=("Segoe UI", 12, "bold"), bg=CARD, fg=GOLD).pack(pady=14)

    except Exception as ex:
        Label(f, text=f"Error:\n{ex}", font=("Segoe UI", 11), bg=CARD, fg=RED).pack(pady=20)


def _show_graph(frame):
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(fill=BOTH, expand=True, padx=20, pady=20)
    Label(f, text="📈  Results Graph",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=(0, 10))
    try:
        import dframe as df
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt

        result = df.show_result()
        labels = ["BJP", "Congress", "AAP", "Shiv Sena", "NOTA"]
        values = [result.get(k, 0) for k in ["bjp", "cong", "aap", "ss", "nota"]]
        colors = ["#f97316", "#3b82f6", "#ef4444", "#6b7280", "#94a3b8"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
        fig.patch.set_facecolor("#131c31")

        # bar chart
        bars = ax1.bar(labels, values, color=colors, edgecolor="#1e3a5f", linewidth=0.8)
        ax1.set_facecolor("#1a2744")
        ax1.set_title("Vote Count", color="#f1f5f9", fontsize=12, fontweight="bold")
        ax1.tick_params(colors="#64748b")
        for spine in ax1.spines.values():
            spine.set_color("#1e3a5f")
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                     str(val), ha='center', va='bottom', color='white', fontsize=9)

        # pie chart
        non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
        if non_zero:
            pie_labels, pie_vals, pie_cols = zip(*non_zero)
            ax2.pie(pie_vals, labels=pie_labels, colors=pie_cols,
                    autopct='%1.1f%%', textprops={'color': '#f1f5f9', 'fontsize': 9},
                    wedgeprops={'linewidth': 0.5, 'edgecolor': '#0a0f1e'})
        ax2.set_facecolor("#1a2744")
        ax2.set_title("Vote Share", color="#f1f5f9", fontsize=12, fontweight="bold")

        plt.tight_layout()
        canvas_widget = FigureCanvasTkAgg(fig, master=f)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill=BOTH, expand=True)

    except ImportError:
        Label(f, text="Install matplotlib to view graphs:\npip install matplotlib",
              font=("Segoe UI", 12), bg=CARD, fg=MUTED).pack(pady=20)
    except Exception as ex:
        Label(f, text=f"Graph Error:\n{ex}", font=("Segoe UI", 11), bg=CARD, fg=RED).pack(pady=20)


def _show_fraud(frame):
    """Fraud Detection panel — runs all checks and displays results."""
    _clear(frame)
    PURPLE = "#a855f7"

    f = Frame(frame, bg=CARD)
    f.pack(fill=BOTH, expand=True, padx=20, pady=16)

    # header row
    hdr = Frame(f, bg=CARD)
    hdr.pack(fill=X)
    Label(hdr, text="🛡️  Fraud Detection",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(side=LEFT)

    scan_btn = styled_btn(hdr, "🔍  Run Scan", lambda: _do_scan(),
                          color=PURPLE, width=16, pady=5, font_size=10)
    scan_btn.pack(side=RIGHT, padx=4)
    clear_btn = styled_btn(hdr, "🗑  Clear Log", lambda: _do_clear(),
                           color=MUTED, width=14, pady=5, font_size=10)
    clear_btn.pack(side=RIGHT, padx=4)

    status_var = tk.StringVar(value="Press 'Run Scan' to analyse the vote log.")
    Label(f, textvariable=status_var,
          font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(anchor=W, pady=(6, 0))

    Frame(f, bg=BORDER, height=1).pack(fill=X, pady=8)

    # summary badges
    badge_row = Frame(f, bg=CARD)
    badge_row.pack(fill=X, pady=(0, 10))

    high_var   = tk.StringVar(value="—")
    med_var    = tk.StringVar(value="—")
    low_var    = tk.StringVar(value="—")
    total_var  = tk.StringVar(value="—")

    def _badge(parent, label, var, color):
        b = Frame(parent, bg=color, padx=16, pady=10,
                  highlightbackground=BORDER, highlightthickness=1)
        b.pack(side=LEFT, padx=6)
        Label(b, textvariable=var,
              font=("Segoe UI", 22, "bold"), bg=color, fg=TEXT).pack()
        Label(b, text=label,
              font=("Segoe UI", 9, "bold"), bg=color, fg=TEXT).pack()

    _badge(badge_row, "HIGH",   high_var,  RED)
    _badge(badge_row, "MEDIUM", med_var,   ORANGE)
    _badge(badge_row, "LOW",    low_var,   GOLD)
    _badge(badge_row, "TOTAL",  total_var, PURPLE)

    # alert table header
    table_wrap = Frame(f, bg=CARD)
    table_wrap.pack(fill=BOTH, expand=True)

    th = Frame(table_wrap, bg=CARD2)
    th.pack(fill=X)
    for col_txt, col_w in [("Severity", 9), ("Type", 20), ("Voter ID", 9), ("Detail", 52)]:
        Label(th, text=col_txt, font=("Segoe UI", 10, "bold"),
              bg=CARD2, fg=ACCENT2, width=col_w, pady=6, anchor=W, padx=4).pack(side=LEFT)

    canvas  = Canvas(table_wrap, bg=CARD, highlightthickness=0)
    scrollb = Scrollbar(table_wrap, orient=VERTICAL, command=canvas.yview)
    inner   = Frame(canvas, bg=CARD)
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollb.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollb.pack(side=RIGHT, fill=Y)

    Label(inner, text="No alerts yet. Run a scan above.",
          font=("Segoe UI", 11), bg=CARD, fg=MUTED, pady=30).pack()

    def _populate_table(alerts):
        for w in inner.winfo_children():
            w.destroy()
        if not alerts:
            Label(inner, text="No fraud alerts detected.",
                  font=("Segoe UI", 12, "bold"), bg=CARD, fg=GREEN, pady=24).pack()
            return
        severity_colors = {"HIGH": RED, "MEDIUM": ORANGE, "LOW": GOLD}
        for i, a in enumerate(alerts):
            bg  = CARD if i % 2 == 0 else CARD2
            col = severity_colors.get(a.get("severity", "LOW"), MUTED)
            row = Frame(inner, bg=bg)
            row.pack(fill=X)
            Label(row, text=a.get("severity", ""),
                  font=("Segoe UI", 9, "bold"), bg=bg, fg=col,
                  width=9, pady=5, anchor=W, padx=4).pack(side=LEFT)
            Label(row, text=a.get("type", ""),
                  font=("Segoe UI", 9), bg=bg, fg=TEXT,
                  width=20, pady=5, anchor=W, padx=4).pack(side=LEFT)
            Label(row, text=str(a.get("voter_id", "")),
                  font=("Segoe UI", 9), bg=bg, fg=MUTED,
                  width=9, pady=5, anchor=W, padx=4).pack(side=LEFT)
            Label(row, text=a.get("detail", ""),
                  font=("Segoe UI", 9), bg=bg, fg=TEXT,
                  width=52, pady=5, anchor=W, padx=4,
                  wraplength=420, justify=LEFT).pack(side=LEFT)

    def _do_scan():
        status_var.set("Scanning...")
        frame.update_idletasks()
        try:
            import fraud_detection as fd
            result = fd.run_scan()
            alerts = result["alerts"]
            s      = result["summary"]["severity"]
            high_var.set(str(s.get("HIGH", 0)))
            med_var.set(str(s.get("MEDIUM", 0)))
            low_var.set(str(s.get("LOW", 0)))
            total_var.set(str(result["total"]))
            _populate_table(alerts)
            ts = result["scanned_at"][:19].replace("T", " ")
            status_var.set(f"Last scan: {ts}  |  {result['total']} alert(s) found.")
        except Exception as ex:
            status_var.set(f"Scan error: {ex}")

    def _do_clear():
        try:
            import fraud_detection as fd
            fd.clear_fraud_log()
            high_var.set("—"); med_var.set("—"); low_var.set("—"); total_var.set("—")
            for w in inner.winfo_children():
                w.destroy()
            Label(inner, text="Fraud log cleared.", font=("Segoe UI", 11),
                  bg=CARD, fg=MUTED, pady=20).pack()
            status_var.set("Fraud log cleared.")
        except Exception as ex:
            status_var.set(f"Clear error: {ex}")

    # auto-load saved alerts on open
    try:
        import fraud_detection as fd
        saved = fd.load_saved_alerts()
        if not saved.empty:
            alerts_list = saved.to_dict("records")
            s = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for a in alerts_list:
                sev = a.get("severity", "LOW")
                s[sev] = s.get(sev, 0) + 1
            high_var.set(str(s["HIGH"]))
            med_var.set(str(s["MEDIUM"]))
            low_var.set(str(s["LOW"]))
            total_var.set(str(len(alerts_list)))
            _populate_table(alerts_list)
            status_var.set(f"Showing {len(alerts_list)} saved alert(s). Run a new scan to refresh.")
    except Exception:
        pass


def _reset_election(frame):
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(expand=True)
    Label(f, text="🔄  Reset Election",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=20)
    Label(f, text="⚠️  This will erase ALL votes and mark all voters as not-voted.\n"
                  "This action CANNOT be undone.",
          font=("Segoe UI", 11), bg=CARD, fg=ORANGE, justify=CENTER).pack(pady=10)

    def do_reset():
        if messagebox.askyesno("Confirm Reset",
                               "Are you absolutely sure?\nAll votes will be deleted."):
            import dframe as df
            df.count_reset()
            _clear(f)
            Label(f, text="✅  Election Reset Complete",
                  font=("Segoe UI", 18, "bold"), bg=CARD, fg=GREEN).pack(pady=40)

    styled_btn(f, "⚠️  Confirm Reset", do_reset, color=RED, width=24).pack(pady=20)


def _export_results(frame):
    _clear(frame)
    f = Frame(frame, bg=CARD); f.pack(expand=True)
    Label(f, text="💾  Export Results",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=20)

    def do_export():
        try:
            import dframe as df
            import datetime
            result = df.show_result()
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"results_{ts}.txt"
            with open(fname, "w") as fp:
                fp.write("ONLINE VOTING SYSTEM — ELECTION RESULTS\n")
                fp.write(f"Exported: {datetime.datetime.now()}\n")
                fp.write("=" * 40 + "\n\n")
                party_map = {"bjp": "BJP", "cong": "Congress",
                             "aap": "AAP",  "ss": "Shiv Sena", "nota": "NOTA"}
                total = sum(result.values()) or 1
                for key, name in party_map.items():
                    v = result.get(key, 0)
                    fp.write(f"{name:<15}: {v:>4} votes  ({v/total*100:.1f}%)\n")
                fp.write(f"\n{'Total':.<15}: {sum(result.values()):>4} votes\n")
            messagebox.showinfo("Exported", f"Results saved to:\n{fname}")
            Label(f, text=f"✅  Saved as {fname}",
                  font=("Segoe UI", 12, "bold"), bg=CARD, fg=GREEN).pack(pady=10)
        except Exception as ex:
            messagebox.showerror("Export Error", str(ex))

    Label(f, text="Export current vote counts to a text file.",
          font=("Segoe UI", 11), bg=CARD, fg=MUTED).pack(pady=8)
    styled_btn(f, "💾  Export Now", do_export, color=GREEN, width=24).pack(pady=20)


# ─────────────────────────── navigation ───────────────────────────────
def _go_home(root):
    import homePage
    for w in root.winfo_children():
        w.destroy()
    frame1 = Frame(root)
    frame2 = Frame(root)
    homePage.Home(root, frame1, frame2)
