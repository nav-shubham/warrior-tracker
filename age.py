import argparse
import calendar
import json
import os
import sys
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import requests

# Force UTF-8 encoding on standard streams to avoid Windows UnicodeEncodeErrors
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


# ─── LOAD ENV ───────────────────────────────────
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

# ─── CONSTANTS & DEFAULTS ───────────────────────
DEFAULT_CONFIG_PATH = "warrior_config.json"
DEFAULT_CONFIG = {
    "character_name": "SHUBHAM",
    "birth_date": "2001-09-22",
    "target_age": 27,
    "mission_date": "2026-11-02",
    "mission_title": "MISSION: 2 Nov 2026",
    "life_expectancy_years": 80
}

WARRIOR_QUOTES = [
    "Precision in time = leverage.",
    "He who has a why to live can bear almost any how. — Nietzsche",
    "Discipline is the bridge between goals and accomplishment. — Jim Rohn",
    "We are what we repeatedly do. Excellence, then, is not an act, but a habit. — Aristotle",
    "Time is the only coin you have. Only you can determine how it will be spent. — Carl Sandburg",
    "Focus on being productive instead of busy. — Tim Ferriss",
    "The best way to predict the future is to create it. — Peter Drucker",
    "Precision is the antidote to anxiety. Execution is the cure for doubt.",
    "Small daily improvements over time lead to stunning results. — Robin Sharma",
    "Do not seek to follow in the footsteps of the wise. Seek what they sought. — Basho",
    "The warrior's path requires self-mastery above all external conquest.",
    "Freedom is not the absence of boundaries, but the presence of absolute discipline.",
    "It is not that we have a short time to live, but that we waste much of it. — Seneca",
    "How you spend your days is, of course, how you spend your life. — Annie Dillard",
    "The double-edged sword of time: it can be your greatest asset or your silent destroyer."
]

class TermColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ─── TERMINAL COLORS INITIALIZATION ─────────────
def init_terminal():
    if os.name == 'nt':
        os.system('')  # Activates virtual terminal processing (ANSI escape sequences) in Windows

# ─── CONFIG ENGINE ──────────────────────────────
def load_config(config_path):
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not create default config at {config_path}: {e}")
            return DEFAULT_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # Reconcile defaults for any missing key
            for key, val in DEFAULT_CONFIG.items():
                if key not in cfg:
                    cfg[key] = val
            return cfg
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path} ({e}). Using defaults.")
        return DEFAULT_CONFIG

# ─── DYNAMIC WISDOM ENGINE ──────────────────────
def get_daily_quote(ref_date):
    index = ref_date.toordinal() % len(WARRIOR_QUOTES)
    return WARRIOR_QUOTES[index]

# ─── PROGRESS BARS ──────────────────────────────
def generate_themed_bar(percentage, style="green", length=10):
    percentage = max(0.0, min(100.0, percentage))
    filled_len = int((percentage / 100.0) * length)
    empty_len = length - filled_len
    
    filled_chars = {
        "green": "🟩",
        "blue": "🟦",
        "orange": "🟧",
        "red": "🟥",
        "yellow": "🟨",
        "purple": "🟪"
    }
    
    filled_char = filled_chars.get(style, "🟩")
    empty_char = "⬜"
    return filled_char * filled_len + empty_char * empty_len

