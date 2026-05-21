"""
voter.py
========
Voter login page — establishes socket connection to the voting server,
authenticates the voter, then hands off to VotingPage.
"""

import tkinter as tk
import socket
from tkinter import *
from tkinter import messagebox


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


def styled_btn(parent, text, cmd, color=ACCENT, width=22, pady=10, font_size=12):
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


def _centre(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────── socket helpers ───────────────────────────
def establish_connection():
    """Attempt to connect to the voting server.  Returns socket or 'Failed'."""
    try:
        host = socket.gethostname()
        port = 4001
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((host, port))
        message = client_socket.recv(1024)
        if message.decode() == "Connection Established":
            client_socket.settimeout(None)
            return client_socket
        return "Failed"
    except Exception:
        return "Failed"


# ─────────────────────────── Voter Login Page ─────────────────────────
def voterLogin(root, frame1):
    """Render the voter login page."""
    root.title("Voter Login — Online Voting System")
    root.geometry("1000x680")
    root.configure(bg=BG)
    _centre(root, 1000, 680)

    for w in root.winfo_children():
        w.destroy()

    # top bar
    topbar = Frame(root, bg=CARD2, pady=8)
    topbar.pack(fill=X)
    Label(topbar, text="🗳️  Online Voting System  ›  Voter Login",
          font=("Segoe UI", 12, "bold"), bg=CARD2, fg=TEXT).pack(side=LEFT, padx=18)

    # centre card
    outer = Frame(root, bg=BG)
    outer.pack(expand=True)

    card = Frame(outer, bg=CARD, padx=60, pady=50,
                 highlightbackground=BORDER, highlightthickness=2)
    card.pack()

    Label(card, text="🗳️", font=("Segoe UI Emoji", 42), bg=CARD).pack()
    Label(card, text="VOTER LOGIN",
          font=("Segoe UI", 22, "bold"), bg=CARD, fg=TEXT).pack(pady=(8, 2))
    Label(card, text="Enter your Voter ID and password to cast your vote",
          font=("Segoe UI", 10), bg=CARD, fg=MUTED).pack(pady=(0, 18))

    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=6)

    voter_ID = tk.StringVar()
    password = tk.StringVar()
    error_var = tk.StringVar()

    # Voter ID field
    Label(card, text="Voter ID",
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(anchor=W, pady=(10, 2))
    Entry(card, textvariable=voter_ID,
          font=("Segoe UI", 13), width=26,
          bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat",
          highlightbackground=BORDER, highlightthickness=1).pack(ipady=8)

    # Password field
    Label(card, text="Password",
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=MUTED).pack(anchor=W, pady=(12, 2))
    pwd_frame = Frame(card, bg=CARD)
    pwd_frame.pack()
    pwd_entry = Entry(pwd_frame, textvariable=password, show="*",
                      font=("Segoe UI", 13), width=22,
                      bg=CARD2, fg=TEXT, insertbackground=TEXT, relief="flat",
                      highlightbackground=BORDER, highlightthickness=1)
    pwd_entry.pack(side=LEFT, ipady=8)

    # show/hide toggle
    show_var = tk.BooleanVar(value=False)
    def toggle_pwd():
        pwd_entry.config(show="" if show_var.get() else "*")
    Checkbutton(pwd_frame, text="👁", variable=show_var, command=toggle_pwd,
                bg=CARD, fg=MUTED, activebackground=CARD,
                selectcolor=CARD, bd=0, font=("Segoe UI", 12)).pack(side=LEFT, padx=6)

    # error label
    Label(card, textvariable=error_var,
          font=("Segoe UI", 10, "bold"), bg=CARD, fg=RED).pack(pady=(6, 0))

    def do_login():
        error_var.set("")
        vid = voter_ID.get().strip()
        pwd = password.get().strip()

        if not vid or not pwd:
            error_var.set("⚠  Please enter Voter ID and Password.")
            return

        # show loading state
        login_btn.config(text="Connecting…", state=DISABLED)
        root.update()

        client_socket = establish_connection()

        if client_socket == "Failed":
            login_btn.config(text="🔓  Login", state=NORMAL)
            error_var.set("❌  Cannot connect. Please ask the Admin to start the server.")
            return

        login_btn.config(text="Authenticating…")
        root.update()
        _process_login(root, client_socket, vid, pwd, error_var, login_btn)

    login_btn = styled_btn(card, "🔓  Login", do_login,
                           color=GREEN, width=26, font_size=12)
    login_btn.pack(pady=18)

    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=4)
    styled_btn(card, "← Back to Home", lambda: _go_home(root),
               color=CARD2, width=26, font_size=10).pack(pady=6)


def _process_login(root, client_socket, voter_ID, password, error_var, login_btn):
    """Send credentials to server and handle response."""
    try:
        message = voter_ID + " " + password
        client_socket.send(message.encode())

        response = client_socket.recv(1024).decode()

        if response == "Authenticate":
            # open voting page
            from VotingPage import votingPg
            for w in root.winfo_children():
                w.destroy()
            frame = Frame(root, bg=CARD)
            votingPg(root, frame, client_socket)

        elif response == "VoteCasted":
            client_socket.close()
            login_btn.config(text="🔓  Login", state=NORMAL)
            error_var.set("⚠️  You have already cast your vote.")

        elif response == "InvalidVoter":
            client_socket.close()
            login_btn.config(text="🔓  Login", state=NORMAL)
            error_var.set("❌  Invalid Voter ID or Password.")

        else:
            client_socket.close()
            login_btn.config(text="🔓  Login", state=NORMAL)
            error_var.set("⚠️  Unexpected server response.")

    except Exception as ex:
        login_btn.config(text="🔓  Login", state=NORMAL)
        error_var.set(f"Connection error: {ex}")


# ─────────────────────────── navigation ───────────────────────────────
def _go_home(root):
    import homePage
    for w in root.winfo_children():
        w.destroy()
    frame1 = Frame(root)
    frame2 = Frame(root)
    homePage.Home(root, frame1, frame2)
