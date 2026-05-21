import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit.components.v1 as components

MAX_CLEANING_SLOTS = 2

CARGO_BY_CONTAINER = {
    "Reefer 20ft": ["Daging beku", "Sayur buah", "Farmasi", "General"],
    "Reefer 40ft": ["Daging beku", "Sayur buah", "Farmasi", "General"],
    "Dry 20ft": ["Food grade", "Chemical", "Jagung", "Biji sawit", "General"],
    "Dry 40ft": ["Food grade", "Chemical", "Jagung", "Biji sawit", "General"],
    "Flat Rack 20ft": ["Alat berat", "General"],
    "Flat Rack 40ft": ["Alat berat", "General"],
}

CONTAINER_TYPES = list(CARGO_BY_CONTAINER.keys())

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CleanCycle Dashboard",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# THEME & BACKGROUND
# ============================================================

PANEL_STYLES = {
    "rose": {
        "head": "background:linear-gradient(90deg,#fecdd3,#ffe4e6,#fff1f2);color:#0f172a;",
        "body": "background:rgba(255,255,255,0.92);border-color:#fecdd3;",
    },
    "violet": {
        "head": "background:linear-gradient(90deg,#ddd6fe,#ede9fe,#f5f3ff);color:#0f172a;",
        "body": "background:rgba(245,243,255,0.85);border-color:#ddd6fe;",
    },
    "mint": {
        "head": "background:linear-gradient(90deg,#a7f3d0,#d1fae5,#ecfdf5);color:#0f172a;",
        "body": "background:rgba(236,253,245,0.75);border-color:#a7f3d0;",
    },
    "amber": {
        "head": "background:linear-gradient(90deg,#fde68a,#fef3c7,#fffbeb);color:#0f172a;",
        "body": "background:rgba(255,251,235,0.85);border-color:#fde68a;",
    },
    "sky": {
        "head": "background:linear-gradient(90deg,#bae6fd,#e0f2fe,#f0f9ff);color:#0f172a;",
        "body": "background:rgba(240,249,255,0.85);border-color:#bae6fd;",
    },
}

CARD_STYLES = {
    "hero": "background:rgba(255,255,255,0.9);border:1px solid #fff;",
    "rose": "background:#fff1f2;border:1px solid #fecdd3;",
    "violet": "background:#f5f3ff;border:1px solid #ddd6fe;",
    "mint": "background:#ecfdf5;border:1px solid #a7f3d0;",
    "amber": "background:#fffbeb;border:1px solid #fde68a;",
    "sky": "background:#f0f9ff;border:1px solid #bae6fd;",
    "lime": "background:#f7fee7;border:1px solid #d9f99d;",
    "clock": "background:#f5f3ff;border:1px solid #ddd6fe;text-align:right;",
}


def cc_card(open_tag_extra="", variant="mint"):
    base = (
        "border-radius:24px;padding:20px;margin-bottom:12px;"
        "box-shadow:0 12px 40px rgba(15,23,42,0.08);color:#1e293b;"
    )
    return f'<div class="cc-card" style="{base}{CARD_STYLES.get(variant, CARD_STYLES["mint"])}{open_tag_extra}">'


def cc_card_close():
    return "</div>"


def pastel_tag(text, kind="violet"):
    colors = {
        "violet": "background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;",
        "slate": "background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;",
        "mint": "background:#d1fae5;color:#047857;border:1px solid #6ee7b7;",
        "sky": "background:#e0f2fe;color:#0369a1;border:1px solid #7dd3fc;",
        "amber": "background:#fef3c7;color:#b45309;border:1px solid #fcd34d;",
        "rose": "background:#ffe4e6;color:#be123c;border:1px solid #fda4af;",
        "lime": "background:#ecfccb;color:#4d7c0f;border:1px solid #bef264;",
        "food": "background:#d1fae5;color:#065f46;border:1px solid #34d399;",
    }
    style = colors.get(kind, colors["slate"])
    return (
        f'<span class="cc-tag" style="display:inline-block;padding:5px 12px;'
        f"border-radius:999px;font-size:11px;font-weight:600;margin:3px 6px 3px 0;"
        f'{style}">{text}</span>'
    )


def progress_bar_html(pct, fill_color, label_left, label_right, height=10):
    pct = max(0, min(100, pct))
    return (
        f'<div style="margin:10px 0 6px;">'
        f'<div style="display:flex;justify-content:space-between;font-size:12px;'
        f'color:#475569;margin-bottom:5px;font-weight:500;">'
        f"<span>{label_left}</span><span style='font-weight:700;color:#0f172a;'>"
        f"{label_right}</span></div>"
        f'<div class="cc-pbar" style="height:{height}px;background:#e2e8f0;'
        f'border-radius:999px;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{fill_color};'
        f'border-radius:999px;transition:width 0.5s ease;"></div></div></div>'
    )


def due_time_bar_html(due_datetime):
    now = datetime.now()
    diff = (due_datetime - now).total_seconds() / 3600
    if diff <= 0:
        pct, color, label = 0, "#ef4444", "Waktu habis"
    elif diff >= 48:
        pct, color, label = 100, "#22c55e", f"{diff:.0f}j tersisa"
    else:
        pct = (diff / 48) * 100
        color = "#22c55e" if diff >= 12 else ("#f59e0b" if diff >= 4 else "#ef4444")
        label = f"{int(diff)}j tersisa" if diff >= 1 else f"{int(diff * 60)}m tersisa"
    return progress_bar_html(pct, color, "Sisa waktu due", label)


def panel_header(title, icon, variant="mint"):
    ps = PANEL_STYLES.get(variant, PANEL_STYLES["mint"])
    st.markdown(
        f'<div class="cc-panel-head" style="border-radius:24px 24px 0 0;padding:16px 24px;'
        f"font-weight:700;font-size:16px;display:flex;align-items:center;gap:12px;"
        f'border:1px solid #e2e8f0;border-bottom:none;{ps["head"]}">'
        f'<span style="font-size:22px;">{icon}</span><span>{title}</span></div>',
        unsafe_allow_html=True,
    )


