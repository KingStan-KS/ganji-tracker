"""
Ganji Tracker - University Student Money Manager

A low-friction, terminal-based expense tracker designed for university students
who receive weekly allowances, earn from side hustles, or occasionally borrow
from friends.

"""

import datetime
import json
import os

#
# GLOBAL CONSTANTS
# Written in UPPER_CASE by Python convention (PEP 8) so readers know
# these values should not be modified while the program runs.
# 

CURRENCY = "KES"

# Save the data file in the exact same folder as this Python script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "ganji_data.json")

# Tuples are used here because these options are fixed (immutable)
INCOME_SOURCES = (
    "Weekly Allowance (Parents/Guardian)",
    "Side Hustle",
    "Borrowed from Friend (Loan)",
)

EXPENSE_CATEGORIES = (
    "Food",
    "Transport",
    "Data/Wi-Fi",
    "Clothing",
    "Leisure/Drinks/Partying",
    "Miscellaneous",
    "Emergency",
)

# Dictionary mapping short user shortcuts to the official category names.
# This lets users type '1', 'f', or 'food' without creating messy typos.
# These shortcuts are limited and do not cover every possible word but enough to serve the purpose as of now
CATEGORY_SHORTCUTS = {
    "1": "Food", "f": "Food", "food": "Food",
    "2": "Transport", "t": "Transport", "trans": "Transport", "fare": "Transport",
    "3": "Data/Wi-Fi", "d": "Data/Wi-Fi", "data": "Data/Wi-Fi", "wifi": "Data/Wi-Fi",
    "4": "Clothing", "c": "Clothing", "cloth": "Clothing", "clothes": "Clothing",
    "5": "Leisure/Drinks/Partying", "l": "Leisure/Drinks/Partying",
    "fun": "Leisure/Drinks/Partying", "party": "Leisure/Drinks/Partying",
    "drinks": "Leisure/Drinks/Partying", "leisure": "Leisure/Drinks/Partying",
    "6": "Miscellaneous", "m": "Miscellaneous", "misc": "Miscellaneous",
    "7": "Emergency", "e": "Emergency", "emerg": "Emergency", "emergency": "Emergency",
}


# ===========================================================================
# SECTION 1: FILE STORAGE 
# ===========================================================================

def create_empty_state():
    """
    Create and return a fresh dictionary for a brand-new user.
    We pass this 'state' dictionary into functions instead of using
    the 'global' keyword, which keeps data flow easy to trace.
    """
    return {
        "days_left": 7,
        "emergency_buffer": 0.0,
        "transactions": [],
    }


def load_data():
    """
    Read saved records from ganji_data.json if the file exists.
    If the file is missing or corrupted, return a fresh state safely
    so the program never crashes on startup.
    """
    if not os.path.exists(DATA_FILE):
        return create_empty_state()

    try:
        # 'with open(...)' automatically closes the file even if an error occurs
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Basic sanity check to make sure the JSON file has what we expect
        if type(data) is not dict or "transactions" not in data:
            print("  [!] Saved file format was invalid. Starting with clean data.")
            return create_empty_state()

        return {
            "days_left": int(data.get("days_left", 7)),
            "emergency_buffer": float(data.get("emergency_buffer", 0.0)),
            "transactions": list(data["transactions"]),
        }
    except (json.JSONDecodeError, ValueError, OSError) as error:
        print(f"  [!] Could not load saved file ({error}). Starting fresh.")
        return create_empty_state()


