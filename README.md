```markdown
# Ganji Tracker

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)
![Storage](https://img.shields.io/badge/Storage-Local%20JSON-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
[![GitHub stars](https://img.shields.io/github/stars/KingStan-KS/ganji-tracker?style=social)](https://github.com/KingStan-KS/ganji-tracker/stargazers)

A low-friction, terminal-based personal finance tracker built in pure Python for university students who are trying to manage weekly allowances, side hustles, and occasional loans from friends.

---

## Why Ganji Tracker?
Most budget apps fail because they demand unrealistic discipline—asking you to fill out multiple prompts every time you buy lunch—and scold you when an unbudgeted emergency hits. **Ganji Tracker** is designed around real student habits:

* **Quick-Log Bulk Mode:** Log a whole day or week in under 30 seconds using single-line shortcuts (`150 food chapo madondo`, `50 data bundles -r`) with a sticky batch date.
* **Honest Loan Accounting:** Separates borrowed cash (`loan`) from real income and logs repayments separately (`repayment`) so paying back a friend never inflates your spending totals.
* **Emergency Buffer & Recovery Mode:** Optionally ring-fence 10% of incoming funds for emergencies; unexpected costs draw from that buffer first and trigger a calm daily survival cap instead of guilt warnings.
* **Active Co-Pilot Output:** Includes a **"Can I Afford This?"** purchase simulator, pure-Python ASCII category bar charts, and a **Small-Leak Detector** (flags categories hit 3+ times).
* **Zero-Dependency Persistence:** Auto-saves locally to `ganji_data.json` with graceful error recovery—nothing to install.

---

## Sample Output

```text
==========================================================
                  GANJI TRACKER SUMMARY
==========================================================
  Real Income          : KES   2,000.00
  Normal Spending      : KES     650.00
  Remaining Balance    : KES   1,350.00
  Emergency Buffer     : KES     200.00 (protected)
----------------------------------------------------------
  Safe to Spend        : KES 164.29/day (7 days left)
  Status               : HEALTHY - Spending is under control.

  Spending Breakdown:
    Food                    ################ KES     450 (69.2%)
    Data/Wi-Fi              #####            KES     150 (23.1%)
    Transport               #                KES      50 ( 7.7%)

  Small-Leak Alerts (3+ spends in the same category):
    [!] Food: 3 times totaling KES 450.00

```

---

## Quick Start

Requires **Python 3.8+** (no third-party packages required).

```bash
# 1. Clone the repository
git clone [https://github.com/KingStan-KS/ganji-tracker.git](https://github.com/KingStan-KS/ganji-tracker.git)
cd ganji-tracker

# 2. Run the tracker
python ganji_tracker.py

```

---

## Quick-Log Syntax

```text
<amount> <category> [note] [-r recurring] [-e emergency]

```

| Shortcut | Category | Example |
| --- | --- | --- |
| `1` / `f` / `food` | Food | `150 food chapo madondo` |
| `2` / `t` / `trans` | Transport | `60 trans matatu to town` |
| `3` / `d` / `data` | Data/Wi-Fi | `50 data daily bundles -r` |
| `4` / `c` / `cloth` | Clothing | `500 cloth t-shirt` |
| `5` / `l` / `fun` | Leisure/Drinks/Partying | `300 fun friday hangout` |
| `6` / `m` / `misc` | Miscellaneous | `100 misc printing` |
| `7` / `e` / `emerg` | Emergency | `400 emerg clinic visit -e` |

---

## Engineering Journal

Read [`DEVLOG.md`](DEVLOG.md) for the honest build log—including accounting bugs caught during testing, terminal snags, and design pivots.

## License

This project is open source under the [MIT License](https://www.google.com/search?q=LICENSE).

