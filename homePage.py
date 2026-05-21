"""
homePage.py
===========
Entry point for the Online Voting System.
Displays splash screen, then the main home page with Admin / Voter login options.
Run with:  python homePage.py
"""

import tkinter as tk
from tkinter import *
from tkinter import font as tkfont
import threading
import time


# ─────────────────────────── colour palette ───────────────────────────
BG        = "#0a0f1e"          # deep navy background
CARD      = "#131c31"          # card surface
CARD2     = "#1a2744"          # lighter card
ACCENT    = "#3b82f6"          # blue accent
ACCENT2   = "#06b6d4"          # cyan accent
GREEN     = "#10b981"          # success / voter
RED       = "#ef4444"          # danger
TEXT      = "#f1f5f9"          # primary text
MUTED     = "#64748b"          # muted text
BORDER    = "#1e3a5f"          # card border
GOLD      = "#f59e0b"          # gold highlight


# ─────────────────────────── reusable widgets ─────────────────────────
def styled_btn(parent, text, cmd, color=ACCENT, width=22, pady=10, font_size=12):
    """Modern flat button with hover effect."""
    btn = Button(
        parent, text=text, command=cmd,
        bg=color, fg=TEXT,
        activebackground=color, activeforeground=TEXT,
        font=("Segoe UI", font_size, "bold"),
        width=width, pady=pady, bd=0, cursor="hand2",
        relief="flat"
    )
    # hover brightness via lambda bind
    darker = _darken(color)
    btn.bind("<Enter>", lambda e: btn.config(bg=darker))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def _darken(hex_color, amount=20):
    """Return a slightly darker hex colour."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = max(0, r - amount), max(0, g - amount), max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def separator(parent, bg=BORDER):
    """Thin horizontal rule."""
    Frame(parent, bg=bg, height=1).pack(fill=X, pady=10)


# ─────────────────────────── splash screen ────────────────────────────
class SplashScreen:
    """Full-window animated splash that auto-closes after 2.5 s."""

    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("600x380")
        self.root.configure(bg=BG)
        self.root.overrideredirect(True)          # borderless
        self._centre()

        self._build()
        self._animate()

    def _centre(self):
        self.root.update_idletasks()
        w, h = 600, 380
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        Frame(self.root, bg=BG).pack(expand=True)

        # ── logo / emoji stand-in ──
        Label(self.root, text="🗳️", font=("Segoe UI Emoji", 52),
              bg=BG, fg=ACCENT2).pack(pady=(50, 5))

        self.title_lbl = Label(self.root,
            text="ONLINE VOTING SYSTEM",
            font=("Segoe UI", 26, "bold"), bg=BG, fg=TEXT)
        self.title_lbl.pack()

        Label(self.root,
            text="Secure  •  Transparent  •  Digital",
            font=("Segoe UI", 12), bg=BG, fg=MUTED).pack(pady=8)

        self.progress_var = DoubleVar(value=0)
        self.bar_canvas = Canvas(self.root, bg=CARD, height=6,
                                 width=420, bd=0, highlightthickness=0)
        self.bar_canvas.pack(pady=20)
        self.bar_rect = self.bar_canvas.create_rectangle(
            0, 0, 0, 6, fill=ACCENT2, outline="")

        self.status_lbl = Label(self.root, text="Initialising…",
            font=("Segoe UI", 10), bg=BG, fg=MUTED)
        self.status_lbl.pack()

    def _animate(self):
        steps = [
            (0.3, "Loading modules…"),
            (0.6, "Connecting database…"),
            (0.9, "Almost ready…"),
            (1.0, "Welcome!"),
        ]
        self._run_steps(steps, 0)

    def _run_steps(self, steps, idx):
        if idx >= len(steps):
            self.root.after(400, self._finish)
            return
        frac, msg = steps[idx]
        self._fill_bar(frac, msg)
        self.root.after(500, lambda: self._run_steps(steps, idx + 1))

    def _fill_bar(self, frac, msg):
        width = int(420 * frac)
        self.bar_canvas.coords(self.bar_rect, 0, 0, width, 6)
        self.status_lbl.config(text=msg)

    def _finish(self):
        self.root.destroy()


# ─────────────────────────── clock widget ─────────────────────────────
class LiveClock:
    def __init__(self, parent, bg=BG):
        self.lbl = Label(parent, font=("Segoe UI", 11),
                         bg=bg, fg=MUTED)
        self.lbl.pack(side=RIGHT, padx=15)
        self._tick()

    def _tick(self):
        import datetime
        now = datetime.datetime.now().strftime("%d %b %Y  |  %H:%M:%S")
        self.lbl.config(text=now)
        self.lbl.after(1000, self._tick)


# ─────────────────────────── main home page ───────────────────────────
def Home(root, frame1, frame2):
    """
    Build the main homepage inside *root*.
    frame1 / frame2 are kept for backward-compatibility with callers.
    """
    # clear everything
    for w in root.winfo_children():
        w.destroy()

    root.title("Online Voting System — Home")
    root.geometry("1000x680")
    root.resizable(True, True)
    root.configure(bg=BG)
    _centre_window(root, 1000, 680)

    # ── top bar ──────────────────────────────────────────────────────
    topbar = Frame(root, bg=CARD2, pady=8)
    topbar.pack(fill=X)
    Label(topbar, text="🗳️  Online Voting System",
          font=("Segoe UI", 13, "bold"), bg=CARD2, fg=ACCENT2).pack(side=LEFT, padx=20)
    LiveClock(topbar, bg=CARD2)

    # ── hero section ─────────────────────────────────────────────────
    hero = Frame(root, bg=BG, pady=30)
    hero.pack(fill=X)

    Label(hero, text="ONLINE VOTING SYSTEM",
          font=("Segoe UI", 36, "bold"), bg=BG, fg=TEXT).pack()
    Label(hero, text="Secure  •  Transparent  •  Digital Election Platform",
          font=("Segoe UI", 14), bg=BG, fg=ACCENT2).pack(pady=6)
    Label(hero, text="Your vote is your voice. Cast it wisely.",
          font=("Segoe UI", 11, "italic"), bg=BG, fg=MUTED).pack()

    separator(hero, BG)

    # ── card row ─────────────────────────────────────────────────────
    cards_row = Frame(root, bg=BG)
    cards_row.pack(expand=True, pady=10)

    _login_card(cards_row,
        icon="🔐", title="Admin Portal",
        desc="Manage elections,\nregister voters &\nview live results.",
        btn_text="Admin Login",
        btn_color=ACCENT,
        cmd=lambda: _go_admin(root)
    ).grid(row=0, column=0, padx=30)

    _login_card(cards_row,
        icon="🗳️", title="Voter Portal",
        desc="Login securely\nand cast your\nprecious vote.",
        btn_text="Voter Login",
        btn_color=GREEN,
        cmd=lambda: _go_voter(root)
    ).grid(row=0, column=1, padx=30)

    # ── exit button ──────────────────────────────────────────────────
    exit_frame = Frame(root, bg=BG)
    exit_frame.pack(pady=18)
    styled_btn(exit_frame, "✕  Exit Application",
               lambda: root.destroy(), color=RED, width=20, font_size=11).pack()

    # ── status bar ───────────────────────────────────────────────────
    statusbar = Frame(root, bg=CARD, pady=5)
    statusbar.pack(fill=X, side=BOTTOM)
    Label(statusbar, text="Python Tkinter  |  Socket-Based Secure Voting  |  v2.0",
          font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side=LEFT, padx=15)
    Label(statusbar, text="© 2025 Online Voting System",
          font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side=RIGHT, padx=15)


def _login_card(parent, icon, title, desc, btn_text, btn_color, cmd):
    """Rounded card widget for login options."""
    card = Frame(parent, bg=CARD, padx=40, pady=35,
                 highlightbackground=BORDER, highlightthickness=2)

    Label(card, text=icon, font=("Segoe UI Emoji", 38),
          bg=CARD).pack()
    Label(card, text=title,
          font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT).pack(pady=(8, 4))
    Label(card, text=desc,
          font=("Segoe UI", 11), bg=CARD, fg=MUTED,
          justify=CENTER).pack(pady=(0, 20))
    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=6)
    styled_btn(card, btn_text, cmd,
               color=btn_color, width=18, font_size=12).pack(pady=10)
    return card


def _go_admin(root):
    from Admin import AdmLogin
    for w in root.winfo_children():
        w.destroy()
    frame = Frame(root, bg=CARD)
    AdmLogin(root, frame)


def _go_voter(root):
    from voter import voterLogin
    for w in root.winfo_children():
        w.destroy()
    frame = Frame(root, bg=CARD)
    voterLogin(root, frame)


def _centre_window(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────── entry point ──────────────────────────────
if __name__ == "__main__":
    # 1. splash
    splash_root = tk.Tk()
    SplashScreen(splash_root)
    splash_root.mainloop()        # blocks until splash destroys itself

    # 2. main window
    root = tk.Tk()
    frame1 = Frame(root)
    frame2 = Frame(root)
    Home(root, frame1, frame2)
    root.mainloop()
