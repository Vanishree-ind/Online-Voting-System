"""
registerVoter.py
================
Voter registration form — can run embedded inside the Admin dashboard
or standalone.
NEW: Date of Birth picker with 18+ age gate.
"""

import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import datetime
import dframe as df


# ─────────────────────────── palette ──────────────────────────────────
BG      = "#0a0f1e"
CARD    = "#131c31"
CARD2   = "#1a2744"
ACCENT  = "#3b82f6"
GREEN   = "#10b981"
RED     = "#ef4444"
TEXT    = "#f1f5f9"
MUTED   = "#64748b"
BORDER  = "#1e3a5f"
ACCENT2 = "#06b6d4"


def _darken(hex_color, amount=20):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,r-amount):02x}{max(0,g-amount):02x}{max(0,b-amount):02x}"


def styled_btn(parent, text, cmd, color=ACCENT, width=22, pady=10, font_size=11):
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


def _field(parent, label, var, row, show=None, combo_vals=None):
    """
    Render label + entry or combobox in a two-column grid layout.
    Returns the entry/combobox widget.
    """
    Label(parent, text=label,
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED,
          anchor=E, width=14).grid(row=row, column=0, padx=(0, 8), pady=8, sticky=E)

    if combo_vals:
        widget = ttk.Combobox(parent, textvariable=var, values=combo_vals,
                              font=("Segoe UI", 11), width=24, state="readonly")
        widget.grid(row=row, column=1, pady=8, sticky=W)
        widget.current(0)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=CARD2, background=CARD2,
                        foreground=TEXT, selectbackground=ACCENT,
                        arrowcolor=TEXT)
        return widget

    kw = dict(textvariable=var, font=("Segoe UI", 11), width=25,
              bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat",
              highlightbackground=BORDER, highlightthickness=1)
    if show:
        kw["show"] = show
    entry = Entry(parent, **kw)
    entry.grid(row=row, column=1, ipady=6, pady=8, sticky=W)
    return entry


def _dob_field(parent, row, day_var, month_var, year_var):
    """
    Render a Date of Birth row with three dropdowns: DD / MM / YYYY.
    """
    Label(parent, text="Date of Birth",
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED,
          anchor=E, width=14).grid(row=row, column=0, padx=(0, 8), pady=8, sticky=E)

    dob_frame = Frame(parent, bg=CARD)
    dob_frame.grid(row=row, column=1, pady=8, sticky=W)

    days   = [f"{d:02d}" for d in range(1, 32)]
    months = [f"{m:02d}" for m in range(1, 13)]
    today  = datetime.date.today()
    years  = [str(y) for y in range(today.year, today.year - 120, -1)]

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=CARD2, background=CARD2,
                    foreground=TEXT, selectbackground=ACCENT,
                    arrowcolor=TEXT)

    # sub-labels
    for col_idx, lbl in enumerate(["DD", "MM", "YYYY"]):
        Label(dob_frame, text=lbl,
              font=("Segoe UI", 8), bg=CARD, fg=MUTED).grid(row=0, column=col_idx, padx=(0, 6))

    dd_cb = ttk.Combobox(dob_frame, textvariable=day_var,   values=days,   width=4,  state="readonly", font=("Segoe UI", 11))
    mm_cb = ttk.Combobox(dob_frame, textvariable=month_var, values=months, width=4,  state="readonly", font=("Segoe UI", 11))
    yy_cb = ttk.Combobox(dob_frame, textvariable=year_var,  values=years,  width=6,  state="readonly", font=("Segoe UI", 11))

    dd_cb.grid(row=1, column=0, padx=(0, 6))
    mm_cb.grid(row=1, column=1, padx=(0, 6))
    yy_cb.grid(row=1, column=2)


