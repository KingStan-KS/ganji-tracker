# Ganji Tracker — My learning log

> **About this log:** This isn't a polished highlight reel. It's an honest record of how I built **Ganji Tracker** from scratch 
---

## Project Origin | Why Did i Build This

I wanted my GitHub portfolio project to do two things at once:
1. Force me to actually *use* the Python fundamentals from my semester notes (data types, conditionals, loops, functions and others) instead of just memorizing them for paper exams.
2. Solve a real problem I understand—managing weekly student money (**"ganji"**) when cash comes from parents/guardians, occasional side hustles, and sometimes borrowing from friends, while disappearing into food, transport, data/Wi-Fi, clothing, leisure, and random miscellaneous costs.

I also wanted to stretch myself later with recurring-expense flags, summary reports, and eventually 6-hour phone spending alerts. To avoid getting overwhelmed and quitting halfway, I broke the build into **4 phases** so I could be realistic and climb the Python ladder one step at a time.

---

## Entry 01 | 2026-11-25 | Phase 1: The First Working Prototype (And Its Cracks)

### What I Built
- A single-file terminal app (`ganji_tracker.py`) with a numbered interactive menu (options 1–6).
- Basic in-memory tracking using a list of dictionaries for each transaction.
- Separated incoming money into **Real Income** (allowance, side hustle) vs. **Loans** (borrowed from friends), because borrowed cash sits in your wallet today but isn't actually yours.
- Added a basic daily **Safe-to-Spend** calculation (`cash_on_hand / days_left`) and `if/elif/else` status alerts.

### Challenges, Inaccuracies & Logical Failures
1. **The "Cash on Hand" confusion:** When I tested the script by entering a week's worth of expenses *without* any loans, the summary showed `Cash on Hand`, `Unpaid Loans: 0.00`, and `Actual Net Worth`which was essentially just repeating the exact same number twice. It felt cluttered and made me question why "Cash on Hand" was even there.
   - *Realization:* "Cash on Hand" only earns its keep when you owe a friend money (e.g., KES 1,000 in M-Pesa, KES 500 owed = KES 500 real net balance). When debt is zero, showing three balance lines just confuses the user.
2. **Repaying a loan broke my spending stats:** In v1, marking a friend's loan as repaid logged a normal `kind: "expense"` record. That meant paying back KES 500 inflated `Total Spent` and distorted my category percentages, even though repaying debt isn't consumption like buying food.
3. **Hardcoded dates:** Every entry auto-stamped `date.today()`. That completely breaks down if a student sits down on Sunday evening to log what they spent on Tuesday and Thursday.
4. **Everything vanished on exit:** Because Phase 1 only lived in memory, closing the terminal wiped all my test data. Now that was annoying and i crushed out, but it gave me a concrete reason to care about File I/O 

### Reality Check on User Discipline
Testing v1 made something obvious: **the program demanded way too much discipline.** Expecting a busy student with life happening around him or her to open a laptop, launch VS Code, and answer 4–5 menu prompts every time they buy lunch or pay fare is unrealistic. Most people would abandon it by day three. Also, v1 had zero answer for **unbudgeted emergencies** (like a sudden clinic visit or broken charger)—an emergency would just trigger harsh "CRITICAL / OVER BUDGET" warnings and make the user feel guilty.

---

## Entry 02 | 2026-11-25 | Phase 2: Lowering Friction, Emergencies & JSON Persistence

### Goal
Redesign Ganji Tracker around *real human behavior* rather than ideal discipline, fix every accounting bug from Entry 01, and save data permanently to disk.

### Key Design Shifts
- **Quick-Log Bulk Mode:** Replaced the tedious multi-prompt expense flow with a single-line loop (`150 food chapo madondo`, `50 data bundles -r`, `400 emerg clinic -e`) and a sticky batch date (`Enter` = today, `y` = yesterday, or `YYYY-MM-DD`). Now a user can catch up on a whole day or week in under 30 seconds without bouncing back to the main menu.
- **Emergency Buffer & Recovery Mode:** Added an optional **10% skim** on incoming allowance/hustle into a protected `emergency_buffer`. Emergency expenses (`-e` or category `7`) draw from that buffer first and trigger a calm **Recovery Mode** survival budget instead of scolding the user for poor discipline.
- **Honest Accounting & Cleaner Output:**
  - Changed loan repayments to `kind: "repayment"` so they deduct cash accurately without inflating spending totals.
  - Hid `Unpaid Loans` and `Actual Net Balance` whenever `unpaid_debt == 0`, showing a single clean `Remaining Balance`.
- **From Rear-View Mirror to Co-Pilot:** Added a **"Can I Afford This?"** simulator (tests how a planned purchase affects daily Safe-to-Spend *before* buying), a **Small-Leak Detector** (flags any non-emergency category hit 3+ times), and pure-Python **ASCII bar charts**.
- **Permanent Storage:** Added `load_data()` and `save_data()` using `json`, `os`, and `with open()` wrapped in `try/except` so missing or corrupted files never crash the app.

### Code Style Pivot (Keeping It Grounded)
My first draft of Phase 2 leaned on compact shortcuts (`pathlib`, `collections.Counter`, dense generator expressions). Looking at it closely, I realized I wanted code I could **hand-trace on paper and try to explain my idea behind it** to a lecturer or interviewer. I rewrote Phase 2 using explicit `for` loops, clear tuples/dictionaries, `os.path`, `datetime`, and plain-English comments.

### Blocks, Snags & Friction
- **The VS Code Terminal Trap:** After pasting Phase 2 into `ganji_tracker.py` and clicking the Play button, I got:
  ```text
  Choose an action (1–6): C:\Users\...\python.exe ".../ganji_tracker.py"
    [!] Enter a whole number between 1 and 6.

    It threw me off for a second until I realized my Phase 1 script was still running at the 1–6 prompt! Clicking Play literally typed the Python command straight into my old input() loop—and my own validation function rejected it.

Lesson: Always exit an interactive CLI (6/7 or Ctrl + C) before hitting Run again.

Mental Fatigue Check: Juggling syllabus revision, designing data models, and debugging terminal quirks in one stretch definitely tested my focus. Pausing to trace why a bug happened instead of blindly re-running saved a lot of frustration but there was frustration along the way