# 🗳️ Online Voting System v2.0

A modern, socket-based online voting system built with Python Tkinter.

---

## 📦 Requirements

- **Python 3.8+**
- Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project

```bash
python homePage.py
```

That's it! The home page opens with a splash screen, then the main menu.

---

## 👤 Default Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | `Admin`  | `admin`  |

Sample voters (in `database/voterList.csv`):

| Voter ID | Name      | Password |
|----------|-----------|----------|
| 10001    | Deep      | abcd     |
| 10002    | Prachi    | abcd     |
| 10003    | Het       | abcd     |
| 10004    | Shivanshi | abcd     |
| 10005    | Dev       | abcd     |

---

## 📋 How to Use

### Admin Workflow
1. Open the app → click **Admin Login**
2. Login with `Admin` / `admin`
3. From the dashboard, click **🟢 Run Server** to start the voting server
4. Use **Register Voter** to add new voters
5. Use **Live Vote Count** or **Results Graph** to monitor the election
6. Use **Export Results** to save results to a text file
7. Use **Reset Election** to start a fresh election

### Voter Workflow
1. Admin must have started the server first
2. Open the app → click **Voter Login**
3. Enter your **Voter ID** and **Password**
4. Select a candidate card and click **Vote**
5. Confirm your vote in the dialog
6. View your thank-you screen

---

## 📁 Project Structure

```
Online-Voting-System/
├── homePage.py         # Entry point — splash + home page
├── Admin.py            # Admin login + full dashboard
├── voter.py            # Voter login + socket auth
├── VotingPage.py       # Candidate cards + vote casting
├── registerVoter.py    # Voter registration form
├── admFunc.py          # Admin utility functions
├── dframe.py           # Database layer (pandas + CSV)
├── Server.py           # Voting server (socket + threading)
├── requirements.txt
├── database/
│   ├── voterList.csv   # Registered voters
│   ├── cand_list.csv   # Candidates + vote counts
│   └── vote_log.csv    # Audit log (created automatically)
└── img/
    ├── bjp.png
    ├── cong.jpg
    ├── aap.png
    ├── ss.png
    └── nota.jpg
```

---

## 🔐 Security Features

- Password masking (show/hide toggle on voter login)
- One-person-one-vote enforcement at server level
- Thread-locked database writes (concurrent safety)
- Input validation on all forms
- Confirmation dialog before vote is submitted
- Vote audit log with timestamps

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection Failed` on voter login | Start the server from Admin Dashboard first |
| `ModuleNotFoundError: PIL` | Run `pip install Pillow` |
| `ModuleNotFoundError: pandas` | Run `pip install pandas` |
| Charts not showing | Run `pip install matplotlib` |
| Server port already in use | Restart the app or wait 30 s |

---

## ✨ Features Added in v2.0

- Animated splash screen
- Live clock in top bar
- Modern dark theme throughout
- Hover effects on all buttons
- Admin sidebar navigation dashboard
- Voter candidate cards with logos
- Vote confirmation dialog
- Thank-you page after voting
- Results bar charts + pie chart (matplotlib)
- Export results to text file
- Reset election with confirmation
- View all registered voters table
- Vote audit log with timestamps
- Improved socket error handling
- Password show/hide toggle
- Full input validation with inline error messages

---

## 🛡️ Fraud Detection (v2.1)

A **Fraud Detection** panel has been added to the Admin Dashboard.

### Accessing It
1. Log in as Admin (`Admin` / `admin`).
2. Click **🛡️  Fraud Detection** in the left sidebar.

### Detection Rules

| Rule | Severity | Description |
|------|----------|-------------|
| Duplicate Vote | HIGH | Same voter ID found more than once in the vote log |
| Unregistered Voter | HIGH | Vote log entry for a voter ID not in `voterList.csv` |
| Flag Mismatch | HIGH / MEDIUM | `hasVoted` flag in database contradicts the vote log |
| Rapid Voting | MEDIUM | Two votes cast within 5 seconds of each other (bot detection) |
| Off-Hours Vote | LOW | Vote cast outside the 08:00–20:00 window |

### Files Added
- `fraud_detection.py` — detection engine (no extra dependencies)
- `database/fraud_alerts.csv` — auto-created on first scan; persists across sessions

### Usage
- **Run Scan** — executes all rules and shows alerts grouped by severity.
- **Clear Log** — wipes `fraud_alerts.csv` and resets the panel.
- Alerts are colour-coded: 🔴 HIGH · 🟠 MEDIUM · 🟡 LOW.