# ─── METRICS ENGINE ─────────────────────────────
def get_warrior_metrics(cfg, today=None):
    if today is None:
        today = date.today()

    dob = date.fromisoformat(cfg["birth_date"])
    target_age = cfg["target_age"]
    mission_date = date.fromisoformat(cfg["mission_date"])
    life_expectancy = cfg["life_expectancy_years"]

    # 1. Character Age
    age = relativedelta(today, dob)
    total_days = (today - dob).days

    # 2. Level Progress (to next birthday)
    next_bday = date(today.year, dob.month, dob.day)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    days_to_level = (next_bday - today).days
    # Progress towards next birthday (out of roughly 365 days)
    lvl_progress = max(0.0, min(100.0, ((365.0 - days_to_level) / 365.0) * 100.0))

    # 3. Calendar Year
    cy_end = date(today.year, 12, 31)
    days_to_cy = (cy_end - today).days
    cy_progress = max(0.0, min(100.0, ((365.0 - days_to_cy) / 365.0) * 100.0))

    # 4. Target Age Milestone
    bday_target = date(dob.year + target_age, dob.month, dob.day)
    days_to_target = (bday_target - today).days

    bday_current_year = date(today.year, dob.month, dob.day)
    if bday_current_year > today:
        bday_current_year = bday_current_year.replace(year=today.year - 1)

    total_span = (bday_target - bday_current_year).days
    elapsed = (today - bday_current_year).days
    progress_target = (elapsed / total_span) * 100 if total_span > 0 else 0

    # 5. Mission Countdown
    mission_start = bday_current_year
    mission_total = (mission_date - mission_start).days
    mission_elapsed = (today - mission_start).days
    mission_days_left = (mission_date - today).days
    mission_progress = (mission_elapsed / mission_total) * 100 if mission_total > 0 else 0

    # 6. Macro Life Progress (Against Expectancy)
    death_date = date(dob.year + life_expectancy, dob.month, dob.day)
    life_total = (death_date - dob).days
    life_elapsed = (today - dob).days
    life_progress = (life_elapsed / life_total) * 100 if life_total > 0 else 0
    days_left_life = (death_date - today).days

    # 7. Month Progress
    _, last_day = calendar.monthrange(today.year, today.month)
    month_start = date(today.year, today.month, 1)
    month_end = date(today.year, today.month, last_day)
    month_total = (month_end - month_start).days + 1
    month_elapsed = (today - month_start).days + 1
    month_progress = (month_elapsed / month_total) * 100

    # 8. Week Progress
    week_elapsed = today.weekday() + 1  # Mon = 1, Sun = 7
    week_progress = (week_elapsed / 7.0) * 100.0

    return {
        "character_name": cfg["character_name"],
        "birth_date": dob,
        "age": age,
        "total_days": total_days,
        "lvl": days_to_level,
        "lvl_progress": lvl_progress,
        "cy": days_to_cy,
        "cy_progress": cy_progress,
        "target_age": target_age,
        "days_to_target": days_to_target,
        "progress_target": progress_target,
        "mission_title": cfg["mission_title"],
        "mission_days": mission_days_left,
        "mission_progress": mission_progress,
        "life_expectancy": life_expectancy,
        "life_progress": life_progress,
        "days_left_life": days_left_life,
        "month_progress": month_progress,
        "month_name": today.strftime("%B"),
        "week_progress": week_progress,
        "today_str": today.strftime("%A, %b %d, %Y")
    }

# ─── TELEGRAM NOTIFICATION SYSTEM ──────────────
def send_telegram_notification(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: BOT_TOKEN or CHAT_ID is not configured in your environment (.env file).")
        return False
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"Telegram notification failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Network error sending Telegram notification: {e}")
        return False

# ─── TERMINAL DASHBOARD PRINTER ─────────────────
def print_terminal_dashboard(m, urgency, quote, simulated=False):
    init_terminal()

    def console_bar(perc, color_code, length=12):
        perc = max(0.0, min(100.0, perc))
        filled = int((perc / 100.0) * length)
        empty = length - filled
        bar_char = "█"
        empty_char = "░"
        return f"{color_code}{bar_char * filled}{TermColors.RESET}{empty_char * empty}"

    border = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sim_indicator = f" {TermColors.RED}[SIMULATED MODE]{TermColors.RESET}" if simulated else ""

    print(f"\n{TermColors.HEADER}{TermColors.BOLD}🎮 WARRIOR STATUS: {m['character_name']} 🎮{sim_indicator}{TermColors.RESET}")
    print(f"{TermColors.CYAN}{border}{TermColors.RESET}")
    
    print(f"📅 {TermColors.BOLD}Reference Date:{TermColors.RESET} {m['today_str']}")
    print(f"👤 {TermColors.BOLD}Character Age:{TermColors.RESET} {m['age'].years}y {m['age'].months}m {m['age'].days}d  ({TermColors.GREEN}{m['total_days']:,}{TermColors.RESET} days total)")
    print(f"♾️  {TermColors.BOLD}Life Expectancy:{TermColors.RESET} {m['life_expectancy']}y Milestone")
    print(f"   {console_bar(m['life_progress'], TermColors.BLUE)} {TermColors.BOLD}{m['life_progress']:.1f}%{TermColors.RESET} ({m['days_left_life']:,} days left)\n")
    
    print(f"📊 {TermColors.BOLD}Level Progress (Age Up):{TermColors.RESET}")
    print(f"   {console_bar(m['lvl_progress'], TermColors.GREEN)} {TermColors.BOLD}{m['lvl_progress']:.1f}%{TermColors.RESET} ({m['lvl']} days left)\n")

    print(f"📅 {TermColors.BOLD}Calendar Year Progress:{TermColors.RESET}")
    print(f"   {console_bar(m['cy_progress'], TermColors.YELLOW)} {TermColors.BOLD}{m['cy_progress']:.1f}%{TermColors.RESET} ({m['cy']} days left)\n")

    print(f"🎯 {TermColors.BOLD}Milestone: Age {m['target_age']}:{TermColors.RESET}")
    print(f"   {console_bar(m['progress_target'], TermColors.HEADER)} {TermColors.BOLD}{m['progress_target']:.1f}%{TermColors.RESET} ({m['days_to_target']} days left)\n")

    mission_color = TermColors.GREEN
    if "CRITICAL" in urgency:
        mission_color = TermColors.RED
    elif "FINAL" in urgency:
        mission_color = TermColors.YELLOW
    print(f"🚀 {TermColors.BOLD}{m['mission_title']}:{TermColors.RESET}")
    print(f"   {console_bar(m['mission_progress'], mission_color)} {TermColors.BOLD}{m['mission_progress']:.1f}%{TermColors.RESET} ({m['mission_days']} days remaining)\n")

    print(f"⚡ {TermColors.BOLD}Status:{TermColors.RESET} {mission_color}{TermColors.BOLD}{urgency}{TermColors.RESET}")
    print(f"{TermColors.CYAN}{border}{TermColors.RESET}")
    print(f"💡 {TermColors.BOLD}Daily Wisdom:{TermColors.RESET} {TermColors.CYAN}{quote}{TermColors.RESET}\n")

