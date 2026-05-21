"""
VotingPage.py
=============
Displays candidate cards and handles the vote-casting flow.
After a vote is cast, shows a thank-you / result page.
"""

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import os


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
ACCENT2 = "#06b6d4"
GOLD    = "#f59e0b"


def _darken(hex_color, amount=20):
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{max(0,r-amount):02x}{max(0,g-amount):02x}{max(0,b-amount):02x}"


def _centre(win, w, h):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────── candidates list ──────────────────────────
CANDIDATES = [
    {
        "name":    "Narendra Modi",
        "party":   "BJP — Bharatiya Janata Party",
        "symbol":  "bjp",
        "img":     "img/bjp.png",
        "color":   ORANGE,
        "icon":    "🟠",
    },
    {
        "name":    "Rahul Gandhi",
        "party":   "Congress — Indian National Congress",
        "symbol":  "cong",
        "img":     "img/cong.jpg",
        "color":   ACCENT,
        "icon":    "🔵",
    },
    {
        "name":    "Arvind Kejriwal",
        "party":   "AAP — Aam Aadmi Party",
        "symbol":  "aap",
        "img":     "img/aap.png",
        "color":   "#6366f1",
        "icon":    "🟣",
    },
    {
        "name":    "Uddhav Thackeray",
        "party":   "Shiv Sena",
        "symbol":  "ss",
        "img":     "img/ss.png",
        "color":   "#6b7280",
        "icon":    "⚫",
    },
    {
        "name":    "NOTA",
        "party":   "None Of The Above",
        "symbol":  "nota",
        "img":     "img/nota.jpg",
        "color":   MUTED,
        "icon":    "⚪",
    },
]


# ─────────────────────────── voting page ──────────────────────────────
def votingPg(root, frame1, client_socket):
    """Render the candidate-selection page."""
    root.title("Cast Your Vote — Online Voting System")
    root.geometry("1100x720")
    root.configure(bg=BG)
    _centre(root, 1100, 720)

    for w in root.winfo_children():
        w.destroy()

    # top bar
    topbar = Frame(root, bg=CARD2, pady=10)
    topbar.pack(fill=X)
    Label(topbar, text="🗳️  Online Voting System  ›  Cast Your Vote",
          font=("Segoe UI", 13, "bold"), bg=CARD2, fg=TEXT).pack(side=LEFT, padx=18)
    Label(topbar, text="⚠️  You can only vote ONCE",
          font=("Segoe UI", 10, "bold"), bg=CARD2, fg=GOLD).pack(side=RIGHT, padx=18)

    # heading
    hdr = Frame(root, bg=BG, pady=16)
    hdr.pack(fill=X)
    Label(hdr, text="SELECT YOUR CANDIDATE",
          font=("Segoe UI", 26, "bold"), bg=BG, fg=TEXT).pack()
    Label(hdr, text="Click on a candidate card below to cast your vote.",
          font=("Segoe UI", 11), bg=BG, fg=MUTED).pack(pady=4)
    Frame(hdr, bg=BORDER, height=1).pack(fill=X, padx=30, pady=8)

    # scrollable candidate cards
    outer = Frame(root, bg=BG)
    outer.pack(fill=BOTH, expand=True, padx=30, pady=10)

    canvas  = Canvas(outer, bg=BG, highlightthickness=0)
    scrollb = Scrollbar(outer, orient=VERTICAL, command=canvas.yview)
    inner   = Frame(canvas, bg=BG)

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollb.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollb.pack(side=RIGHT, fill=Y)

    # mouse-wheel scroll
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # keep image refs alive
    img_refs = []

    cols = 3
    for idx, cand in enumerate(CANDIDATES):
        row_idx, col_idx = divmod(idx, cols)
        card = _make_candidate_card(
            inner, cand, client_socket, root, img_refs
        )
        card.grid(row=row_idx, column=col_idx, padx=16, pady=14, sticky="nsew")

    for c in range(cols):
        inner.columnconfigure(c, weight=1)

    # store img refs on root to prevent GC
    root._voting_img_refs = img_refs


