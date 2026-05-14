import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Container Cleaning Dashboard",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa !important;
        color: #333333 !important;
    }
    h1, h2, h3, h4 {
        color: #1a1a1a !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .panel-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 15px 15px 0 0;
        font-weight: bold;
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .panel-body {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 0 0 15px 15px;
        border: 1px solid #e0e0e0;
        border-top: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    .card:hover {
        border-color: #4caf50;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76,175,80,0.15);
    }
    .badge-emergency {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #c62828, #e53935);
        color: white;
    }
    .badge-high {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #e65100, #ff6d00);
        color: white;
    }
    .badge-medium {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #f9a825, #ffca28);
        color: #333;
    }
    .badge-low {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: linear-gradient(135deg, #2e7d32, #4caf50);
        color: white;
    }
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        margin: 2px 4px 2px 0;
    }
    .tag-food {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    .tag-type {
        background-color: #f3e5f5;
        color: #6a1b9a;
    }
    .tag-time {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .tag-ro {
        background-color: #fff3e0;
        color: #e65100;
    }
    .timer-display {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 15px 0;
    }
    .timer-value {
        font-size: 42px;
        font-weight: bold;
        color: white;
        font-family: 'Courier New', monospace;
    }
    .timer-label {
        font-size: 13px;
        color: #a5d6a7;
        margin-top: 5px;
    }
    .stat-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e8e8e8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #1b5e20;
    }
    .stat-label {
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }
    .divider {
        height: 1px;
        background-color: #e0e0e0;
        margin: 15px 0;
    }
    .queue-item {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 4px solid #4caf50;
        border: 1px solid #e8e8e8;
        border-left-width: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .queue-item-emergency { border-left-color: #e53935; }
    .queue-item-high { border-left-color: #ff6d00; }
    .queue-item-medium { border-left-color: #ffca28; }
    .queue-item-low { border-left-color: #4caf50; }
    .progress-bar {
        width: 100%;
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 8px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .container-id {
        font-weight: bold;
        font-size: 15px;
        color: #1a1a1a;
    }
    .container-details {
        font-size: 12px;
        color: #666;
        margin-top: 4px;
    }
    
    /* Tombol Utama Streamlit */
    .stButton > button {
        background-color: #2e7d32 !important;
        color: #ffffff !important;
        border: 1px solid #4caf50 !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #1b5e20 !important;
        color: #ffffff !important;
        border-color: #66bb6a !important;
    }

    .cr-critical { color: #e53935; font-weight: bold; }
    .cr-high { color: #ff6d00; font-weight: bold; }
    .cr-medium { color: #ffca28; font-weight: bold; }
    .cr-low { color: #4caf50; font-weight: bold; }
    .due-soon { color: #e53935; font-weight: bold; font-size: 12px; }
    .due-warning { color: #ffca28; font-size: 12px; }
    .due-normal { color: #aaa; font-size: 12px; }
    .info-banner {
        background-color: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0;
        color: #2e7d32;
        font-size: 13px;
    }

    /* Tombol Hapus Antrian - Merah Terang */
    div[data-testid="column"]:has(button[title="Hapus antrian"]) .stButton > button {
        background-color: #e53935 !important;
        color: #ffffff !important;
        border: 1px solid #c62828 !important;
        height: 100% !important;
        min-height: 110px !important;
        width: 100% !important;
        border-radius: 12px !important;
        margin-top: 0 !important;
    }
    div[data-testid="column"]:has(button[title="Hapus antrian"]) .stButton > button:hover {
        background-color: #c62828 !important;
        color: #ffffff !important;
        border-color: #b71c1c !important;
    }
</style>
""", unsafe_allow_html=True)

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
    badges = {
        "EMERGENCY": '<span class="badge-emergency">EMERGENCY</span>',
        "HIGH": '<span class="badge-high">HIGH</span>',
        "MEDIUM": '<span class="badge-medium">MEDIUM</span>',
        "LOW": '<span class="badge-low">LOW</span>',
    }
    return badges.get(priority_class, badges["LOW"])

def get_queue_border_class(priority_class):
    classes = {
        "EMERGENCY": "queue-item queue-item-emergency",
        "HIGH": "queue-item queue-item-high",
        "MEDIUM": "queue-item queue-item-medium",
        "LOW": "queue-item queue-item-low",
    }
    return classes.get(priority_class, "queue-item")

def get_cr_class(cr):
    if cr < 1: return "cr-critical"
    elif cr < 2: return "cr-high"
    elif cr < 4: return "cr-medium"
    return "cr-low"

def format_time_remaining(due_datetime):
    now = datetime.now()
    diff = due_datetime - now
    if diff.total_seconds() < 0:
        hours_overdue = abs(diff.total_seconds()) // 3600
        return f'<span class="due-soon">TERLAMBAT {int(hours_overdue)}j</span>'
    hours = diff.total_seconds() / 3600
    if hours < 4:
        return f'<span class="due-soon">{int(hours)}j {int((hours % 1) * 60)}m</span>'
    elif hours < 24:
        return f'<span class="due-warning">{int(hours)} jam lagi</span>'
    else:
        days = hours / 24
        return f'<span class="due-normal">{days:.1f} hari lagi</span>'

def get_progress_bar_color(priority_class):
    colors = {
        "EMERGENCY": "#e53935",
        "HIGH": "#ff6d00",
        "MEDIUM": "#ffca28",
        "LOW": "#4caf50",
    }
    return colors.get(priority_class, "#4caf50")

# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    if 'queue' not in st.session_state:
        now = datetime.now()
        st.session_state.queue = [
            {'id': 'SPNU 468208', 'container_type': 'Reefer 20ft', 'cargo_type': 'Daging beku', 'dirt_level': 'Sedang', 'due_datetime': now + timedelta(hours=3), 'ro_info': 'RO hari H', 'added_at': now - timedelta(hours=1)},
            {'id': 'SPNU 391047', 'container_type': 'Dry 40ft', 'cargo_type': 'Jagung', 'dirt_level': 'Ringan', 'due_datetime': now + timedelta(hours=8), 'ro_info': 'RO hari H', 'added_at': now - timedelta(hours=2)},
            {'id': 'SPNU 283122', 'container_type': 'Dry 20ft', 'cargo_type': 'Biji sawit', 'dirt_level': 'Ringan', 'due_datetime': now + timedelta(hours=48), 'ro_info': '', 'added_at': now - timedelta(hours=3)},
            {'id': 'SPNU 482019', 'container_type': 'Flat Rack 40ft', 'cargo_type': 'Alat berat', 'dirt_level': 'Berat', 'due_datetime': now + timedelta(hours=12), 'ro_info': '', 'added_at': now - timedelta(minutes=30)},
        ]
    if 'in_progress' not in st.session_state:
        now = datetime.now()
        start_time = now - timedelta(minutes=23, seconds=15)
        st.session_state.in_progress = {
            'id': 'SPNU 468208', 'container_type': 'Reefer 20ft', 'cargo_type': 'Daging beku', 'dirt_level': 'Sedang',
            'start_time': start_time, 'estimated_duration': 50, 'due_datetime': now + timedelta(hours=3), 'ro_info': 'RO hari H',
        }
        st.session_state.queue = [q for q in st.session_state.queue if q['id'] != 'SPNU 468208']
    if 'completed_today' not in st.session_state:
        st.session_state.completed_today = 12
    if 'available' not in st.session_state:
        st.session_state.available = 34
    if 'queue_filter' not in st.session_state:
        st.session_state.queue_filter = "ALL"
    if 'success_toast' not in st.session_state:
        st.session_state.success_toast = ""

# ============================================================
# RENDER FUNCTIONS
# ============================================================

def render_stat_card(label, value, icon):
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{value}</div>
        <div class="stat-label">{icon} {label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_queue_item(item, score_data):
    priority_class = get_priority_class(score_data['final_score'], score_data['critical_ratio'])
    border_class = get_queue_border_class(priority_class)
    badge_html = get_priority_badge_html(priority_class)
    cr_class = get_cr_class(score_data['critical_ratio'])
    due_html = format_time_remaining(item['due_datetime'])
    bar_color = get_progress_bar_color(priority_class)
    progress_width = min(100, score_data['final_score'] / 2)
    
    food_grade_tags = ""
    if item['cargo_type'] in ['Daging beku', 'Sayur buah', 'Farmasi', 'Food grade']:
        food_grade_tags = '<span class="tag tag-food">Food grade</span>'
    
    ro_tag = ""
    if item['ro_info']:
        ro_tag = f'<span class="tag tag-ro">{item["ro_info"]}</span>'
    
    # HTML ditulis dalam satu baris untuk menghindari bug Code Block di Streamlit
    html = f'<div class="{border_class}"><div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="flex: 1;"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><span class="container-id">{item["id"]}</span>{badge_html}</div><div style="margin-top: 6px;"><span class="tag tag-type">{item["container_type"]}</span><span class="tag">{item["cargo_type"]}</span>{food_grade_tags}<span class="tag tag-time">~{score_data["estimated_duration"]} mnt</span>{ro_tag}</div><div style="margin-top: 8px; display: flex; align-items: center; gap: 15px;"><span style="font-size: 12px; color: #666;">Score: <strong style="color: #1a1a1a;">{score_data["final_score"]}</strong></span><span style="font-size: 12px; color: #666;">CR: <span class="{cr_class}">{score_data["critical_ratio"]}x</span></span>{due_html}</div><div class="progress-bar"><div class="progress-fill" style="width: {progress_width}%; background: {bar_color};"></div></div></div></div></div>'
    
    st.markdown(html, unsafe_allow_html=True)

# ============================================================
# MAIN APP
# ============================================================

def main():
    init_session_state()
    
    # Munculkan toast jika ada flag dari rerun sebelumnya
    if st.session_state.success_toast:
        st.toast(st.session_state.success_toast, icon="✅")
        st.session_state.success_toast = ""
        
    # Header
    now = datetime.now()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                padding: 20px 30px; border-radius: 15px; margin-bottom: 20px;
                display: flex; align-items: center; justify-content: space-between;
                border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div>
            <h1 style="margin: 0; color: #1b5e20; font-size: 28px;">🧹 Container Cleaning System</h1>
            <p style="margin: 5px 0 0 0; color: #4caf50; font-size: 14px;">
                Smart Priority Queue Management &mdash; Critical Ratio Algorithm
            </p>
        </div>
        <div style="text-align: right; color: #1a1a1a;">
            <div style="font-size: 24px; font-weight: bold; color: #1b5e20;">{now.strftime("%H:%M")}</div>
            <div style="font-size: 12px; color: #888;">{now.strftime("%d %b %Y")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Three Column Layout
    col1, col2, col3 = st.columns([1.1, 1.1, 1.0])
    
    # ============================================================
    # COLUMN 1: INPUT DATA CLEANING
    # ============================================================
    with col1:
        st.markdown("""
        <div class="panel-header" style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);">
            <span style="font-size: 20px;">📝</span>
            <span>Input Data Cleaning</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        
        with st.form("input_form", border=False):
            container_id = st.text_input("No. Kontainer", value="SPNU ", placeholder="SPNU XXXXXX")
            container_type = st.selectbox("Tipe Kontainer", 
                ['Reefer 20ft', 'Reefer 40ft', 'Dry 20ft', 'Dry 40ft', 'Flat Rack 20ft', 'Flat Rack 40ft'])
            cargo_type = st.selectbox("Jenis Muatan", 
                ['Daging beku', 'Sayur buah', 'Farmasi', 'Food grade', 'Chemical', 
                 'Jagung', 'Biji sawit', 'General', 'Alat berat'])
            
            if cargo_type in ['Daging beku', 'Sayur buah', 'Farmasi', 'Food grade']:
                st.markdown("""
                <div class="info-banner">
                    Kontainer <strong>food grade</strong> &mdash; prioritas otomatis ditingkatkan
                </div>
                """, unsafe_allow_html=True)
            
            dirt_level = st.select_slider("Tingkat Kekotoran", options=['Ringan', 'Sedang', 'Berat'], value='Sedang')
            
            col_due1, col_due2 = st.columns(2)
            with col_due1: due_date = st.date_input("Tanggal Due", value=datetime.now().date())
            with col_due2: due_time = st.time_input("Jam Due", value=(datetime.now() + timedelta(hours=8)).time())
            
            due_datetime = datetime.combine(due_date, due_time)
            ro_info = st.text_input("Info RO (opsional)", placeholder="Contoh: RO hari H")
            
            score_data = calculate_priority_score(container_type, cargo_type, dirt_level, due_datetime)
            priority_class = get_priority_class(score_data['final_score'], score_data['critical_ratio'])
            bar_color = get_progress_bar_color(priority_class)
            progress_width = min(100, score_data['final_score'] / 2)
            
            # HTML ini dipanjangkan jadi 1 baris supaya aman dari bug Markdown
            html_score_preview = f'<div style="background-color: #f8f9fa; border-radius: 10px; padding: 12px; margin: 15px 0; border: 1px solid #e0e0e0;"><div style="display: flex; justify-content: space-between; align-items: center;"><span style="color: #666; font-size: 13px;">Estimasi Durasi</span><span style="color: #2e7d32; font-size: 16px; font-weight: bold;">{score_data["estimated_duration"]} mnt</span></div><div class="divider" style="margin: 8px 0;"></div><div style="display: flex; justify-content: space-between; align-items: center;"><span style="color: #666; font-size: 13px;">Priority Score</span><div>{get_priority_badge_html(priority_class)}</div></div><div style="display: flex; justify-content: space-between; margin-top: 8px;"><span style="color: #888; font-size: 11px;">Base: {score_data["base_priority"]} x Cargo: {score_data["cargo_multiplier"]} x Dirt: {score_data["dirt_multiplier"]}</span><span style="color: #666; font-size: 11px;">CR: {score_data["critical_ratio"]}x</span></div><div class="progress-bar" style="margin-top: 10px;"><div class="progress-fill" style="width: {progress_width}%; background: {bar_color};"></div></div></div>'
            st.markdown(html_score_preview, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Tambah ke Antrian", use_container_width=True, type="primary")
            
            if submitted:
                new_item = {
                    'id': container_id, 'container_type': container_type, 'cargo_type': cargo_type,
                    'dirt_level': dirt_level, 'due_datetime': due_datetime, 'ro_info': ro_info, 'added_at': datetime.now(),
                }
                st.session_state.queue.append(new_item)
                st.session_state.success_toast = f"{container_id} ditambahkan ke antrian!"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # COLUMN 2: CLEANING BERLANGSUNG
    # ============================================================
    with col2:
        st.markdown("""
        <div class="panel-header" style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);">
            <span style="font-size: 20px;">⏱️</span>
            <span>Cleaning Berlangsung</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        
        if st.session_state.in_progress:
            job = st.session_state.in_progress
            now = datetime.now()
            elapsed = (now - job['start_time']).total_seconds()
            estimated = job['estimated_duration'] * 60
            remaining = max(0, estimated - elapsed)
            
            # Format timer jam & menit
            mins, secs = divmod(int(remaining), 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                time_display = f"{hours:02d}:{mins:02d}:{secs:02d}"
            else:
                time_display = f"{mins:02d}:{secs:02d}"
            
            progress_pct = min(100, (elapsed / estimated) * 100) if estimated > 0 else 100
            
            # Perbaikan: Hanya tampilkan tag food grade jika memang tipenya makanan
            food_grade_tags = '<span class="tag tag-food">Food grade</span>' if job['cargo_type'] in ['Daging beku', 'Sayur buah', 'Farmasi', 'Food grade'] else ''
            ro_html = f'<span class="tag tag-ro">{job["ro_info"]}</span>' if job['ro_info'] else ''
            
            # Perbaikan Bug: HTML di bawah ditulis memanjang satu baris 
            html_berlangsung = f'<div style="background-color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.06);"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;"><span style="font-weight: bold; font-size: 18px; color: #1a1a1a;">{job["id"]}</span><span class="badge-high">Urgensi tinggi</span></div><div style="margin-bottom: 12px;"><span class="tag tag-type">{job["container_type"]}</span><span class="tag">{job["cargo_type"]}</span><span class="tag">{job["dirt_level"]}</span></div><div style="margin-bottom: 10px;">{food_grade_tags}<span class="tag tag-time">Est. {job["estimated_duration"]} mnt</span>{ro_html}</div></div><div class="timer-display"><div class="timer-value">{time_display}</div><div class="timer-label">dari estimasi {job["estimated_duration"]} menit</div></div><div style="margin-top: 15px;"><div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><span style="font-size: 12px; color: #aaa;">Progress</span><span style="font-size: 12px; color: #4caf50;">{int(progress_pct)}%</span></div><div class="progress-bar"><div class="progress-fill" style="width: {progress_pct}%; background: linear-gradient(90deg, #4caf50, #66bb6a);"></div></div></div>'
            
            st.markdown(html_berlangsung, unsafe_allow_html=True)
            
            actual_duration = st.number_input("Durasi Aktual (menit)", min_value=1, max_value=200, value=job['estimated_duration'], step=1)
            notes = st.text_area("Catatan (opsional)", placeholder="Tambahkan catatan cleaning...", height=60)
            
            if st.button("Selesai Cleaning", type="primary", use_container_width=True):
                st.session_state.completed_today += 1
                st.session_state.in_progress = None
                st.session_state.success_toast = "Cleaning selesai dicatat!"
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px; color: #888;">
                <div style="font-size: 48px; margin-bottom: 10px;">⏸️</div>
                <div style="font-size: 16px; color: #555;">Tidak ada cleaning aktif</div>
                <div style="font-size: 13px; margin-top: 5px; color: #888;">Pilih kontainer dari antrian untuk memulai</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.queue:
                scored_queue = []
                for item in st.session_state.queue:
                    score = calculate_priority_score(item['container_type'], item['cargo_type'], item['dirt_level'], item['due_datetime'])
                    scored_queue.append((item, score))
                scored_queue.sort(key=lambda x: x[1]['final_score'], reverse=True)
                next_item = scored_queue[0][0]
                next_score = scored_queue[0][1]
                
                # HTML satu baris
                html_next_item = f'<div style="background-color: #e8f5e9; border: 1px solid #4caf50; border-radius: 10px; padding: 12px; margin: 15px 0;"><div style="font-size: 13px; color: #2e7d32; margin-bottom: 5px;">Next Priority:</div><div style="font-weight: bold; color: #1a1a1a;">{next_item["id"]} &mdash; {next_item["container_type"]}</div><div style="font-size: 12px; color: #666;">{next_item["cargo_type"]} | Score: {next_score["final_score"]} | ~{next_score["estimated_duration"]} mnt</div></div>'
                st.markdown(html_next_item, unsafe_allow_html=True)
                
                if st.button("Mulai Cleaning", type="primary", use_container_width=True):
                    st.session_state.queue = [q for q in st.session_state.queue if q['id'] != next_item['id']]
                    st.session_state.in_progress = {
                        'id': next_item['id'], 'container_type': next_item['container_type'],
                        'cargo_type': next_item['cargo_type'], 'dirt_level': next_item['dirt_level'],
                        'start_time': datetime.now(), 'estimated_duration': next_score['estimated_duration'],
                        'due_datetime': next_item['due_datetime'], 'ro_info': next_item['ro_info'],
                    }
                    st.session_state.success_toast = f"Mulai mengerjakan {next_item['id']}!"
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # COLUMN 3: STATUS & ANTRIAN
    # ============================================================
    with col3:
        st.markdown("""
        <div class="panel-header" style="background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);">
            <span style="font-size: 20px;">📊</span>
            <span>Status Depo Hari Ini</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: render_stat_card("Selesai", st.session_state.completed_today, "✅")
        with c2: render_stat_card("Siap Pakai", st.session_state.available, "📦")
        with c3: 
            queue_count = len(st.session_state.queue) + (1 if st.session_state.in_progress else 0)
            render_stat_card("Antrian", queue_count, "⏳")
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='margin-bottom: 12px;'>📋 Antrian Cleaning</h4>", unsafe_allow_html=True)
        
        if st.session_state.in_progress:
            job = st.session_state.in_progress
            elapsed = (datetime.now() - job['start_time']).total_seconds()
            progress_pct = min(100, (elapsed / (job['estimated_duration'] * 60)) * 100) if job['estimated_duration'] > 0 else 100
            
            # HTML satu baris
            active_html = f'<div style="background: linear-gradient(135deg, #1b5e20, #2e7d32); border-radius: 12px; padding: 14px; margin-bottom: 15px; color: white; box-shadow: 0 2px 8px rgba(27,94,32,0.3);"><div style="font-size: 11px; opacity: 0.9; margin-bottom: 5px;">SEDANG DIKERJAKAN</div><div style="font-weight: bold; font-size: 15px;">{job["id"]}</div><div style="font-size: 12px; opacity: 0.95;">{job["container_type"]} &bull; {job["cargo_type"]}</div><div class="progress-bar" style="margin-top: 8px; background: rgba(255,255,255,0.3);"><div class="progress-fill" style="width: {progress_pct}%; background: white;"></div></div></div>'
            st.markdown(active_html, unsafe_allow_html=True)
        
        if st.session_state.queue:
            scored_queue = []
            for item in st.session_state.queue:
                score = calculate_priority_score(item['container_type'], item['cargo_type'], item['dirt_level'], item['due_datetime'])
                scored_queue.append((item, score))
            scored_queue.sort(key=lambda x: x[1]['final_score'], reverse=True)
            
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                if st.button("Semua", key="btn_all", use_container_width=True): st.session_state.queue_filter = "ALL"
            with col_f2:
                if st.button("Urgent", key="btn_urgent", use_container_width=True): st.session_state.queue_filter = "URGENT"
            with col_f3:
                if st.button("Normal", key="btn_normal", use_container_width=True): st.session_state.queue_filter = "NORMAL"
            
            filter_mode = st.session_state.get('queue_filter', 'ALL')
            
            displayed = 0
            # 1. Tambahkan 'enumerate' untuk mendapatkan index (i)
            for i, (item, score) in enumerate(scored_queue):
                priority_class = get_priority_class(score['final_score'], score['critical_ratio'])
                
                if filter_mode == "URGENT" and priority_class not in ["EMERGENCY", "HIGH"]: continue
                if filter_mode == "NORMAL" and priority_class not in ["MEDIUM", "LOW"]: continue
                
                col_item, col_del = st.columns([0.88, 0.12], vertical_alignment="center", gap="small")
                with col_item:
                    render_queue_item(item, score)
                with col_del:
                    # 2. Sisipkan variabel 'i' ke dalam key agar selalu unik
                    if st.button("🗑️", key=f"del_{i}_{item['id']}", help="Hapus antrian"):
                        # 3. Gunakan .remove(item) agar hanya menghapus satu item spesifik tersebut
                        st.session_state.queue.remove(item)
                        st.session_state.success_toast = "Antrian berhasil dihapus!"
                        st.rerun()
                displayed += 1

            if displayed == 0:
                st.info("Tidak ada kontainer yang sesuai filter.")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 30px; color: #888;">
                <div style="font-size: 36px; margin-bottom: 10px;">📭</div>
                <div style="font-size: 14px; color: #555;">Antrian kosong</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # BOTTOM: ANALYTICS & METHOD
    # ============================================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1.2, 1.0])
    
    with col_a:
        st.markdown("""
        <div class="panel-header" style="background: linear-gradient(135deg, #1565c0, #1976d2);">
            <span style="font-size: 20px;">📈</span>
            <span>Distribusi Prioritas Antrian</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        
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
                    marker_color=['#e53935', '#ff6d00', '#ffca28', '#4caf50'],
                    text=[counts['EMERGENCY'], counts['HIGH'], counts['MEDIUM'], counts['LOW']],
                    textposition='auto',
                    textfont=dict(color='white', size=14),
                )
            ])

            fig.update_layout(
                font=dict(color="#1a1a1a", size=13),
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(title=dict(text="Priority Class", font=dict(color="#1a1a1a", size=14)), tickfont=dict(color="#1a1a1a", size=12)),
                yaxis=dict(title=dict(text="Jumlah Kontainer", font=dict(color="#1a1a1a", size=14)), tickfont=dict(color="#1a1a1a", size=12)),
                showlegend=False,
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data antrian untuk divisualisasikan.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class="panel-header" style="background: linear-gradient(135deg, #6a1b9a, #8e24aa);">
            <span style="font-size: 20px;">🧮</span>
            <span>Metode Critical Ratio</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="panel-body">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 13px; line-height: 1.6; color: #555;">
            <p><strong style="color: #1a1a1a;">Formula Priority Score:</strong></p>
            <div style="background-color: #f5f5f5; border-radius: 8px; padding: 10px; margin: 8px 0; font-family: 'Courier New', monospace; font-size: 12px; color: #1a1a1a; border: 1px solid #e0e0e0;">
                Score = Base x (1/CR) x Cargo x Dirt
            </div>
            <p><strong style="color: #1a1a1a;">Dimana:</strong></p>
            <ul style="padding-left: 18px; margin: 5px 0; color: #555;">
                <li><strong style="color: #1a1a1a;">Base</strong>: Prioritas dasar tipe (50-95)</li>
                <li><strong style="color: #1a1a1a;">CR</strong>: Sisa Waktu / Durasi Estimasi</li>
                <li><strong style="color: #1a1a1a;">Cargo</strong>: Multiplier sensitivitas (1.0-1.5)</li>
                <li><strong style="color: #1a1a1a;">Dirt</strong>: Multiplier kekotoran (1.0-1.3)</li>
            </ul>
            <div class="divider" style="background-color: #e0e0e0;"></div>
            <p><strong style="color: #1a1a1a;">Kategori Prioritas:</strong></p>
            <table style="width: 100%; font-size: 12px; margin-top: 8px; color: #555;">
                <tr>
                    <td><span class="badge-emergency">EMERGENCY</span></td>
                    <td style="text-align: right;">Score >= 150 / CR &lt; 0.5</td>
                </tr>
                <tr><td colspan="2" style="height: 5px;"></td></tr>
                <tr>
                    <td><span class="badge-high">HIGH</span></td>
                    <td style="text-align: right;">Score >= 100 / CR &lt; 1.5</td>
                </tr>
                <tr><td colspan="2" style="height: 5px;"></td></tr>
                <tr>
                    <td><span class="badge-medium">MEDIUM</span></td>
                    <td style="text-align: right;">Score >= 60</td>
                </tr>
                <tr><td colspan="2" style="height: 5px;"></td></tr>
                <tr>
                    <td><span class="badge-low">LOW</span></td>
                    <td style="text-align: right;">Score &lt; 60</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()