# ─── MAIN FUNCTION ──────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Warrior Life & Milestone Dashboard Tracker")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Print beautiful dashboard locally without sending Telegram")
    parser.add_argument("-f", "--force", action="store_true", help="Force send notifications even if in simulate mode")
    parser.add_argument("-s", "--simulate", type=str, help="Simulate a custom date in YYYY-MM-DD format")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config JSON file")
    args = parser.parse_args()

    # Load config file
    cfg = load_config(args.config)

    # Establish the reference target date
    simulated = False
    ref_date = date.today()
    if args.simulate:
        try:
            ref_date = date.fromisoformat(args.simulate)
            simulated = True
        except ValueError:
            print(f"Error: Invalid date format for --simulate: '{args.simulate}'. Use YYYY-MM-DD.")
            sys.exit(1)

    # Gather Metrics
    m = get_warrior_metrics(cfg, today=ref_date)

    # Dynamic Urgency System
    if m['mission_days'] <= 30:
        urgency = "⚠️ CRITICAL ZONE"
        mission_bar_style = "red"
    elif m['mission_days'] <= 100:
        urgency = "🔥 FINAL PHASE"
        mission_bar_style = "orange"
    else:
        urgency = "🧭 BUILD PHASE"
        mission_bar_style = "green"

    # Themed Progress Bars for Telegram Message
    bar_lvl = generate_themed_bar(m['lvl_progress'], "green", 10)
    bar_cy = generate_themed_bar(m['cy_progress'], "yellow", 10)
    bar_target = generate_themed_bar(m['progress_target'], "purple", 10)
    bar_mission = generate_themed_bar(m['mission_progress'], mission_bar_style, 10)
    bar_life = generate_themed_bar(m['life_progress'], "blue", 10)

    # Deterministic Daily Wisdom
    quote = get_daily_quote(ref_date)

    # Draft HTML formatted Telegram message
    message = (
        f"🎮 <b>WARRIOR STATUS: {m['character_name']}</b> 🎮\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━</code>\n\n"

        f"👤 <b>Character Age</b>\n"
        f"{m['age'].years}y {m['age'].months}m {m['age'].days}d\n"
        f"<code>{m['total_days']:,}</code> days\n\n"

        f"📊 <b>Level Progress (Age Up)</b>\n"
        f"{bar_lvl} <b>{m['lvl_progress']:.0f}%</b>\n"
        f"<i>{m['lvl']} days left</i>\n\n"

        f"📅 <b>Calendar Year</b>\n"
        f"{bar_cy} <b>{m['cy_progress']:.0f}%</b>\n"
        f"<i>{m['cy']} days left</i>\n\n"

        f"🎯 <b>Milestone: Age {m['target_age']}</b>\n"
        f"{bar_target} <b>{m['progress_target']:.0f}%</b>\n"
        f"<i>{m['days_to_target']} days left</i>\n\n"

        f"🚀 <b>{m['mission_title']}</b>\n"
        f"{bar_mission} <b>{m['mission_progress']:.0f}%</b>\n"
        f"<i>{m['mission_days']} days remaining</i>\n\n"
        
        f"♾️ <b>Macro Life Progress ({m['life_expectancy']}y)</b>\n"
        f"{bar_life} <b>{m['life_progress']:.1f}%</b>\n"
        f"<i>{m['days_left_life']:,} days remaining</i>\n\n"

        f"⚡ <b>Status:</b> {urgency}\n\n"

        f"<code>━━━━━━━━━━━━━━━━━━━━</code>\n"
        f"💡 {quote}"
    )

    # Trigger action based on flags
    # Default behavior: send notification to Telegram UNLESS dry-run is specified
    # If in simulation mode, default to dry-run (do NOT send to Telegram) unless force is passed.
    if args.dry_run or (simulated and not args.force):
        print_terminal_dashboard(m, urgency, quote, simulated=simulated)
        if simulated and not args.force:
            print("(Simulation runs default to terminal output. Use --force to push mock notifications to Telegram.)")
    else:
        print_terminal_dashboard(m, urgency, quote, simulated=simulated)
        print("Sending Warrior Status notification to Telegram...")
        success = send_telegram_notification(message)
        if success:
            print("Notification dispatched successfully!")
        else:
            print("Failed to dispatch notification.")

if __name__ == "__main__":
    main()
