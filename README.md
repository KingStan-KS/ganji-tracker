# Ganji Tracker

A low-friction, terminal-based personal finance tracker built in pure Python for university students managing weekly allowances, side hustles, and occasional loans from friends.

## Features
- **Quick-Log Bulk Mode:** Record multiple expenses in one sitting using single-line shortcuts (e.g., `150 food chapo madondo`, `50 data bundles -r`) with a sticky batch date for end-of-day or Sunday catch-ups.
- **Honest Loan Tracking:** Separates borrowed cash (`loan`) from real income and logs repayments separately so paying back a friend never distorts your spending percentages.
- **Emergency Buffer & Recovery Mode:** Optionally ring-fence 10% of incoming funds for emergencies; unexpected costs draw from the buffer first and trigger a calm daily survival cap instead of scolding alerts.
- **Active Co-Pilot Output:** Includes a **"Can I Afford This?"** purchase simulator, pure-Python ASCII category bar charts, and a **Small-Leak Detector** (flags categories hit 3+ times).
- **Persistent JSON Storage:** Automatically saves and reloads records locally via `ganji_data.json` with graceful error recovery.

## How to Run
Requires Python 3.8+ (zero external dependencies).

```bash
python ganji_tracker.py