# ─────────────────────────── registration ─────────────────────────────
def Register(root, frame1, embedded=False):
    """
    Build the voter registration form.
    If *embedded* is True, renders directly in frame1 (used inside the
    Admin dashboard content panel).
    """

    for w in frame1.winfo_children():
        w.destroy()

    frame1.configure(bg=CARD)

    if not embedded:
        root.title("Register Voter — Online Voting System")
        root.geometry("820x680")
        root.configure(bg=BG)

    # ── heading ─────────────────────────────────────────────────────
    hdr = Frame(frame1, bg=CARD)
    hdr.pack(fill=X, padx=30, pady=(20, 10))
    Label(hdr, text="➕  Register New Voter",
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(side=LEFT)

    Frame(frame1, bg=BORDER, height=1).pack(fill=X, padx=30, pady=2)

    # ── form ────────────────────────────────────────────────────────
    form_frame = Frame(frame1, bg=CARD, padx=20, pady=5)
    form_frame.pack()

    name      = tk.StringVar()
    sex       = tk.StringVar(value="Male")
    zone      = tk.StringVar()
    city      = tk.StringVar()
    password  = tk.StringVar()
    confirm   = tk.StringVar()
    dob_day   = tk.StringVar(value="01")
    dob_month = tk.StringVar(value="01")
    dob_year  = tk.StringVar(value="2000")
    error_var = tk.StringVar()

    _field(form_frame, "Full Name",   name,     row=0)
    _field(form_frame, "Gender",      sex,      row=1,
           combo_vals=("Male", "Female", "Transgender", "Prefer not to say"))
    _field(form_frame, "Zone",        zone,     row=2)
    _field(form_frame, "City",        city,     row=3)
    _field(form_frame, "Password",    password, row=4, show="*")
    _field(form_frame, "Confirm Pwd", confirm,  row=5, show="*")
    _dob_field(form_frame, row=6,
               day_var=dob_day, month_var=dob_month, year_var=dob_year)

    # age preview label — updates live as dropdowns change
    age_lbl = Label(form_frame, text="",
                    font=("Segoe UI", 9, "italic"), bg=CARD, fg=MUTED)
    age_lbl.grid(row=7, column=1, sticky=W, pady=(0, 4))

    def _refresh_age_preview(*_):
        try:
            dob_str = f"{dob_year.get()}-{dob_month.get()}-{dob_day.get()}"
            age = df.calculate_age(dob_str)
            if age < 0:
                age_lbl.config(text="", fg=MUTED)
            elif age < 18:
                age_lbl.config(text=f"Age: {age}  ⚠ Must be 18+", fg=RED)
            else:
                age_lbl.config(text=f"Age: {age}  ✓ Eligible", fg=GREEN)
        except Exception:
            age_lbl.config(text="", fg=MUTED)

    dob_day.trace_add("write",   _refresh_age_preview)
    dob_month.trace_add("write", _refresh_age_preview)
    dob_year.trace_add("write",  _refresh_age_preview)

    # error label
    err_lbl = Label(form_frame, textvariable=error_var,
                    font=("Segoe UI", 10, "bold"), bg=CARD, fg=RED)
    err_lbl.grid(row=8, column=0, columnspan=2, pady=(4, 0))

    # ── buttons ─────────────────────────────────────────────────────
    btn_frame = Frame(frame1, bg=CARD, pady=10)
    btn_frame.pack()

    def do_register():
        error_var.set("")

        n  = name.get().strip()
        s  = sex.get().strip()
        z  = zone.get().strip()
        c  = city.get().strip()
        p  = password.get().strip()
        cf = confirm.get().strip()

        # ── basic field validation ───────────────────────────────
        if not all([n, s, z, c, p]):
            error_var.set("⚠  All fields are required.")
            return
        if len(p) < 4:
            error_var.set("⚠  Password must be at least 4 characters.")
            return
        if p != cf:
            error_var.set("⚠  Passwords do not match.")
            return

        # ── date-of-birth validation ─────────────────────────────
        try:
            dob_obj = datetime.date(
                int(dob_year.get()),
                int(dob_month.get()),
                int(dob_day.get())
            )
            dob_str = dob_obj.isoformat()          # YYYY-MM-DD
        except ValueError:
            error_var.set("⚠  Invalid date of birth — please check day/month.")
            return

        if dob_obj > datetime.date.today():
            error_var.set("⚠  Date of birth cannot be in the future.")
            return

        # ── 18+ age gate ─────────────────────────────────────────
        age = df.calculate_age(dob_str)
        if age < 18:
            error_var.set(f"⚠  Must be 18 or older to register.  (Your age: {age})")
            return

        # ── save to database ─────────────────────────────────────
        try:
            vid = df.taking_data_voter(n, s, z, c, p, dob_str)
            _show_success(frame1, vid, n, dob_str, age, embedded)
        except Exception as ex:
            error_var.set(f"Database error: {ex}")

    styled_btn(btn_frame, "✅  Register Voter", do_register,
               color=GREEN, width=22, font_size=11).pack(side=LEFT, padx=8)

    if not embedded:
        styled_btn(btn_frame, "← Back to Home",
                   lambda: _go_home(root),
                   color=CARD2, width=18, font_size=10).pack(side=LEFT, padx=8)

    if not embedded:
        frame1.pack(expand=True)


# ─────────────────────────── success card ────────────────────────────
def _show_success(frame1, vid, name, dob_str, age, embedded=False):
    """Replace form with a success card showing Voter ID, DOB, and age."""
    try:
        dob_display = datetime.date.fromisoformat(dob_str).strftime("%d %B %Y")
    except Exception:
        dob_display = dob_str

    for w in frame1.winfo_children():
        w.destroy()

    outer = Frame(frame1, bg=CARD)
    outer.pack(expand=True)

    Label(outer, text="✅", font=("Segoe UI Emoji", 50), bg=CARD).pack(pady=(30, 10))
    Label(outer, text="Voter Registered Successfully!",
          font=("Segoe UI", 20, "bold"), bg=CARD, fg=GREEN).pack()
    Label(outer, text=f"Welcome, {name}",
          font=("Segoe UI", 13), bg=CARD, fg=TEXT).pack(pady=6)

    # ── ID card ─────────────────────────────────────────────────────
    id_frame = Frame(outer, bg=CARD2, padx=36, pady=22,
                     highlightbackground=BORDER, highlightthickness=1)
    id_frame.pack(pady=16)

    Label(id_frame, text="VOTER ID",
          font=("Segoe UI", 10, "bold"), bg=CARD2, fg=MUTED).pack()
    Label(id_frame, text=str(vid),
          font=("Segoe UI", 34, "bold"), bg=CARD2, fg=ACCENT2).pack()

    Frame(id_frame, bg=BORDER, height=1).pack(fill=X, pady=10)

    Label(id_frame, text="DATE OF BIRTH",
          font=("Segoe UI", 9, "bold"), bg=CARD2, fg=MUTED).pack()
    Label(id_frame, text=dob_display,
          font=("Segoe UI", 13, "bold"), bg=CARD2, fg=TEXT).pack()
    Label(id_frame, text=f"Age: {age} years",
          font=("Segoe UI", 10), bg=CARD2, fg=GREEN).pack(pady=(2, 0))

    Frame(id_frame, bg=BORDER, height=1).pack(fill=X, pady=10)

    Label(id_frame, text="Please note this Voter ID — it cannot be recovered.",
          font=("Segoe UI", 9, "italic"), bg=CARD2, fg=MUTED).pack()

    # ── register another ────────────────────────────────────────────
    def reg_another():
        Register(None, frame1, embedded=embedded)

    Button(outer, text="➕  Register Another",
           command=reg_another,
           bg=ACCENT, fg=TEXT,
           font=("Segoe UI", 11, "bold"),
           width=22, pady=8, bd=0, cursor="hand2", relief="flat").pack(pady=12)


# ─────────────────────────── navigation ───────────────────────────────
def _go_home(root):
    import homePage
    for w in root.winfo_children():
        w.destroy()
    frame1 = Frame(root)
    frame2 = Frame(root)
    homePage.Home(root, frame1, frame2)