def save_data(state):
    """Write the current state dictionary to ganji_data.json."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            # indent=2 makes the JSON file neatly formatted and human-readable
            json.dump(state, file, indent=2)
    except OSError as error:
        print(f"  [!] Warning: Could not save your data ({error}).")


# ===========================================================================
# SECTION 2: INPUT VALIDATION HELPERS 
# ===========================================================================

def get_positive_amount(prompt):
    """
    Keep asking the user until they enter a valid number greater than 0.
    Prevents negative numbers or letters from corrupting the balance.
    """
    while True:
        raw_input = input(prompt).strip()
        try:
            amount = float(raw_input)
        except ValueError:
            print("  [!] Invalid input. Please enter a number (e.g., 150 or 1200.50).")
            continue

        if amount <= 0:
            print("  [!] Amount must be greater than zero.")
            continue

        return amount


def get_menu_choice(prompt, low, high):
    """Keep asking until the user enters a whole number between low and high."""
    while True:
        raw_input = input(prompt).strip()
        try:
            choice = int(raw_input)
        except ValueError:
            print(f"  [!] Please enter a whole number between {low} and {high}.")
            continue

        if low <= choice <= high:
            return choice

        print(f"  [!] Out of range. Choose a number from {low} to {high}.")


def get_transaction_date(prompt):
    """
    Ask for a date using quick shortcuts so logging past expenses is painless:
    - Press Enter or 't' -> today's date
    - Type 'y'           -> yesterday's date
    - Type YYYY-MM-DD    -> any specific date
    Returns the date as a string (e.g., '2026-11-25').
    """
    today = datetime.date.today()

    while True:
        text = input(prompt).strip().lower()

        if text == "" or text == "t" or text == "today":
            return today.isoformat()
        elif text == "y" or text == "yesterday":
            yesterday = today - datetime.timedelta(days=1)
            return yesterday.isoformat()
        else:
            # Validate custom YYYY-MM-DD format using datetime
            try:
                parsed_date = datetime.date.fromisoformat(text)
                return parsed_date.isoformat()
            except ValueError:
                print("  [!] Invalid date. Use YYYY-MM-DD, 'y' for yesterday, or press Enter.")


def choose_from_options(title, options):
    """Display a numbered list from a tuple and return the chosen text."""
    print("\n" + title)
    # Loop with an index starting from 1 so the menu feels natural to users
    for index in range(len(options)):
        print(f"  {index + 1}. {options[index]}")

    choice = get_menu_choice("Select option number: ", 1, len(options))
    return options[choice - 1]


def generate_next_id(transactions):
    """Return the next available ID number for a new transaction."""
    if len(transactions) == 0:
        return 1

    highest_id = 0
    for tx in transactions:
        if tx["id"] > highest_id:
            highest_id = tx["id"]
    return highest_id + 1


# ===========================================================================
# SECTION 3: CORE USER ACTIONS (Adding Income, Bulk Expenses, Repayments)
# ===========================================================================

def log_money_in(state):
    """
    Log incoming money from parents, side hustles, or a friend's loan.
    Loans are stored separately from real income because they must be repaid.
    """
    transactions = state["transactions"]
    source = choose_from_options("Where did the ganji come from?", INCOME_SOURCES)
    amount = get_positive_amount(f"Amount ({CURRENCY}): ")
    tx_date = get_transaction_date("Date [Enter=today, y=yesterday, YYYY-MM-DD]: ")

    # Case 1: Borrowed money (creates a debt record)
    if source == "Borrowed from Friend (Loan)":
        lender = input("Who did you borrow from? ").strip()
        if lender == "":
            lender = "Friend"

        new_loan = {
            "id": generate_next_id(transactions),
            "kind": "loan",
            "amount": amount,
            "category": "Loan",
            "note": lender,
            "recurring": False,
            "emergency": False,
            "repaid": False,
            "date": tx_date,
        }
        transactions.append(new_loan)
        save_data(state)
        print(f"  [+] Logged loan of {CURRENCY} {amount:,.2f} from {lender} ({tx_date}).")
        return

    # Case 2: Real income (weekly allowance or side hustle)
    note = input("Short note [press Enter to skip]: ").strip()
    if note == "":
        note = source

    new_income = {
        "id": generate_next_id(transactions),
        "kind": "income",
        "amount": amount,
        "category": source,
        "note": note,
        "recurring": False,
        "emergency": False,
        "repaid": False,
        "date": tx_date,
    }
    transactions.append(new_income)

    # Offer to ring-fence 10% into an Emergency Buffer for unexpected events
    skim_amount = round(amount * 0.10, 2)
    reply = input(
        f"Save 10% ({CURRENCY} {skim_amount:,.2f}) into your Emergency Buffer? (y/n): "
    ).strip().lower()

    if reply == "y" or reply == "yes":
        state["emergency_buffer"] = round(state["emergency_buffer"] + skim_amount, 2)
        print(f"  [+] Moved {CURRENCY} {skim_amount:,.2f} into your protected Emergency Buffer.")

    save_data(state)
    print(f"  [+] Logged income of {CURRENCY} {amount:,.2f} ({source}) on {tx_date}.")


def quick_bulk_expenses(state):
    """
    Low-friction expense logger.
    Instead of answering 5 separate prompts per item, the user types one short
    line per expense and stays inside this loop until they finish catching up.
    """
    transactions = state["transactions"]
    batch_date = get_transaction_date("\nBatch date [Enter=today, y=yesterday, YYYY-MM-DD]: ")

    print("\n--- QUICK BULK EXPENSE LOGGER ---")
    print("Format : <amount> <category> [note] [-r recurring] [-e emergency]")
    print("Cats   : 1/food  2/trans  3/data  4/cloth  5/fun  6/misc  7/emerg")
    print("Example: 150 food chapo madondo   |   50 data bundles -r")
    print("Tip    : Type 'date' to change date, or press Enter on a blank line to finish.\n")

    added_count = 0

    while True:
        line = input(f"[{batch_date}] > ").strip()

        # Exit the bulk loop when the user presses Enter or types 'done'
        if line == "" or line.lower() in ("done", "q", "exit"):
            break

        # Allow switching dates mid-session (useful for Sunday catch-ups)
        if line.lower() == "date":
            batch_date = get_transaction_date("New batch date [Enter=today, y=yesterday, YYYY-MM-DD]: ")
            continue

        # Split the user's sentence into words (Unit III: string.split())
        parts = line.split()
        if len(parts) < 2:
            print("  [!] Please enter at least <amount> and <category> (e.g., 120 food).")
            continue

        # Step 1: Parse the amount (first word)
        try:
            amount = float(parts[0])
            if amount <= 0:
                print("  [!] Amount must be greater than 0.")
                continue
        except ValueError:
            print("  [!] The first value must be a valid number (e.g., 150).")
            continue

        # Step 2: Look up the category shortcut (second word)
        raw_cat = parts[1].lower()
        if raw_cat not in CATEGORY_SHORTCUTS:
            print("  [!] Unknown category. Use 1-7 or: food, trans, data, cloth, fun, misc, emerg.")
            continue
        category = CATEGORY_SHORTCUTS[raw_cat]

        # Step 3: Check remaining words for optional flags (-r, -e) and the note
        is_recurring = False
        is_emergency = (category == "Emergency")
        note_words = []

        for word in parts[2:]:
            lower_word = word.lower()
            if lower_word == "-r" or lower_word == "--recurring":
                is_recurring = True
            elif lower_word == "-e" or lower_word == "--emergency":
                is_emergency = True
            else:
                note_words.append(word)

        # Join remaining words back into a clean description string
        note = " ".join(note_words)
        if note == "":
            note = category

        new_expense = {
            "id": generate_next_id(transactions),
            "kind": "expense",
            "amount": amount,
            "category": category,
            "note": note,
            "recurring": is_recurring,
            "emergency": is_emergency,
            "repaid": False,
            "date": batch_date,
        }
        transactions.append(new_expense)
        added_count = added_count + 1

        # If this was an emergency, automatically absorb what we can from the buffer
        buffer_note = ""
        if is_emergency and state["emergency_buffer"] > 0:
            covered = min(state["emergency_buffer"], amount)
            state["emergency_buffer"] = round(state["emergency_buffer"] - covered, 2)
            buffer_note = f" (buffer covered {CURRENCY} {covered:,.2f})"

        tag_text = ""
        if is_recurring:
            tag_text += " [RECURRING]"
        if is_emergency:
            tag_text += " [EMERGENCY]"

        print(f"  [-] Saved {CURRENCY} {amount:,.2f} | {category} | {note}{tag_text}{buffer_note}")

    # Save to disk once at the end of the batch
    if added_count > 0:
        save_data(state)
        print(f"  [OK] Saved {added_count} expense(s) to ganji_data.json.")


def repay_loan(state):
    """
    Mark an unpaid loan as repaid.
    Logged as kind='repayment' (NOT 'expense') so paying back a friend
    reduces your cash honestly without inflating your spending totals.
    """
    transactions = state["transactions"]

    # List comprehension (Unit IV) to filter only unpaid loans
    unpaid_loans = [tx for tx in transactions if tx["kind"] == "loan" and not tx["repaid"]]

    if len(unpaid_loans) == 0:
        print("\n  You have no unpaid loans. Clean slate!")
        return

    print("\nUnpaid Loans:")
    for index in range(len(unpaid_loans)):
        loan = unpaid_loans[index]
        print(f"  {index + 1}. {loan['note']} - {CURRENCY} {loan['amount']:,.2f} ({loan['date']})")

    choice = get_menu_choice("Select loan to mark as repaid (0 to cancel): ", 0, len(unpaid_loans))
    if choice == 0:
        return

    selected_loan = unpaid_loans[choice - 1]
    selected_loan["repaid"] = True

    repayment_record = {
        "id": generate_next_id(transactions),
        "kind": "repayment",
        "amount": selected_loan["amount"],
        "category": "Loan Repayment",
        "note": "Repaid " + selected_loan["note"],
        "recurring": False,
        "emergency": False,
        "repaid": True,
        "date": datetime.date.today().isoformat(),
    }
    transactions.append(repayment_record)
    save_data(state)
    print(f"  [OK] Marked loan of {CURRENCY} {selected_loan['amount']:,.2f} to {selected_loan['note']} as repaid.")


# ===========================================================================
# SECTION 4: ANALYTICS, SUMMARY REPORT & SIMULATOR
# ===========================================================================

def compute_summary(state):
    """
    Fruitful function that calculates all financial metrics from scratch
    based on the transaction history and returns them in a single dictionary.
    """
    transactions = state["transactions"]
    days_left = state["days_left"]

    total_income = 0.0
    total_borrowed = 0.0
    total_repaid = 0.0
    unpaid_debt = 0.0
    normal_spent = 0.0
    emergency_spent = 0.0

    # Dictionaries to track total amount and frequency per category
    by_category = {}
    category_counts = {}
    recurring_list = []

    # Walk through every transaction once and accumulate totals
    for tx in transactions:
        kind = tx["kind"]
        amt = tx["amount"]

        if kind == "income":
            total_income += amt
        elif kind == "loan":
            total_borrowed += amt
            if not tx["repaid"]:
                unpaid_debt += amt
        elif kind == "repayment":
            total_repaid += amt
        elif kind == "expense":
            cat = tx["category"]
            by_category[cat] = by_category.get(cat, 0.0) + amt

            if tx["emergency"]:
                emergency_spent += amt
            else:
                normal_spent += amt
                # Count non-emergency spends to catch "Small Leaks"
                category_counts[cat] = category_counts.get(cat, 0) + 1

            if tx["recurring"]:
                recurring_list.append(tx)

    total_spent = normal_spent + emergency_spent
    total_inflow = total_income + total_borrowed

    # Actual cash currently sitting in wallet / M-Pesa
    cash_on_hand = total_inflow - total_spent - total_repaid

    # Protected buffer cannot exceed the actual cash you currently have
    effective_buffer = min(state["emergency_buffer"], max(0.0, cash_on_hand))
    spendable_cash = max(0.0, cash_on_hand - effective_buffer)

    # Actual Net Worth subtracts money owed to friends
    net_balance = cash_on_hand - unpaid_debt
    safe_daily = spendable_cash / days_left if days_left > 0 else 0.0

    # Chained conditional (Unit II) to determine financial health status.
    # Notice the order: we check the most severe cases first!
    if total_inflow == 0:
        status = "NO FUNDS LOGGED YET"
    elif cash_on_hand < 0:
        status = "OVERDRAWN - Spending exceeds logged cash!"
    elif emergency_spent > 0 and spendable_cash < (total_inflow * 0.25):
        # Fair handling: emergencies trigger Recovery Mode instead of scolding
        status = f"RECOVERY MODE - Emergency hit your cash. Stick to {CURRENCY} {safe_daily:,.0f}/day."
    else:
        normal_ratio = normal_spent / total_inflow
        if normal_ratio >= 0.85:
            status = "CRITICAL - Over 85% spent on normal expenses."
        elif normal_ratio >= 0.60:
            status = "CAUTION - Past 60% spent. Pace discretionary spending."
        else:
            status = "HEALTHY - Spending is under control."

    # Identify "Small Leaks": any non-emergency category spent on 3 or more times
    small_leaks = []
    for cat, count in category_counts.items():
        if count >= 3:
            small_leaks.append((cat, count, by_category[cat]))

    return {
        "total_income": total_income,
        "total_repaid": total_repaid,
        "unpaid_debt": unpaid_debt,
        "normal_spent": normal_spent,
        "emergency_spent": emergency_spent,
        "total_spent": total_spent,
        "cash_on_hand": cash_on_hand,
        "effective_buffer": effective_buffer,
        "spendable_cash": spendable_cash,
        "net_balance": net_balance,
        "safe_daily": safe_daily,
        "status": status,
        "by_category": by_category,
        "small_leaks": small_leaks,
        "recurring": recurring_list,
    }


def show_summary(state):
    """Print the financial dashboard, ASCII bar chart, and spending alerts."""
    s = compute_summary(state)
    days_left = state["days_left"]

    print("\n" + "=" * 58)
    print("                  GANJI TRACKER SUMMARY")
    print("=" * 58)
    print(f"  Real Income          : {CURRENCY} {s['total_income']:>10,.2f}")
    print(f"  Normal Spending      : {CURRENCY} {s['normal_spent']:>10,.2f}")

    if s["emergency_spent"] > 0:
        print(f"  Emergency Spending   : {CURRENCY} {s['emergency_spent']:>10,.2f}")
    if s["total_repaid"] > 0:
        print(f"  Loans Repaid         : {CURRENCY} {s['total_repaid']:>10,.2f}")

    # Only display debt breakdown when the student actually owes someone
    if s["unpaid_debt"] > 0:
        print(f"  Cash on Hand         : {CURRENCY} {s['cash_on_hand']:>10,.2f}")
        print(f"  Unpaid Loans         : {CURRENCY} {s['unpaid_debt']:>10,.2f}")
        print(f"  Actual Net Balance   : {CURRENCY} {s['net_balance']:>10,.2f}")
    else:
        print(f"  Remaining Balance    : {CURRENCY} {s['cash_on_hand']:>10,.2f}")

    if s["effective_buffer"] > 0:
        print(f"  Emergency Buffer     : {CURRENCY} {s['effective_buffer']:>10,.2f} (protected)")

    print("-" * 58)
    print(f"  Safe to Spend        : {CURRENCY} {s['safe_daily']:,.2f}/day ({days_left} days left)")
    print(f"  Status               : {s['status']}")

    # Draw a simple ASCII bar chart sorted from highest to lowest spend
    if len(s["by_category"]) > 0:
        print("\n  Spending Breakdown:")
        max_amount = max(s["by_category"].values())

        # Convert dict items to a list of (amount, category) tuples to sort easily
        ranked = []
        for cat, amt in s["by_category"].items():
            ranked.append((amt, cat))
        ranked.sort(reverse=True)

        for amt, cat in ranked:
            percent = (amt / s["total_spent"] * 100) if s["total_spent"] > 0 else 0
            bar_length = max(1, int((amt / max_amount) * 16))
            bar = "#" * bar_length
            print(f"    {cat:<23} {bar:<16} {CURRENCY} {amt:>7,.0f} ({percent:4.1f}%)")

    if len(s["small_leaks"]) > 0:
        print("\n  Small-Leak Alerts (3+ spends in the same category):")
        for cat, count, total in s["small_leaks"]:
            print(f"    [!] {cat}: {count} times totaling {CURRENCY} {total:,.2f}")

    if len(s["recurring"]) > 0:
        print("\n  Flagged Recurring Expenses:")
        for tx in s["recurring"]:
            print(f"    * {tx['note']} ({tx['category']}) - {CURRENCY} {tx['amount']:,.2f}")

    print("=" * 58)


def afford_simulator(state):
    """
    Co-pilot tool: lets the user test a planned purchase BEFORE buying
    to see how hard it will hit their daily Safe-to-Spend limit.
    """
    s = compute_summary(state)
    days_left = state["days_left"]
    planned_cost = get_positive_amount(f"\nPlanned purchase amount ({CURRENCY}): ")

    cash_after = s["spendable_cash"] - planned_cost
    new_daily = max(0.0, cash_after / days_left) if days_left > 0 else 0.0

    print("\n--- AFFORDABILITY CHECK ---")
    print(f"  Current Safe-to-Spend : {CURRENCY} {s['safe_daily']:,.2f}/day")

    if cash_after < 0:
        shortfall = abs(cash_after)
        print(f"  [X] TOO STEEP - Exceeds your spendable cash by {CURRENCY} {shortfall:,.2f}.")
        if s["effective_buffer"] >= shortfall:
            print("      (Only possible if you dip into your Emergency Buffer.)")
    else:
        print(f"  After Purchase        : {CURRENCY} {new_daily:,.2f}/day for {days_left} days")
        if s["safe_daily"] > 0:
            drop_percent = ((s["safe_daily"] - new_daily) / s["safe_daily"]) * 100
        else:
            drop_percent = 0.0

        if drop_percent >= 50:
            print(f"  [!] HEAVY HIT - Cuts your daily budget by {drop_percent:.0f}%. Sleep on it.")
        else:
            print(f"  [OK] MANAGEABLE - Reduces your daily budget by {drop_percent:.0f}%.")


# ===========================================================================
# SECTION 5: MAIN PROGRAM LOOP
# ===========================================================================

def main():
    """Load saved data and run the interactive main menu loop."""
    state = load_data()
    count = len(state["transactions"])
    print(f"Welcome to Ganji Tracker ({count} saved record(s) loaded)")

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Quick-Log Expenses (Fast / Bulk Mode)")
        print("2. Log Money In (Allowance / Hustle / Loan)")
        print("3. View Summary Report & Alerts")
        print("4. 'Can I Afford This?' Check")
        print("5. Repay a Friend's Loan")
        print(f"6. Set Days Left Until Next Allowance (currently {state['days_left']})")
        print("7. Exit")

        choice = get_menu_choice("Choose an action (1-7): ", 1, 7)

        if choice == 1:
            quick_bulk_expenses(state)
        elif choice == 2:
            log_money_in(state)
        elif choice == 3:
            show_summary(state)
        elif choice == 4:
            afford_simulator(state)
        elif choice == 5:
            repay_loan(state)
        elif choice == 6:
            state["days_left"] = get_menu_choice("Days remaining (1-30): ", 1, 30)
            save_data(state)
            print(f"  [OK] Updated days remaining to {state['days_left']}.")
        elif choice == 7:
            print("Data saved. Stay disciplined with your ganji!")
            break


# Standard Python entry-point guard: ensures main() only runs when this file
# is executed directly, not when another file imports its functions.
if __name__ == "__main__":
    main()