def _make_candidate_card(parent, cand, client_socket, root, img_refs):
    """Build a single candidate card widget."""
    color = cand["color"]

    card = Frame(parent, bg=CARD, padx=20, pady=20,
                 highlightbackground=BORDER, highlightthickness=2,
                 cursor="hand2")

    # party colour bar at top
    Frame(card, bg=color, height=5).pack(fill=X)

    # logo / image
    try:
        img_path = cand["img"]
        if os.path.exists(img_path):
            pil_img = Image.open(img_path).resize((80, 70), Image.LANCZOS)
            photo   = ImageTk.PhotoImage(pil_img)
            img_refs.append(photo)
            Label(card, image=photo, bg=CARD).pack(pady=(12, 4))
        else:
            raise FileNotFoundError
    except Exception:
        Label(card, text=cand["icon"], font=("Segoe UI Emoji", 34),
              bg=CARD).pack(pady=(12, 4))

    Label(card, text=cand["name"],
          font=("Segoe UI", 13, "bold"), bg=CARD, fg=TEXT).pack()
    Label(card, text=cand["party"],
          font=("Segoe UI", 9), bg=CARD, fg=MUTED, wraplength=180,
          justify=CENTER).pack(pady=(2, 12))

    Frame(card, bg=BORDER, height=1).pack(fill=X, pady=4)

    vote_btn = Button(
        card, text=f"Vote for {cand['name'].split()[0]}",
        command=lambda: _confirm_vote(root, cand, client_socket),
        bg=color, fg=TEXT, activebackground=_darken(color),
        font=("Segoe UI", 10, "bold"),
        width=20, pady=7, bd=0, cursor="hand2", relief="flat"
    )
    vote_btn.pack(pady=6)
    vote_btn.bind("<Enter>", lambda e: vote_btn.config(bg=_darken(color)))
    vote_btn.bind("<Leave>", lambda e: vote_btn.config(bg=color))

    return card


def _confirm_vote(root, cand, client_socket):
    """Show confirmation dialog before actually sending the vote."""
    confirmed = messagebox.askyesno(
        "Confirm Your Vote",
        f"You are about to vote for:\n\n"
        f"  {cand['name']}\n  ({cand['party']})\n\n"
        f"This action CANNOT be undone.\n\nProceed?"
    )
    if confirmed:
        voteCast(root, cand["symbol"], client_socket, cand)


# ─────────────────────────── vote casting ─────────────────────────────
def voteCast(root, vote, client_socket, cand=None):
    """Send the vote to the server and display the result screen."""
    try:
        client_socket.send(vote.encode())
        message = client_socket.recv(1024).decode()
    except Exception as ex:
        messagebox.showerror("Connection Error",
                             f"Failed to send vote:\n{ex}")
        return
    finally:
        try:
            client_socket.close()
        except Exception:
            pass

    # ── result / thank-you screen ─────────────────────────────────────
    for w in root.winfo_children():
        w.destroy()

    root.configure(bg=BG)
    outer = Frame(root, bg=BG)
    outer.pack(expand=True)

    if message == "Successful":
        Label(outer, text="🎉", font=("Segoe UI Emoji", 60), bg=BG).pack(pady=(30, 10))
        Label(outer, text="VOTE CAST SUCCESSFULLY!",
              font=("Segoe UI", 26, "bold"), bg=BG, fg=GREEN).pack()

        if cand:
            Label(outer, text=f"You voted for  {cand['name']}",
                  font=("Segoe UI", 14), bg=BG, fg=TEXT).pack(pady=8)
            Label(outer, text=cand["party"],
                  font=("Segoe UI", 11), bg=BG, fg=MUTED).pack()

        Frame(outer, bg=BORDER, height=1).pack(fill=X, padx=60, pady=20)
        Label(outer, text="Thank you for exercising your democratic right!",
              font=("Segoe UI", 12, "italic"), bg=BG, fg=ACCENT2).pack()

    else:
        Label(outer, text="❌", font=("Segoe UI Emoji", 60), bg=BG).pack(pady=(30, 10))
        Label(outer, text="VOTE FAILED",
              font=("Segoe UI", 26, "bold"), bg=BG, fg=RED).pack()
        Label(outer, text=f"Server response: {message}",
              font=("Segoe UI", 12), bg=BG, fg=MUTED).pack(pady=8)

    # return home button
    def go_home():
        import homePage
        for w in root.winfo_children():
            w.destroy()
        frame1 = Frame(root)
        frame2 = Frame(root)
        homePage.Home(root, frame1, frame2)

    btn = Button(
        outer, text="← Return to Home", command=go_home,
        bg=CARD2, fg=TEXT, activebackground=CARD,
        font=("Segoe UI", 12, "bold"),
        width=24, pady=10, bd=0, cursor="hand2", relief="flat"
    )
    btn.pack(pady=30)
