import requests
import os
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# ─── LOAD ENV ───────────────────────────────────
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

# ─── CONFIG ─────────────────────────────────────
BIRTH_DATE = date(2001, 9, 22)
TARGET_AGE = 27

# ─── METRICS ENGINE ─────────────────────────────
def get_warrior_metrics(dob, target_age):
    today = date.today()
    
    # Age
    age = relativedelta(today, dob)
    total_days = (today - dob).days

    # Next birthday
    next_bday = date(today.year, dob.month, dob.day)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    days_to_level = (next_bday - today).days

    # Calendar Year
    cy_end = date(today.year, 12, 31)
    days_to_cy = (cy_end - today).days

    # Target Age milestone
    bday_target = date(dob.year + target_age, dob.month, dob.day)
    days_to_target = (bday_target - today).days

    # Progress for target age
    bday_current_year = date(today.year, dob.month, dob.day)
    if bday_current_year > today:
        bday_current_year = bday_current_year.replace(year=today.year - 1)

    total_span = (bday_target - bday_current_year).days
    elapsed = (today - bday_current_year).days
    progress_target = (elapsed / total_span) * 100 if total_span > 0 else 0

    # 🚀 Mission: 2 Nov 2026
    mission_start = bday_current_year
    mission_end = date(2026, 11, 2)

    mission_total = (mission_end - mission_start).days
    mission_elapsed = (today - mission_start).days
    mission_days_left = (mission_end - today).days

    mission_progress = (mission_elapsed / mission_total) * 100 if mission_total > 0 else 0

    return {
        "age": age,
        "total_days": total_days,
        "lvl": days_to_level,
        "cy": days_to_cy,
        "target_age": target_age,
        "days_to_target": days_to_target,
        "progress_target": progress_target,
        "mission_days": mission_days_left,
        "mission_progress": mission_progress
    }

# ─── PROGRESS BARS ──────────────────────────────
def generate_bar(days_left, total=365):
    progress = max(0, min(100, ((total - days_left) / total) * 100))
    bar_len = 10
    filled = int((progress / 100) * bar_len)
    return "🟩" * filled + "⬜" * (bar_len - filled), progress

def generate_progress_bar(percentage):
    bar_len = 10
    filled = int((max(0, min(100, percentage)) / 100) * bar_len)
    return "🟩" * filled + "⬜" * (bar_len - filled)

# ─── TELEGRAM ───────────────────────────────────
def send_telegram_notification(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

# ─── EXECUTION ──────────────────────────────────
m = get_warrior_metrics(BIRTH_DATE, TARGET_AGE)

bar_lvl, perc_lvl = generate_bar(m['lvl'])
bar_cy, perc_cy   = generate_bar(m['cy'])
bar_target        = generate_progress_bar(m['progress_target'])
bar_mission       = generate_progress_bar(m['mission_progress'])

# ─── URGENCY SYSTEM ─────────────────────────────
if m['mission_days'] <= 30:
    urgency = "⚠️ CRITICAL ZONE"
elif m['mission_days'] <= 100:
    urgency = "🔥 FINAL PHASE"
else:
    urgency = "🧭 BUILD PHASE"

# ─── MESSAGE ────────────────────────────────────
message = (
    f"🎮 <b>WARRIOR STATUS: SHUBHAM</b> 🎮\n"
    f"<code>━━━━━━━━━━━━━━━━━━━━</code>\n\n"

    f"👤 <b>Character Age</b>\n"
    f"{m['age'].years}y {m['age'].months}m {m['age'].days}d\n"
    f"<code>{m['total_days']:,}</code> days\n\n"

    f"📊 <b>Level Progress</b>\n"
    f"{bar_lvl} <b>{perc_lvl:.0f}%</b>\n"
    f"<i>{m['lvl']} days left</i>\n\n"

    f"📅 <b>Calendar Year</b>\n"
    f"{bar_cy} <b>{perc_cy:.0f}%</b>\n"
    f"<i>{m['cy']} days left</i>\n\n"

    f"🎯 <b>Milestone: Age {m['target_age']}</b>\n"
    f"{bar_target} <b>{m['progress_target']:.0f}%</b>\n"
    f"<i>{m['days_to_target']} days left</i>\n\n"

    f"🚀 <b>Mission: 2 Nov 2026</b>\n"
    f"{bar_mission} <b>{m['mission_progress']:.0f}%</b>\n"
    f"<i>{m['mission_days']} days remaining</i>\n\n"

    f"⚡ <b>Status:</b> {urgency}\n\n"

    f"<code>━━━━━━━━━━━━━━━━━━━━</code>\n"
    f"💡 Precision in time = leverage."
)

# ─── FIRE ───────────────────────────────────────
send_telegram_notification(message)