def panel_body_open(variant="mint"):
    ps = PANEL_STYLES.get(variant, PANEL_STYLES["mint"])
    st.markdown(
        f'<div class="cc-panel-body" style="border-radius:0 0 24px 24px;padding:24px;'
        f"border:1px solid #e2e8f0;border-top:none;box-shadow:0 12px 40px rgba(15,23,42,0.06);"
        f'color:#334155;{ps["body"]}">',
        unsafe_allow_html=True,
    )


def panel_body_close():
    st.markdown("</div>", unsafe_allow_html=True)


def inject_tailwind_theme():
    st.markdown(
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    }
  }
}
</script>
<style>
    html, body, .stApp, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    .stApp {
        background-color: #faf8f5 !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 10% 20%, rgba(251, 207, 232, 0.45), transparent),
            radial-gradient(ellipse 60% 40% at 90% 10%, rgba(196, 181, 253, 0.4), transparent),
            radial-gradient(ellipse 70% 50% at 70% 90%, rgba(167, 243, 208, 0.35), transparent),
            radial-gradient(ellipse 50% 40% at 20% 80%, rgba(253, 230, 138, 0.4), transparent) !important;
        color: #1e293b !important;
    }
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* MODIFIKASI: Block Container Max Width 1500px */
    .block-container { 
        padding-top: 1.2rem !important; 
        max-width: 1500px !important; 
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin: 0 auto !important; 
    }
    
    label, [data-testid="stWidgetLabel"] p,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #334155 !important;
        font-weight: 500 !important;
    }
    h1, h2, h3, h4 { color: #0f172a !important; font-weight: 700 !important; }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] span { color: #0f172a !important; }
    #MainMenu, footer, header { visibility: hidden; }
    div[data-testid="stForm"] { background: transparent; border: none; padding: 0; }
    .stButton > button {
        background: #F5C842 !important;
        color: #0f172a !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        box-shadow: 0 6px 20px rgba(245, 200, 66, 0.45) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        background: #e8b83a !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06) !important;
    }
    
    /* Delete Button Customization */
    div[data-testid="column"]:has(button[title="Hapus antrian"]) .stButton > button {
        background: #fecaca !important;
        color: #991b1b !important;
        min-height: 50px !important;
    }
    /* Override Button Customization */
    div[data-testid="column"]:has(button[title="Manual Override (Prioritas Tertinggi)"]) .stButton > button {
        background: #bae6fd !important;
        color: #0369a1 !important;
        min-height: 50px !important;
    }
    /* Cancel Override Button Customization */
    div[data-testid="column"]:has(button[title="Batal Override"]) .stButton > button {
        background: #f1f5f9 !important;
        color: #64748b !important;
        min-height: 50px !important;
    }
    
    [data-testid="stAlert"] { color: #0f172a !important; }
    .cc-tag { display: inline-block !important; }
    .cc-card { display: block !important; }
    .cc-badge {
        display: inline-block; padding: 5px 14px; border-radius: 999px;
        font-size: 11px; font-weight: 700; letter-spacing: 0.03em;
    }
    .cc-badge-emergency { background: #ef4444; color: #fff; }
    .cc-badge-high { background: #f97316; color: #fff; }
    .cc-badge-medium { background: #facc15; color: #422006; }
    .cc-badge-low { background: #38bdf8; color: #fff; }
    .cc-timer-box {
        border-radius: 16px; padding: 20px; text-align: center; margin: 12px 0;
        background: linear-gradient(135deg, #6ee7b7, #bef264);
        border: 1px solid #fff; box-shadow: inset 0 2px 8px rgba(255,255,255,0.5);
    }
    .cc-urgency-box {
        border-radius: 20px; padding: 18px; margin: 12px 0;
        box-shadow: 0 8px 28px rgba(15,23,42,0.07);
    }
</style>
        """,
        unsafe_allow_html=True,
    )

inject_tailwind_theme()

# ============================================================
# PRIORITY CALCULATION ENGINE
# ============================================================

def get_base_priority(container_type, cargo_type):
    base_priorities = {
        ("Reefer 20ft", "Daging beku"): 95, ("Reefer 20ft", "Sayur buah"): 92,
        ("Reefer 20ft", "Farmasi"): 93, ("Reefer 20ft", "General"): 75,
        ("Reefer 40ft", "Daging beku"): 95, ("Reefer 40ft", "Sayur buah"): 92,
        ("Reefer 40ft", "Farmasi"): 93, ("Reefer 40ft", "General"): 75,
        ("Dry 20ft", "Food grade"): 85, ("Dry 20ft", "Jagung"): 55,
        ("Dry 20ft", "Biji sawit"): 50, ("Dry 20ft", "General"): 50,
        ("Dry 20ft", "Chemical"): 88, ("Dry 40ft", "Food grade"): 85,
        ("Dry 40ft", "Jagung"): 55, ("Dry 40ft", "Biji sawit"): 50,
        ("Dry 40ft", "General"): 50, ("Dry 40ft", "Chemical"): 88,
        ("Flat Rack 20ft", "Alat berat"): 70, ("Flat Rack 20ft", "General"): 60,
        ("Flat Rack 40ft", "Alat berat"): 70, ("Flat Rack 40ft", "General"): 60,
    }
    return base_priorities.get((container_type, cargo_type), 50)

def get_estimated_duration(container_type, dirt_level):
    durations = {
        ("Reefer 20ft", "Ringan"): 25, ("Reefer 20ft", "Sedang"): 45, ("Reefer 20ft", "Berat"): 65,
        ("Reefer 40ft", "Ringan"): 35, ("Reefer 40ft", "Sedang"): 55, ("Reefer 40ft", "Berat"): 80,
        ("Dry 20ft", "Ringan"): 12, ("Dry 20ft", "Sedang"): 20, ("Dry 20ft", "Berat"): 30,
        ("Dry 40ft", "Ringan"): 18, ("Dry 40ft", "Sedang"): 28, ("Dry 40ft", "Berat"): 40,
        ("Flat Rack 20ft", "Ringan"): 20, ("Flat Rack 20ft", "Sedang"): 35, ("Flat Rack 20ft", "Berat"): 50,
        ("Flat Rack 40ft", "Ringan"): 28, ("Flat Rack 40ft", "Sedang"): 45, ("Flat Rack 40ft", "Berat"): 65,
    }
    return durations.get((container_type, dirt_level), 25)

def get_cargo_multiplier(cargo_type):
    multipliers = {
        "Daging beku": 1.5, "Sayur buah": 1.4, "Farmasi": 1.45, "Food grade": 1.35,
        "Chemical": 1.4, "Jagung": 1.05, "Biji sawit": 1.0, "General": 1.0, "Alat berat": 1.1,
    }
    return multipliers.get(cargo_type, 1.0)

def get_dirt_multiplier(dirt_level):
    multipliers = {"Ringan": 1.0, "Sedang": 1.15, "Berat": 1.3}
    return multipliers.get(dirt_level, 1.0)

def calculate_critical_ratio(due_datetime, estimated_duration):
    now = datetime.now()
    remaining = (due_datetime - now).total_seconds() / 3600
    estimated_hours = estimated_duration / 60
    if remaining <= 0:
        return 0.1
    return remaining / estimated_hours

def get_time_factor(remaining_hours):
    if remaining_hours <= 0: return 20.0     
    elif remaining_hours < 6: return 10.0     
    elif remaining_hours < 12: return 6.0      
    elif remaining_hours < 24: return 2.5      
    elif remaining_hours < 48: return 1.3
    else: return 1.0

def calculate_priority_score(container_type, cargo_type, dirt_level, due_datetime):
    base = get_base_priority(container_type, cargo_type)
    est_duration = get_estimated_duration(container_type, dirt_level)
    cr = calculate_critical_ratio(due_datetime, est_duration)
    cargo_mult = get_cargo_multiplier(cargo_type)
    dirt_mult = get_dirt_multiplier(dirt_level)

    remaining_hours = (due_datetime - datetime.now()).total_seconds() / 3600
    time_factor = get_time_factor(remaining_hours)

    effective_cargo = cargo_mult if remaining_hours < 24 else min(cargo_mult, 1.1)
    final_score = base * time_factor * effective_cargo * dirt_mult
    
    return {
        'base_priority': base,
        'estimated_duration': est_duration,
        'critical_ratio': round(cr, 2),
        'cargo_multiplier': cargo_mult,
        'dirt_multiplier': dirt_mult,
        'time_factor': time_factor,
        'remaining_hours': round(remaining_hours, 1),
        'final_score': round(final_score, 1)
    }

def get_priority_class(final_score, critical_ratio):
    if final_score >= 200: return "EMERGENCY"
    elif final_score >= 120: return "HIGH"
    elif final_score >= 60: return "MEDIUM"
    else: return "LOW"

def get_priority_badge_html(priority_class):
    css = {
        "EMERGENCY": "cc-badge cc-badge-emergency",
        "HIGH": "cc-badge cc-badge-high",
        "MEDIUM": "cc-badge cc-badge-medium",
        "LOW": "cc-badge cc-badge-low",
    }.get(priority_class, "cc-badge cc-badge-low")
    return f'<span class="{css}">{priority_class}</span>'


def get_queue_card_variant(priority_class):
    return {
        "EMERGENCY": "rose",
        "HIGH": "amber",
        "MEDIUM": "lime",
        "LOW": "sky",
    }.get(priority_class, "sky")


def get_queue_card_border(priority_class):
    colors = {
        "EMERGENCY": "#f87171",
        "HIGH": "#fb923c",
        "MEDIUM": "#facc15",
        "LOW": "#38bdf8",
    }
    return colors.get(priority_class, "#38bdf8")


def get_cr_class(cr):
    if cr < 1:
        return "color:#dc2626;font-weight:700;"
    if cr < 2:
        return "color:#ea580c;font-weight:700;"
    if cr < 4:
        return "color:#d97706;font-weight:700;"
    return "color:#059669;font-weight:700;"


def format_time_remaining(due_datetime):
    now = datetime.now()
    diff = due_datetime - now
    if diff.total_seconds() < 0:
        hours_overdue = abs(diff.total_seconds()) // 3600
        return (
            f'<span style="color:#dc2626;font-weight:700;font-size:12px;">'
            f"TERLAMBAT {int(hours_overdue)}j</span>"
        )
    hours = diff.total_seconds() / 3600
    if hours < 4:
        return (
            f'<span style="color:#dc2626;font-weight:700;font-size:12px;">'
            f"{int(hours)}j {int((hours % 1) * 60)}m</span>"
        )
    if hours < 24:
        return (
            f'<span style="color:#ea580c;font-size:12px;font-weight:600;">'
            f"{int(hours)} jam lagi</span>"
        )
    days = hours / 24
    return (
        f'<span style="color:#64748b;font-size:12px;">{days:.1f} hari lagi</span>'
    )

def get_progress_bar_color(priority_class):
    colors = {
        "EMERGENCY": "#e53935",
        "HIGH": "#f57c00",
        "MEDIUM": "#ffca28",
        "LOW": "#5eb8e8",
    }
    return colors.get(priority_class, "#5eb8e8")


def get_cargo_options(container_type):
    return CARGO_BY_CONTAINER.get(container_type, ["General"])


def sync_cargo_on_type_change():
    options = get_cargo_options(st.session_state.input_container_type)
    if st.session_state.input_cargo_type not in options:
        st.session_state.input_cargo_type = options[0]


def get_in_progress_jobs():
    if "in_progress_slots" in st.session_state:
        return st.session_state.in_progress_slots
    if st.session_state.get("in_progress"):
        st.session_state.in_progress_slots = [st.session_state.in_progress]
        del st.session_state["in_progress"]
        return st.session_state.in_progress_slots
    return []


def count_active_cleaning():
    return len(get_in_progress_jobs())


def can_start_cleaning():
    return count_active_cleaning() < MAX_CLEANING_SLOTS


def start_cleaning_job(item, score_data):
    job = {
        "id": item["id"],
        "container_type": item["container_type"],
        "cargo_type": item["cargo_type"],
        "dirt_level": item["dirt_level"],
        "start_time": datetime.now(),
        "estimated_duration": score_data["estimated_duration"],
        "due_datetime": item["due_datetime"],
        "ro_info": item["ro_info"],
    }
    st.session_state.in_progress_slots = get_in_progress_jobs() + [job]
    st.session_state.queue = [q for q in st.session_state.queue if q["id"] != item["id"]]


def finish_cleaning_job(slot_index):
    jobs = get_in_progress_jobs()
    if 0 <= slot_index < len(jobs):
        jobs.pop(slot_index)
        st.session_state.in_progress_slots = jobs
    st.session_state.completed_today += 1


def render_live_clock():
    html_code = """
    <div style="text-align: right; font-family: 'Inter', sans-serif; padding: 5px 15px;">
        <div id="live-time" style="font-size:28px;font-weight:800;color:#0f172a;">--:--:--</div>
        <div id="live-date" style="font-size:13px;color:#64748b;margin-top:6px;">Memuat...</div>
    </div>
    <script>
        function tick() {
            const n = new Date();
            document.getElementById('live-time').textContent =
                n.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            document.getElementById('live-date').textContent =
                n.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' });
        }
        tick();
        setInterval(tick, 1000);
    </script>
    """
    st.markdown(cc_card(variant="clock", open_tag_extra="padding:0;overflow:hidden;"), unsafe_allow_html=True)
    components.html(html_code, height=90)
    st.markdown(cc_card_close(), unsafe_allow_html=True)


def render_urgency_preview(score_data, priority_class):
    bar_color = get_progress_bar_color(priority_class)
    score_pct = min(100, score_data["final_score"] / 2)
    variant = get_queue_card_variant(priority_class)
    border = get_queue_card_border(priority_class)
    st.markdown(
        f"""
        {cc_card(variant=variant, open_tag_extra=f"border-left:5px solid {border};")}
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <span style="font-size:14px;font-weight:600;color:#475569;">Tingkat Urgensi (live)</span>
                {get_priority_badge_html(priority_class)}
            </div>
            <div style="height:1px;background:#e2e8f0;margin:14px 0;"></div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:13px;color:#64748b;">Estimasi Durasi</span>
                <span style="font-size:18px;font-weight:800;color:#0f172a;">
                    {score_data["estimated_duration"]} mnt
                </span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;">
                {pastel_tag(f"Base {score_data['base_priority']}", "slate")}
                {pastel_tag(f"Cargo ×{score_data['cargo_multiplier']}", "amber")}
                {pastel_tag(f"Dirt ×{score_data['dirt_multiplier']}", "lime")}
                {pastel_tag(f"CR {score_data['critical_ratio']}x", "sky")}
            </div>
            {progress_bar_html(score_pct, bar_color, "Skor urgensi", f"{score_data['final_score']} pts", 12)}
            {progress_bar_html(min(100, score_data["remaining_hours"] / 48 * 100), "#22c55e" if score_data["remaining_hours"] >= 12 else "#f59e0b", "Sisa waktu due", f"{score_data['remaining_hours']} jam", 10)}
        {cc_card_close()}
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    if 'queue' not in st.session_state:
        now = datetime.now()
        st.session_state.queue = [
            {'id': 'SPNU 468208', 'container_type': 'Reefer 20ft', 'cargo_type': 'Daging beku', 'dirt_level': 'Sedang', 'due_datetime': now + timedelta(hours=3), 'ro_info': 'RO hari H', 'added_at': now - timedelta(hours=1), 'is_overriden': False},
            {'id': 'SPNU 391047', 'container_type': 'Dry 40ft', 'cargo_type': 'Jagung', 'dirt_level': 'Ringan', 'due_datetime': now + timedelta(hours=8), 'ro_info': 'RO hari H', 'added_at': now - timedelta(hours=2), 'is_overriden': False},
            {'id': 'SPNU 283122', 'container_type': 'Dry 20ft', 'cargo_type': 'Biji sawit', 'dirt_level': 'Ringan', 'due_datetime': now + timedelta(hours=48), 'ro_info': '', 'added_at': now - timedelta(hours=3), 'is_overriden': False},
            {'id': 'SPNU 482019', 'container_type': 'Flat Rack 40ft', 'cargo_type': 'Alat berat', 'dirt_level': 'Berat', 'due_datetime': now + timedelta(hours=12), 'ro_info': '', 'added_at': now - timedelta(minutes=30), 'is_overriden': False},
        ]
    if "in_progress_slots" not in st.session_state:
        now = datetime.now()
        start_time = now - timedelta(minutes=23, seconds=15)
        job1 = {
            "id": "SPNU 468208",
            "container_type": "Reefer 20ft",
            "cargo_type": "Daging beku",
            "dirt_level": "Sedang",
            "start_time": start_time,
            "estimated_duration": 50,
            "due_datetime": now + timedelta(hours=3),
            "ro_info": "RO hari H",
        }
        start_time2 = now - timedelta(minutes=8)
        job2 = {
            "id": "SPNU 391047",
            "container_type": "Dry 40ft",
            "cargo_type": "Jagung",
            "dirt_level": "Ringan",
            "start_time": start_time2,
            "estimated_duration": 28,
            "due_datetime": now + timedelta(hours=8),
            "ro_info": "RO hari H",
        }
        st.session_state.in_progress_slots = [job1, job2]
        st.session_state.queue = [
            q
            for q in st.session_state.queue
            if q["id"] not in ("SPNU 468208", "SPNU 391047")
        ]
    if 'completed_today' not in st.session_state:
        st.session_state.completed_today = 12
    if 'available' not in st.session_state:
        st.session_state.available = 34
    if 'queue_filter' not in st.session_state:
        st.session_state.queue_filter = "ALL"
    if 'success_toast' not in st.session_state:
        st.session_state.success_toast = ""
    if 'input_container_type' not in st.session_state:
        st.session_state.input_container_type = "Reefer 20ft"
    if 'input_cargo_type' not in st.session_state:
        st.session_state.input_cargo_type = "Daging beku"
    if 'input_dirt_level' not in st.session_state:
        st.session_state.input_dirt_level = "Sedang"
        
    if 'input_due_date' not in st.session_state:
        st.session_state.input_due_date = datetime.now().date()
    if 'input_due_time' not in st.session_state:
        st.session_state.input_due_time = (datetime.now() + timedelta(hours=8)).time().replace(second=0, microsecond=0)

# ============================================================
# RENDER FUNCTIONS
# ============================================================

def render_stat_card(label, value, icon, bubble_key="mint"):
    st.markdown(
        f"""
        {cc_card(variant=bubble_key)}
            <div style="text-align:center;padding:8px 0;">
                <div style="font-size:32px;font-weight:800;color:#0f172a;">{value}</div>
                <div style="font-size:12px;color:#64748b;margin-top:8px;font-weight:600;">{icon} {label}</div>
            </div>
        {cc_card_close()}
        """,
        unsafe_allow_html=True,
    )

def render_queue_item(item, score_data):
    priority_class = get_priority_class(
        score_data["final_score"], score_data["critical_ratio"]
    )
    variant = get_queue_card_variant(priority_class)
    border = get_queue_card_border(priority_class)
    badge_html = get_priority_badge_html(priority_class)
    cr_class = get_cr_class(score_data["critical_ratio"])
    due_html = format_time_remaining(item["due_datetime"])
    bar_color = get_progress_bar_color(priority_class)
    score_pct = min(100, score_data["final_score"] / 2)
    tags = [
        pastel_tag(item["container_type"], "violet"),
        pastel_tag(item["cargo_type"], "slate"),
        pastel_tag(f"~{score_data['estimated_duration']} mnt", "sky"),
    ]
    if item["cargo_type"] in ["Daging beku", "Sayur buah", "Farmasi", "Food grade"]:
        tags.append(pastel_tag("Food grade", "food"))
    if item["ro_info"]:
        tags.append(pastel_tag(item["ro_info"], "amber"))
    tags_html = "".join(tags)
    html = (
        f'{cc_card(variant=variant, open_tag_extra=f"border-left:5px solid {border};")}'
        f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;">'
        f'<span style="font-weight:800;font-size:15px;color:#0f172a;">{item["id"]}</span>'
        f"{badge_html}</div>"
        f'<div style="margin-top:10px;line-height:1.8;">{tags_html}</div>'
        f'<div style="margin-top:10px;font-size:12px;color:#64748b;display:flex;flex-wrap:wrap;gap:14px;">'
        f'<span>Score: <strong style="color:#0f172a;">{score_data["final_score"]}</strong></span>'
        f'<span>CR: <span style="{cr_class}">{score_data["critical_ratio"]}x</span></span>'
        f"<span>{due_html}</span></div>"
        f'{progress_bar_html(score_pct, bar_color, "Tingkat urgensi", priority_class, 11)}'
        f"{due_time_bar_html(item['due_datetime'])}"
        f"{cc_card_close()}"
    )
    st.markdown(html, unsafe_allow_html=True)


def build_job_timer_html(job, slot_idx=0):
    now = datetime.now()
    elapsed = (now - job["start_time"]).total_seconds()
    estimated = job["estimated_duration"] * 60
    remaining = max(0, estimated - elapsed)
    mins, secs = divmod(int(remaining), 60)
    hours, mins = divmod(mins, 60)
    time_display = (
        f"{hours:02d}:{mins:02d}:{secs:02d}"
        if hours > 0
        else f"{mins:02d}:{secs:02d}"
    )
    progress_pct = min(100, (elapsed / estimated) * 100) if estimated > 0 else 100
    score = calculate_priority_score(
        job["container_type"],
        job["cargo_type"],
        job["dirt_level"],
        job["due_datetime"],
    )
    priority_class = get_priority_class(
        score["final_score"], score["critical_ratio"]
    )
    badge_html = get_priority_badge_html(priority_class)
    variant = "violet" if slot_idx == 0 else "lime"
    tags = [
        pastel_tag(job["container_type"], "violet"),
        pastel_tag(job["cargo_type"], "slate"),
        pastel_tag(job["dirt_level"], "lime"),
        pastel_tag(f"Est. {job['estimated_duration']} mnt", "sky"),
    ]
    if job["cargo_type"] in ["Daging beku", "Sayur buah", "Farmasi", "Food grade"]:
        tags.append(pastel_tag("Food grade", "food"))
    if job["ro_info"]:
        tags.append(pastel_tag(job["ro_info"], "amber"))
    tags_html = "".join(tags)
    work_bar = progress_bar_html(
        progress_pct, "#22c55e", "Progress cleaning", f"{int(progress_pct)}%", 12
    )
    due_bar = due_time_bar_html(job["due_datetime"])
    return (
        f"{cc_card(variant=variant)}"
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        f'<span style="font-weight:800;font-size:17px;color:#0f172a;">{job["id"]}</span>'
        f"{badge_html}</div>"
        f'<div style="line-height:1.9;margin-bottom:8px;">{tags_html}</div>'
        f'<div class="cc-timer-box">'
        f'<div style="font-size:32px;font-weight:800;font-family:monospace;color:#0f172a;">{time_display}</div>'
        f'<div style="font-size:12px;color:#334155;margin-top:6px;font-weight:600;">sisa estimasi cleaning</div></div>'
        f"{work_bar}{due_bar}{cc_card_close()}"
    )


@st.fragment(run_every=1)
def render_slot_timer_html(slot_idx):
    jobs = get_in_progress_jobs()
    if slot_idx < len(jobs):
        st.markdown(
            build_job_timer_html(jobs[slot_idx], slot_idx), unsafe_allow_html=True
        )


def render_cleaning_panel():
    jobs = get_in_progress_jobs()
    slot_cols = st.columns(2)

    for slot_idx in range(MAX_CLEANING_SLOTS):
        with slot_cols[slot_idx]:
            slot_colors = ["violet", "mint"]
            st.markdown(
                f'<p style="font-weight:700;font-size:14px;color:#0f172a;margin-bottom:10px;">'
                f"🧹 Slot Cleaning {slot_idx + 1}</p>",
                unsafe_allow_html=True,
            )
            if slot_idx < len(jobs):
                render_slot_timer_html(slot_idx)
                st.number_input(
                    "Durasi Aktual (menit)",
                    min_value=1,
                    max_value=200,
                    value=jobs[slot_idx]["estimated_duration"],
                    step=1,
                    key=f"actual_duration_{slot_idx}",
                )
                st.text_area(
                    "Catatan",
                    placeholder="Catatan cleaning...",
                    height=50,
                    key=f"cleaning_notes_{slot_idx}",
                )
                if st.button(
                    "Selesai",
                    type="primary",
                    use_container_width=True,
                    key=f"finish_{slot_idx}",
                ):
                    finished_id = jobs[slot_idx]["id"]
                    finish_cleaning_job(slot_idx)
                    st.session_state.success_toast = f"{finished_id} selesai dicatat!"
                    st.rerun()
            else:
                st.markdown(
                    f"""
                    {cc_card(variant=slot_colors[slot_idx], open_tag_extra="border:2px dashed #cbd5e1;text-align:center;")}
                        <div style="font-size:40px;margin-bottom:8px;">➕</div>
                        <div style="color:#64748b;font-size:14px;font-weight:600;">Slot kosong</div>
                    {cc_card_close()}
                    """,
                    unsafe_allow_html=True,
                )
                if (
                    slot_idx == len(jobs)
                    and st.session_state.queue
                    and can_start_cleaning()
                ):
                    scored_queue = []
                    for item in st.session_state.queue:
                        score = calculate_priority_score(
                            item["container_type"],
                            item["cargo_type"],
                            item["dirt_level"],
                            item["due_datetime"],
                        )
                        scored_queue.append((item, score))
                    
                    scored_queue.sort(
                        key=lambda x: (x[0].get("is_overriden", False), x[1]["final_score"]), 
                        reverse=True
                    )
                    
                    next_item, next_score = scored_queue[0]
                    if st.button(
                        "Mulai di slot ini",
                        type="primary",
                        use_container_width=True,
                        key=f"start_slot_{slot_idx}",
                    ):
                        start_cleaning_job(next_item, next_score)
                        st.session_state.success_toast = (
                            f"Mulai {next_item['id']} di slot {slot_idx + 1}!"
                        )
                        st.rerun()

    if not jobs and not st.session_state.queue:
        st.markdown(
            """
            <div class="text-center py-6 text-slate-500 text-sm font-medium">
                Tidak ada cleaning aktif — tambah kontainer ke antrian dulu.
            </div>
            """,
            unsafe_allow_html=True,
        )

# PERBAIKAN KEY DI MODAL DIALOG
@st.dialog("Daftar Lengkap Antrian Cleaning", width="large")
def show_all_queue_dialog(scored_queue):
    for i, (item, score) in enumerate(scored_queue):
        if item.get("is_overriden"):
            st.markdown(pastel_tag("⚠️ OVERRIDDEN", "rose"), unsafe_allow_html=True)
            
        col_item, col_del, col_up = st.columns([0.76, 0.12, 0.12], vertical_alignment="center")
        with col_item:
            render_queue_item(item, score)
        with col_del:
            # Tambahkan index 'i' agar key unik meskipun ada ID "SPNU " yang sama
            if st.button("🗑️ Hapus", key=f"modal_del_{i}_{item['id']}", help="Hapus antrian"):
                st.session_state.queue.remove(item)
                st.rerun()
        with col_up:
            if item.get("is_overriden"):
                if st.button("⬇️ Batal", key=f"modal_down_{i}_{item['id']}", help="Batal Override"):
                    for q in st.session_state.queue:
                        if q['id'] == item['id']:
                            q['is_overriden'] = False
                            break
                    st.rerun()
            else:
                if st.button("⬆️ Naik", key=f"modal_up_{i}_{item['id']}", help="Manual Override (Prioritas Tertinggi)"):
                    for q in st.session_state.queue:
                        if q['id'] == item['id']:
                            q['is_overriden'] = True
                            break
                    st.rerun()

@st.fragment(run_every=5)
def render_queue_list_fragment():
    if not st.session_state.queue:
        return
    scored_queue = []
    for item in st.session_state.queue:
        score = calculate_priority_score(
            item["container_type"],
            item["cargo_type"],
            item["dirt_level"],
            item["due_datetime"],
        )
        scored_queue.append((item, score))
        
    scored_queue.sort(
        key=lambda x: (x[0].get("is_overriden", False), x[1]["final_score"]), 
        reverse=True
    )
    
    filter_mode = st.session_state.get("queue_filter", "ALL")
    filtered_queue = []
    for item, score in scored_queue:
        priority_class = get_priority_class(
            score["final_score"], score["critical_ratio"]
        )
        if filter_mode == "URGENT" and priority_class not in ["EMERGENCY", "HIGH"]:
            continue
        if filter_mode == "NORMAL" and priority_class not in ["MEDIUM", "LOW"]:
            continue
        filtered_queue.append((item, score))

    displayed = 0
    MAX_DISPLAY = 3

    for i, (item, score) in enumerate(filtered_queue[:MAX_DISPLAY]):
        col_item, col_del, col_up = st.columns(
            [0.76, 0.12, 0.12], vertical_alignment="center", gap="small"
        )
        
        with col_item:
            if item.get("is_overriden"):
                st.markdown(pastel_tag("⚠️ OVERRIDDEN", "rose"), unsafe_allow_html=True)
            render_queue_item(item, score)
            
        with col_del:
            if st.button("🗑️", key=f"del_{i}_{item['id']}", help="Hapus antrian"):
                st.session_state.queue.remove(item)
                st.session_state.success_toast = "Antrian berhasil dihapus!"
                st.rerun()
                
        with col_up:
            if item.get("is_overriden"):
                if st.button("⬇️", key=f"down_{i}_{item['id']}", help="Batal Override"):
                    for q in st.session_state.queue:
                        if q['id'] == item['id']:
                            q['is_overriden'] = False
                            break
                    st.session_state.success_toast = f"Override {item['id']} dibatalkan!"
                    st.rerun()
            else:
                if st.button("⬆️", key=f"up_{i}_{item['id']}", help="Manual Override (Prioritas Tertinggi)"):
                    for q in st.session_state.queue:
                        if q['id'] == item['id']:
                            q['is_overriden'] = True
                            break
                    st.session_state.success_toast = f"{item['id']} berhasil dinaikkan prioritasnya!"
                    st.rerun()
                    
        displayed += 1

    if len(filtered_queue) > MAX_DISPLAY:
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        if st.button(f"Lihat Semua Antrian ({len(filtered_queue)} kontainer) ➡️", use_container_width=True):
            show_all_queue_dialog(filtered_queue)

    if displayed == 0:
        st.info("Tidak ada kontainer yang sesuai filter.")


def render_queue_panel():
    c1, c2, c3 = st.columns(3)
    with c1:
        render_stat_card("Selesai", st.session_state.completed_today, "✅", "rose")
    with c2:
        render_stat_card("Siap Pakai", st.session_state.available, "📦", "sky")
    with c3:
        queue_count = len(st.session_state.queue) + count_active_cleaning()
        render_stat_card("Antrian", queue_count, "⏳", "amber")
    st.markdown('<div class="h-px bg-amber-200/80 my-4"></div>', unsafe_allow_html=True)
    st.markdown(
        '<h4 class="text-slate-900 font-bold mb-3 text-lg">📋 Antrian Cleaning</h4>',
        unsafe_allow_html=True,
    )
    for i, job in enumerate(get_in_progress_jobs()):
        elapsed = (datetime.now() - job["start_time"]).total_seconds()
        progress_pct = (
            min(100, (elapsed / (job["estimated_duration"] * 60)) * 100)
            if job["estimated_duration"] > 0
            else 100
        )
        chip = "violet" if i == 0 else "lime"
        active_html = (
            f'{cc_card(variant=chip)}'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.06em;'
            f'color:#64748b;font-weight:700;">Sedang dikerjakan</div>'
            f'<div style="font-weight:800;font-size:15px;color:#0f172a;margin:6px 0;">{job["id"]}</div>'
            f'<div style="font-size:12px;color:#475569;margin-bottom:8px;">'
            f'{pastel_tag(job["container_type"], "violet")}{pastel_tag(job["cargo_type"], "slate")}</div>'
            f'{progress_bar_html(progress_pct, "#22c55e", "Progress", f"{int(progress_pct)}%", 10)}'
            f"{cc_card_close()}"
        )
        st.markdown(active_html, unsafe_allow_html=True)
    if st.session_state.queue:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            if st.button("Semua", key="btn_all", use_container_width=True):
                st.session_state.queue_filter = "ALL"
        with col_f2:
            if st.button("Urgent", key="btn_urgent", use_container_width=True):
                st.session_state.queue_filter = "URGENT"
        with col_f3:
            if st.button("Normal", key="btn_normal", use_container_width=True):
                st.session_state.queue_filter = "NORMAL"
        render_queue_list_fragment()
    else:
        st.markdown(
            """
            <div class="text-center py-8 text-slate-500">
                <div class="text-4xl mb-2">📭</div>
                <div class="text-sm font-medium">Antrian kosong</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MAIN APP
# ============================================================

def main():
    init_session_state()
    
    if st.session_state.success_toast:
        st.toast(st.session_state.success_toast, icon="✅")
        st.session_state.success_toast = ""
        
    header_left, header_right = st.columns([2.2, 1])
    with header_left:
        st.markdown(
            f"""
            {cc_card(variant="hero")}
                <h1 style="font-size:clamp(32px,4vw,42px);font-weight:800;color:#0f172a;margin:0;line-height:1.15;">
                    CleanCycle<br/>
                    <span style="color:#059669;font-size:clamp(22px,3vw,32px);">Container Cleaning Dashboard</span>
                </h1>
                <p style="color:#64748b;font-size:15px;margin:18px 0 22px;max-width:520px;line-height:1.6;">
                    Smart Priority Queue — Critical Ratio Algorithm untuk operasional depo kontainer.
                </p>
                <span style="display:inline-block;padding:12px 28px;border-radius:999px;
                    background:#F5C842;color:#0f172a;font-weight:700;font-size:14px;
                    box-shadow:0 6px 20px rgba(245,200,66,0.45);">Dashboard Operasional →</span>
            {cc_card_close()}
            """,
            unsafe_allow_html=True,
        )
    with header_right:
        render_live_clock()
    
    col1, col2, col3 = st.columns([1.1, 1.1, 1.0])
    
    with col1:
        panel_header("Input Data Cleaning", "📝", "rose")
        panel_body_open("rose")

        container_type = st.selectbox(
            "Tipe Kontainer",
            CONTAINER_TYPES,
            key="input_container_type",
            on_change=sync_cargo_on_type_change,
        )
        cargo_options = get_cargo_options(container_type)
        cargo_type = st.selectbox(
            "Jenis Muatan",
            cargo_options,
            key="input_cargo_type",
        )

        if cargo_type in ["Daging beku", "Sayur buah", "Farmasi", "Food grade"]:
            st.markdown(
                """
                <div style="border-radius:16px;background:#ecfdf5;border:1px solid #6ee7b7;
                    color:#065f46;font-size:13px;padding:14px;margin:10px 0;font-weight:500;">
                    Kontainer <strong style="color:#047857;">food grade</strong>
                    — prioritas otomatis ditingkatkan
                </div>
                """,
                unsafe_allow_html=True,
            )

        dirt_level = st.select_slider(
            "Tingkat Kekotoran",
            options=["Ringan", "Sedang", "Berat"],
            key="input_dirt_level",
        )

        col_due1, col_due2 = st.columns(2)
        with col_due1:
            due_date = st.date_input("Tanggal Due", key="input_due_date") 
        with col_due2:
            due_time = st.time_input("Jam Due", key="input_due_time")
            
        due_datetime = datetime.combine(due_date, due_time)

        score_data = calculate_priority_score(
            container_type, cargo_type, dirt_level, due_datetime
        )
        priority_class = get_priority_class(
            score_data["final_score"], score_data["critical_ratio"]
        )
        render_urgency_preview(score_data, priority_class)

        with st.form("input_form", border=False):
            container_id = st.text_input(
                "No. Kontainer", value="SPNU ", placeholder="SPNU XXXXXX"
            )
            ro_info = st.text_input("Info RO (opsional)", placeholder="Contoh: RO hari H")
            submitted = st.form_submit_button(
                "Tambah ke Antrian", use_container_width=True, type="primary"
            )

            if submitted:
                new_item = {
                    "id": container_id,
                    "container_type": container_type,
                    "cargo_type": cargo_type,
                    "dirt_level": dirt_level,
                    "due_datetime": due_datetime,
                    "ro_info": ro_info,
                    "added_at": datetime.now(),
                    "is_overriden": False
                }
                st.session_state.queue.append(new_item)
                st.session_state.success_toast = f"{container_id} ditambahkan ke antrian!"
                st.rerun()
        
        panel_body_close()
    
    with col2:
        panel_header("Cleaning Berlangsung (2 Slot)", "⏱️", "violet")
        panel_body_open("violet")
        render_cleaning_panel()
        panel_body_close()
    
    with col3:
        panel_header("Status Depo Hari Ini", "📊", "amber")
        panel_body_open("amber")
        render_queue_panel()
        panel_body_close()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1.2, 1.0])
    
    with col_a:
        panel_header("Distribusi Prioritas Antrian", "📈", "sky")
        panel_body_open("sky")
        
        if st.session_state.queue:
            counts = {"EMERGENCY": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for item in st.session_state.queue:
                score = calculate_priority_score(item['container_type'], item['cargo_type'], item['dirt_level'], item['due_datetime'])
                pc = get_priority_class(score['final_score'], score['critical_ratio'])
                counts[pc] = counts.get(pc, 0) + 1
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['Emergency', 'High', 'Medium', 'Low'],
                    y=[counts['EMERGENCY'], counts['HIGH'], counts['MEDIUM'], counts['LOW']],
                    marker_color=['#e53935', '#f57c00', '#ffca28', '#5eb8e8'],
                    text=[counts['EMERGENCY'], counts['HIGH'], counts['MEDIUM'], counts['LOW']],
                    textposition='auto',
                    textfont=dict(color='white', size=14),
                )
            ])

            fig.update_layout(
                font=dict(color="#334155", size=13, family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.6)",
                xaxis=dict(
                    title=dict(text="Priority Class", font=dict(color="#475569", size=14)),
                    tickfont=dict(color="#64748b", size=12),
                    gridcolor="rgba(148,163,184,0.25)",
                ),
                yaxis=dict(
                    title=dict(text="Jumlah Kontainer", font=dict(color="#475569", size=14)),
                    tickfont=dict(color="#64748b", size=12),
                    gridcolor="rgba(148,163,184,0.25)",
                ),
                showlegend=False,
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data antrian untuk divisualisasikan.")
        
        panel_body_close()
    
    with col_b:
        panel_header("Metode Critical Ratio", "🧮", "mint")
        panel_body_open("mint")
        st.markdown(
            f"""
            {cc_card(variant="lime")}
                <p style="font-size:14px;line-height:1.6;color:#334155;">
                <strong style="color:#0f172a;font-size:15px;">Formula Priority Score</strong></p>
                <div style="border-radius:16px;background:#fff;border:1px solid #bef264;
                    padding:14px;margin:14px 0;font-family:monospace;font-size:12px;
                    color:#047857;font-weight:600;">
                    Score = Base × TimeFactor × Cargo × Dirt
                </div>
                <p><strong class="text-slate-800">Dimana:</strong></p>
                <ul style="padding-left:20px;margin:12px 0;color:#64748b;font-size:13px;line-height:1.7;">
                    <li><strong style="color:#0f172a;">Base</strong>: Prioritas dasar (50-95)</li>
                    <li><strong style="color:#0f172a;">CR</strong>: Sisa waktu / durasi estimasi</li>
                    <li><strong style="color:#0f172a;">Cargo</strong>: Multiplier 1.0-1.5</li>
                    <li><strong style="color:#0f172a;">Dirt</strong>: Multiplier 1.0-1.3</li>
                </ul>
                <div style="height:1px;background:#d9f99d;margin:20px 0;"></div>
                <p><strong style="color:#0f172a;">Kategori Prioritas</strong></p>
                <table style="width:100%;font-size:12px;margin-top:12px;color:#64748b;">
                    <tr><td>"""
            + get_priority_badge_html("EMERGENCY")
            + """</td><td class="text-right">Score &gt;= 200</td></tr>
                    <tr><td class="py-1">"""
            + get_priority_badge_html("HIGH")
            + """</td><td class="text-right py-1">Score &gt;= 120</td></tr>
                    <tr><td>"""
            + get_priority_badge_html("MEDIUM")
            + """</td><td class="text-right">Score &gt;= 60</td></tr>
                    <tr><td>"""
            + get_priority_badge_html("LOW")
            + """</td><td class="text-right">Score &lt; 60</td></tr>
                </table>
            {cc_card_close()}
            """,
            unsafe_allow_html=True,
        )
        
        panel_body_close()

if __name__ == "__main__":
    main()