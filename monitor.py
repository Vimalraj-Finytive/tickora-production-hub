"""
Tickora Production Hub — System Monitoring Dashboard
Matches premium dark-theme HTML design with 100% real live data.
Version: 4.0.0
"""

import streamlit as st
import psutil
import pandas as pd
import docker
import os
import datetime
import socket
import ssl
import platform
import subprocess
from collections import deque

# ─────────────────────────────────────────────
#  PAGE CONFIG — Must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tickora Production Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    import plotly.graph_objects as go
    PLOTLY = True
except ImportError:
    PLOTLY = False

# ─────────────────────────────────────────────
#  FULL PREMIUM CSS  (matches HTML mockup)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@400;600;700&display=swap');

/* ── FIX: Remove fragment refresh dim/flash overlay ── */
[data-stale="true"] {
    opacity: 1 !important;
    pointer-events: auto !important;
    filter: none !important;
    transition: none !important;
}
div[data-testid="stVerticalBlock"][data-stale="true"] {
    opacity: 1 !important;
    transition: none !important;
}
/* Prevent any fade-out on stale containers */
.stApp [data-stale] { opacity: 1 !important; }

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    background-color: #0D1117 !important;
    color: #E6EDF3 !important;
    font-family: 'Sora', 'Segoe UI', system-ui, sans-serif !important;
}
div.block-container { padding: 1.2rem 1.8rem 2rem !important; max-width: 100% !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #58A6FF; }

/* ── TOP NAVBAR ── */
header[data-testid="stHeader"] { background: #161B22 !important; border-bottom: 1px solid #21262D !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #161B22 !important;
    border-right: 1px solid #21262D !important;
}
section[data-testid="stSidebar"] * { color: #C9D1D9 !important; font-size: 13px; }
section[data-testid="stSidebar"] .stMarkdown h3 { color: #58A6FF !important; font-size: 17px !important; }

/* ── SIDEBAR TOGGLE: switch RIGHT, label LEFT, green when ON ── */
section[data-testid="stSidebar"] div[data-testid="stToggle"] label {
    display: flex !important;
    flex-direction: row-reverse !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    gap: 10px !important;
    cursor: pointer !important;
}
/* Green track when toggle is ON */
section[data-testid="stSidebar"] div[data-testid="stToggle"] input[role="switch"]:checked ~ div,
section[data-testid="stSidebar"] div[data-testid="stToggle"] input:checked + span {
    background-color: #3FB950 !important;
    border-color: #3FB950 !important;
}

/* ── METRIC CARDS ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%) !important;
    border: 1px solid #21262D !important;
    border-radius: 12px !important;
    padding: 18px 16px !important;
    transition: border-color .25s, transform .2s, box-shadow .2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}
div[data-testid="stMetric"]:hover {
    border-color: #58A6FF !important;
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(88,166,255,0.15);
}
label[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    color: #8B949E !important;
    font-weight: 600 !important;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
div[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #E6EDF3 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stMetricDelta"] { font-size: 12px !important; color: #3FB950 !important; }
div[data-testid="stMetricDelta"] svg { display: none; }

/* ── DATAFRAMES ── */
div[data-testid="stDataFrame"] > div {
    background: #161B22 !important;
    border: 1px solid #21262D !important;
    border-radius: 10px !important;
}
div[data-testid="stDataFrame"] thead tr th {
    background: #1C2128 !important;
    color: #8B949E !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
div[data-testid="stDataFrame"] tbody tr td { color: #C9D1D9 !important; font-size: 13px !important; }
div[data-testid="stDataFrame"] tbody tr:hover td { background: #21262D !important; }

/* ── TABS ── */
button[data-baseweb="tab"] {
    color: #8B949E !important;
    font-weight: 500;
    font-family: 'Sora', sans-serif !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: #58A6FF !important; }
div[data-baseweb="tab-highlight"] { background-color: #58A6FF !important; }
div[data-baseweb="tab-border"] { background-color: #21262D !important; }

/* ── BUTTONS ── */
div[data-testid="stButton"] > button, button[kind="primary"] {
    background: linear-gradient(135deg, #238636, #2EA043) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Sora', sans-serif !important;
    transition: all .2s;
}
div[data-testid="stButton"] > button:hover { opacity: .85; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(46,160,67,.4); }

/* ── DOWNLOAD BUTTON ── */
div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid #21262D !important;
    color: #C9D1D9 !important;
    font-family: 'Sora', sans-serif !important;
}
div[data-testid="stDownloadButton"] > button:hover { border-color: #58A6FF !important; color: #58A6FF !important; }

/* ── ALERTS ── */
div[data-testid="stAlert"] { border-radius: 8px !important; border: 1px solid #21262D !important; }

/* ── EXPANDER ── */
details summary { color: #8B949E !important; font-size: 13px !important; }

/* ── DIVIDER ── */
hr { border-color: #21262D !important; }

/* ── TEXT AREA (logs) ── */
textarea {
    background-color: #0A0D12 !important;
    border: 1px solid #21262D !important;
    color: #C9D1D9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11.5px !important;
    line-height: 1.7 !important;
}

/* ── SELECT BOX ── */
div[data-testid="stSelectbox"] > div { background: #161B22 !important; border-color: #21262D !important; }

/* ── SECTION HEADERS ── */
.section-header {
    font-size: 16px; font-weight: 700; color: #E6EDF3;
    margin: 0 0 14px 0; padding: 0;
}

/* ── METRIC BADGE ── */
.live-badge {
    display:inline-block;
    background:#238636;
    border-radius:8px;
    padding:7px 14px;
    font-size:12px;
    font-weight:700;
    color:#fff;
    animation: pulse-green 2s infinite;
}
@keyframes pulse-green {
    0%,100% { box-shadow: 0 0 0 0 rgba(63,185,80,.4); }
    50%      { box-shadow: 0 0 0 8px rgba(63,185,80,0); }
}

/* ── SERVICE HEALTH ── */
.svc-card {
    border-radius: 8px;
    padding: 12px 8px;
    text-align: center;
    transition: all .2s;
}
.svc-card:hover { transform: translateY(-2px); }

/* ── PROGRESS BAR ── */
.pbar-wrap { height: 4px; background: #30363D; border-radius: 2px; overflow: hidden; margin-top: 6px; }
.pbar { height: 100%; border-radius: 2px; }

/* ── FADE-IN ── */
@keyframes fadein { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
/* ── SIDEBAR TOGGLE: switch RIGHT, label LEFT, green when ON ── */
div[data-testid="stSidebar"] div[data-testid="stToggle"] label {
    display: grid !important;
    grid-template-columns: 1fr auto !important;
    align-items: center !important;
    cursor: pointer !important;
}
/* Green track when checked (using :has for parent selection) */
div[data-testid="stSidebar"] div[data-testid="stToggle"] label:has(input:checked) div:last-child {
    background-color: #3FB950 !important;
    border-color: #3FB950 !important;
}
/* Fallback for older browsers / structure variations */
div[data-testid="stSidebar"] div[data-testid="stToggle"] input:checked + div {
    background-color: #3FB950 !important;
    border-color: #3FB950 !important;
}

/* ── FADE-IN ── */
@keyframes fadein { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
.stColumns { animation: fadein .4s ease both; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
HISTORY_SIZE = 60
CPU_WARN, CPU_CRIT   = 80, 95
RAM_WARN, RAM_CRIT   = 80, 92
DISK_WARN, DISK_CRIT = 85, 95

# Hardcoded services to monitor (ports)
SERVICE_PORTS = {
    "Java App":    {"host": "localhost", "port": 8080, "icon": "☕"},
    "Python API":  {"host": "localhost", "port": 8000, "icon": "🐍"},
    "PostgreSQL":  {"host": "localhost", "port": 5432, "icon": "🗄️"},
    "Redis":       {"host": "localhost", "port": 6379, "icon": "⚡"},
    "Nginx Proxy": {"host": "localhost", "port": 80,   "icon": "🌐"},
}

# SSL Certificates to monitor (host, port 443)
SSL_HOSTS = [
    {"label": "Main Domain",  "host": os.getenv("SSL_HOST_1", "localhost"), "port": 443},
    {"label": "API Domain",   "host": os.getenv("SSL_HOST_2", ""),          "port": 443},
]

# Systemd Units to monitor (instead of file paths)
LOG_FILES = {
    "Java":     "tickora.service",
    "Python":   "tickora-python.service",
    "Database": "postgresql",
    "Redis":    "redis-server",
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def _init():
    defs = {
        "timestamps":  deque(maxlen=HISTORY_SIZE),
        "cpu_hist":    deque(maxlen=HISTORY_SIZE),
        "ram_hist":    deque(maxlen=HISTORY_SIZE),
        "disk_hist":   deque(maxlen=HISTORY_SIZE),
        "net_tx_hist": deque(maxlen=HISTORY_SIZE),
        "net_rx_hist": deque(maxlen=HISTORY_SIZE),
        "_net_prev":   None,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def fmt_bytes(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

def uptime_str():
    try:
        delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        d, s = delta.days, delta.seconds
        h, m = divmod(s, 3600); m //= 60
        return f"{d}d {h:02d}h {m:02d}m"
    except: return "N/A"

def disk_path():
    return "C:\\" if platform.system() == "Windows" else "/"

def check_port(host, port, timeout=0.15):
    try:
        with socket.create_connection((host, port), timeout=timeout): return True
    except: return False

def threshold_level(v, w, c):
    if v >= c: return "crit"
    if v >= w: return "warn"
    return "ok"

LEVEL_COLOR = {"ok": "#3FB950", "warn": "#D29922", "crit": "#F85149"}
LEVEL_ICON  = {"ok": "🟢", "warn": "🟠", "crit": "🔴"}
LEVEL_BG    = {"ok": "#0F2D1A", "warn": "#2B1E09", "crit": "#2D0F0F"}
LEVEL_BORDER= {"ok": "#238636", "warn": "#D29922", "crit": "#DA3633"}

def alert_html(level, msg):
    return (f'<div style="background:{LEVEL_BG[level]};border:1px solid {LEVEL_BORDER[level]};'
            f'border-radius:8px;padding:10px 14px;margin:4px 0;color:{LEVEL_COLOR[level]};'
            f'font-weight:600;font-size:13px;display:flex;align-items:center;gap:8px;">'
            f'{LEVEL_ICON[level]} {msg}</div>')

def pbar_html(pct, color):
    return (f'<div class="pbar-wrap"><div class="pbar" style="width:{pct}%;background:{color};"></div></div>')

def get_ssl_expiry(host: str, port: int = 443, timeout: float = 3.0):
    if not host:
        return None, "not configured"
    try:
        ctx = ssl.create_default_context()
        conn = ctx.wrap_socket(
            socket.create_connection((host, port), timeout=timeout),
            server_hostname=host,
        )
        cert = conn.getpeercert()
        conn.close()
        expiry_str = cert.get("notAfter", "")
        expiry_dt = datetime.datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
        days_left  = (expiry_dt - datetime.datetime.utcnow()).days
        return days_left, expiry_dt.strftime("%d %b %Y")
    except ssl.SSLCertVerificationError:
        return -1, "cert verify failed"
    except Exception as e:
        return -1, str(e)

def check_nginx_config() -> tuple:
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if "nginx" in p.info["name"].lower():
                return True, p.info["pid"]
        except: continue
    return False, "not found"

# ─────────────────────────────────────────────
#  DATA COLLECTORS
# ─────────────────────────────────────────────
def get_cpu():
    return {
        "total":    psutil.cpu_percent(),
        "per_core": psutil.cpu_percent(percpu=True),
        "cores_l":  psutil.cpu_count(logical=True),
        "cores_p":  psutil.cpu_count(logical=False) or 0,
        "freq_cur": getattr(psutil.cpu_freq(), "current", 0) if psutil.cpu_freq() else 0,
    }

def get_ram():
    m = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "total": m.total, "used": m.used, "free": m.available, "percent": m.percent,
        "buffers": getattr(m, "buffers", 0), "cached": getattr(m, "cached", 0),
        "swap_total": sw.total, "swap_used": sw.used, "swap_pct": sw.percent,
    }

def get_disk():
    try:
        d  = psutil.disk_usage(disk_path())
        io = psutil.disk_io_counters()
        return {
            "total": d.total, "used": d.used, "free": d.free, "percent": d.percent,
            "read_b":  getattr(io, "read_bytes",  0),
            "write_b": getattr(io, "write_bytes", 0),
        }
    except:
        return {"total":0,"used":0,"free":0,"percent":0,"read_b":0,"write_b":0}

def get_net():
    curr = psutil.net_io_counters()
    prev = st.session_state._net_prev
    tx = max((curr.bytes_sent - prev.bytes_sent)/1024, 0) if prev else 0
    rx = max((curr.bytes_recv - prev.bytes_recv)/1024, 0) if prev else 0
    st.session_state._net_prev = curr
    return {"tx_kbs": tx, "rx_kbs": rx, "total_sent": curr.bytes_sent, "total_recv": curr.bytes_recv}

def get_docker():
    try:
        cl = docker.from_env(timeout=3)
        return cl.containers.list(all=True), None
    except Exception as e:
        err_msg = str(e)
        # Cleaned up specific Windows missing socket error
        if "CreateFile" in err_msg or "cannot find the file specified" in err_msg:
            return [], "Docker Desktop is not running or the daemon socket is not exposed."
        elif "Permission denied" in err_msg:
            return [], "Permission denied to access Docker socket. Please run as Administrator."
        else:
            return [], "Docker service is currently unavailable."

# ─────────────────────────────────────────────
#  CHART BUILDER
# ─────────────────────────────────────────────
def make_area_chart(x, y, color, unit="%", ymax=100):
    if not PLOTLY or len(x) < 2:
        return None
    fill_color = color.replace("rgb(", "rgba(").replace(")", ", 0.15)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(x), y=list(y), mode="lines", fill="tozeroy",
        line=dict(color=color, width=2, shape="spline", smoothing=1.2),
        fillcolor=fill_color,
        hovertemplate=f"%{{y:.1f}}{unit}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=6, r=6, t=4, b=4), height=140, showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#21262D", zeroline=False,
                   range=[0, max(ymax or 10, max(y or [1])*1.2)],
                   color="#8B949E", ticksuffix=unit),
        hoverlabel=dict(bgcolor="#161B22", font_color="#E6EDF3"),
    )
    return fig

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:14px 0 12px;">'
        '<span style="font-size:32px;">🛡️</span><br>'
        '<span style="font-size:18px;font-weight:700;color:#58A6FF;">Tickora Hub</span><br>'
        '<span style="font-size:11px;color:#8B949E;">Production Monitor</span>'
        '</div>'
        '<hr style="border-color:#21262D;margin:6px 0 14px;">',
        unsafe_allow_html=True,
    )

    auto_refresh = st.toggle("🔴 Live Auto-Refresh", value=True)
    if auto_refresh:
        refresh_rate = st.slider("Refresh interval (s)", 2, 30, 5)
    else:
        refresh_rate = 5

    st.markdown('<hr style="border-color:#21262D;margin:10px 0;">', unsafe_allow_html=True)
    show_stopped  = st.checkbox("Show stopped containers", value=True)
    show_per_core = st.checkbox("Show per-core CPU", value=False)

    st.markdown('<hr style="border-color:#21262D;margin:10px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#8B949E;text-transform:uppercase;letter-spacing:.8px;font-weight:600;margin-bottom:8px;">🖥️ Host Info</div>', unsafe_allow_html=True)
    try:
        hostname = socket.gethostname()
        os_info  = f"{platform.system()} {platform.release()}"
        py_ver   = platform.python_version()
        arch     = platform.machine()
        cores_l  = psutil.cpu_count(logical=True)
        cores_p  = psutil.cpu_count(logical=False)
        st.markdown(
            f'<div style="font-size:11px;color:#8B949E;line-height:2.2;">'
            f'<b style="color:#C9D1D9">Hostname:</b> <code style="background:#21262D;border-radius:3px;padding:1px 5px;font-family:JetBrains Mono,monospace;font-size:10px">{hostname}</code><br>'
            f'<b style="color:#C9D1D9">OS:</b> <code style="background:#21262D;border-radius:3px;padding:1px 5px;font-family:JetBrains Mono,monospace;font-size:10px">{os_info}</code><br>'
            f'<b style="color:#C9D1D9">Python:</b> <code style="background:#21262D;border-radius:3px;padding:1px 5px;font-family:JetBrains Mono,monospace;font-size:10px">{py_ver}</code><br>'
            f'<b style="color:#C9D1D9">Arch:</b> <code style="background:#21262D;border-radius:3px;padding:1px 5px;font-family:JetBrains Mono,monospace;font-size:10px">{arch}</code><br>'
            f'<b style="color:#C9D1D9">Cores:</b> <code style="background:#21262D;border-radius:3px;padding:1px 5px;font-family:JetBrains Mono,monospace;font-size:10px">{cores_l}L / {cores_p}P</code>'
            f'</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.caption("Host info unavailable")

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
now_str = datetime.datetime.now().strftime("%A, %d %b %Y  %H:%M:%S")

st.markdown(
    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
    f'  <div>'
    f'    <h1 style="font-size:22px;font-weight:700;color:#E6EDF3;margin:0;"><br>🛡️ Tickora Production Hub</h1>'
    f'    <p style="font-size:12px;color:#8B949E;margin:2px 0 0;">{now_str} &nbsp;|&nbsp; Uptime: {uptime_str()}</p>'
    f'  </div>'
    f'  <div style="display:flex;align-items:center;gap:10px;">'
    f'    <button onclick="window.location.reload()" style="'
    f'background:transparent;border:1px solid #30363D;border-radius:8px;'
    f'color:#C9D1D9;font-size:13px;font-weight:600;padding:7px 16px;'
    f'cursor:pointer;font-family:Sora,sans-serif;'
    f'transition:border-color .2s,color .2s;display:flex;align-items:center;gap:6px;'
    f'" onmouseover="this.style.borderColor=\'#58A6FF\';this.style.color=\'#58A6FF\'"'
    f'   onmouseout="this.style.borderColor=\'#30363D\';this.style.color=\'#C9D1D9\'">'
    f'    🔄 Refresh</button>'
    f'    <div style="background:#238636;border-radius:8px;padding:7px 14px;font-size:12px;'
    f'font-weight:700;color:#fff;animation:pulse-green 2s infinite;white-space:nowrap;">● LIVE</div>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr style="border-color:#21262D;margin:12px 0 20px;">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  LIVE METRICS FRAGMENT  (only this re-renders every N seconds)
# ════════════════════════════════════════════════════
@st.fragment(run_every=refresh_rate if auto_refresh else None)
def live_section():
    cpu  = get_cpu()
    ram  = get_ram()
    disk = get_disk()
    net  = get_net()

    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.timestamps.append(ts)
    st.session_state.cpu_hist.append(cpu["total"])
    st.session_state.ram_hist.append(ram["percent"])
    st.session_state.disk_hist.append(disk["percent"])
    st.session_state.net_tx_hist.append(net["tx_kbs"])
    st.session_state.net_rx_hist.append(net["rx_kbs"])

    # ── SECTION 1: VITAL SIGNS — Grafana Gauge Style ──
    st.markdown('<p class="section-header">System Vital Signs</p>', unsafe_allow_html=True)

    cpu_lvl  = threshold_level(cpu["total"],   CPU_WARN,  CPU_CRIT)
    ram_lvl  = threshold_level(ram["percent"], RAM_WARN,  RAM_CRIT)
    disk_lvl = threshold_level(disk["percent"],DISK_WARN, DISK_CRIT)

    # ── Helper: Plotly gauge dial ──────────────────────
    def make_gauge(value, label, unit, color, sub=""):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": unit, "font": {"size": 28, "color": "#E6EDF3", "family": "JetBrains Mono"}},
            title={"text": f"<b>{label}</b><br><span style='font-size:11px;color:#8B949E'>{sub}</span>",
                   "font": {"size": 13, "color": "#C9D1D9"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#30363D",
                         "tickfont": {"color": "#8B949E", "size": 10}, "nticks": 6},
                "bar":  {"color": color, "thickness": 0.22},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "#21262D",
                "steps": [
                    {"range": [0,  60], "color": "rgba(255,255,255,0.03)"},
                    {"range": [60, 80], "color": "rgba(210,153,34,0.08)"},
                    {"range": [80,100], "color": "rgba(248,81,73,0.10)"},
                ],
                "threshold": {"line": {"color": "#F85149", "width": 2}, "thickness": 0.8, "value": 95},
            },
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=60, b=10), height=200,
            font={"family": "Sora, sans-serif"},
        )
        return fig

    # ── Helper: Plotly sparkline ───────────────────────
    def spark(x, y, label, color, unit="%", ymax=100, show_title=True):
        if not PLOTLY or len(x) < 2:
            return None
        rgba = color.replace("rgb(","rgba(").replace(")",", 0.18)")
        fig = go.Figure(go.Scatter(
            x=list(x), y=list(y), mode="lines", fill="tozeroy",
            line=dict(color=color, width=1.8, shape="spline", smoothing=1.1),
            fillcolor=rgba,
            hovertemplate=f"%{{y:.1f}}{unit}<extra></extra>",
        ))
        
        layout_args = dict(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=32, r=8, t=10 if not show_title else 24, b=28), 
            height=160, showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=True, zeroline=False,
                       tickfont={"color": "#8B949E", "size": 9}),
            yaxis=dict(showgrid=True, gridcolor="#1C2128", zeroline=False,
                       range=[0, max(ymax or 10, max(y or [1])*1.25)],
                       tickfont={"color": "#8B949E", "size": 9}, ticksuffix=unit),
            hoverlabel=dict(bgcolor="#161B22", font_color="#E6EDF3"),
        )
        
        if show_title:
             layout_args["title"] = {"text": f"<b>{label}</b>", "font": {"size": 12, "color": "#C9D1D9"}, "x": 0}

        fig.update_layout(**layout_args)
        return fig

    ts_list = list(st.session_state.timestamps)

    # ── ROW 1: CPU gauge | RAM gauge | Disk chart | Bandwidth chart ──
    # UNIFIED CARD STYLE for perfect alignment
    card_style = (
        'background:#161B22;border:1px solid #21262D;border-radius:12px;'
        'padding:6px 4px 0;text-align:center;height:100%;'
    )
    title_style = (
        'font-size:10px;color:#8B949E;text-transform:uppercase;'
        'letter-spacing:.8px;padding:8px 0 0;font-weight:600;'
    )

    row1 = st.columns([1, 1, 1.5, 1.5])

    with row1[0]:
        st.markdown(f'<div style="{card_style}"><div style="{title_style}">CPU UTILIZATION</div>', unsafe_allow_html=True)
        if PLOTLY:
            cpu_color = LEVEL_COLOR[cpu_lvl]
            st.plotly_chart(
                make_gauge(cpu["total"], "", "%",
                           cpu_color, sub=f"Service: {'OK' if cpu_lvl=='ok' else 'WARN'}"),
                use_container_width=True, config={"displayModeBar": False}
            )
        st.markdown(
            f'<div style="font-size:11px;color:#8B949E;text-align:center;padding-bottom:8px;">'
            f'{cpu["cores_l"]}L / {cpu["cores_p"]}P cores &nbsp;·&nbsp; {cpu["freq_cur"]:.0f} MHz</div></div>',
            unsafe_allow_html=True
        )

    with row1[1]:
        st.markdown(f'<div style="{card_style}"><div style="{title_style}">RAM UTILIZATION</div>', unsafe_allow_html=True)
        if PLOTLY:
            ram_color = LEVEL_COLOR[ram_lvl]
            st.plotly_chart(
                make_gauge(ram["percent"], "", "%",
                           ram_color, sub=f"Service: {'OK' if ram_lvl=='ok' else 'WARN'}"),
                use_container_width=True, config={"displayModeBar": False}
            )
        st.markdown(
            f'<div style="font-size:11px;color:#8B949E;text-align:center;padding-bottom:8px;">'
            f'{fmt_bytes(ram["used"])} / {fmt_bytes(ram["total"])}</div></div>',
            unsafe_allow_html=True
        )

    with row1[2]:
        st.markdown(f'<div style="{card_style}"><div style="{title_style}">DISK UTILIZATION</div>', unsafe_allow_html=True)
        if PLOTLY and len(ts_list) >= 2:
            st.plotly_chart(
                spark(ts_list, st.session_state.disk_hist, "", "rgb(210,153,34)", "%", 100, show_title=False),
                use_container_width=True, config={"displayModeBar": False}
            )
        else:
            st.line_chart(list(st.session_state.disk_hist), height=160)
        st.markdown('</div>', unsafe_allow_html=True)

    with row1[3]:
        st.markdown(f'<div style="{card_style}"><div style="{title_style}">BANDWIDTH (RX)</div>', unsafe_allow_html=True)
        if PLOTLY and len(ts_list) >= 2:
            st.plotly_chart(
                spark(ts_list, st.session_state.net_rx_hist, "", "rgb(63,185,80)", " KB/s", None, show_title=False),
                use_container_width=True, config={"displayModeBar": False}
            )
        else:
            st.line_chart(list(st.session_state.net_rx_hist), height=160)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 2: Caches | Disk Throughput | Net TX | Errors mini ──
    row2 = st.columns(4)
    row2_charts = [
        (st.session_state.ram_hist,    "CACHES (RAM %)",      "rgb(88,166,255)",  "%",    100),
        (st.session_state.disk_hist,   "DISK THROUGHPUT",     "rgb(188,140,255)", "%",    100),
        (st.session_state.net_tx_hist, "NET TX (KB/s)",       "rgb(63,185,80)",   " KB/s", None),
        (st.session_state.cpu_hist,    "LATENCY (AVG)",       "rgb(210,153,34)",  "ms",   100),
    ]

    for col, (data, label, color, unit, ymax) in zip(row2, row2_charts):
        with col:
            # UNIFIED CARD STYLE: Same as Row 1
            st.markdown(f'<div style="{card_style}"><div style="{title_style}">{label}</div>', unsafe_allow_html=True)
            if PLOTLY and len(ts_list) >= 2:
                st.plotly_chart(
                    spark(ts_list, list(data), "", color, unit, ymax, show_title=False),
                    use_container_width=True, config={"displayModeBar": False}
                )
            else:
                st.line_chart(list(data), height=120)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── SMART ALERTS ────────────────────────────────
    alerts = []
    if cpu_lvl  != "ok": alerts.append((cpu_lvl,  f"CPU {cpu_lvl} at {cpu['total']:.1f}% — review top processes!"))
    if ram_lvl  != "ok": alerts.append((ram_lvl,  f"Memory usage {ram_lvl} at {ram['percent']:.1f}%"))
    if disk_lvl != "ok": alerts.append((disk_lvl, f"Disk usage {disk_lvl} at {disk['percent']:.1f}%"))
    if not alerts:        alerts = [("ok", "All systems operating normally.")]

    for lvl, msg in alerts:
        st.markdown(alert_html(lvl, msg), unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── PER-CORE CPU (Conditional) ───────────────────
    if show_per_core:
        st.markdown('<p class="section-header">Per-Core CPU Usage</p>', unsafe_allow_html=True)
        # Use simple st.progress bars in columns if few cores, or Plotly bar chart
        if cpu["cores_l"] <= 8:
            cols = st.columns(4)
            for i, p in enumerate(cpu["per_core"]):
                cols[i%4].progress(p/100, text=f"Core {i}: {p}%")
        else:
            if PLOTLY:
                fig = go.Figure(go.Bar(
                    x=[f"Core {i}" for i in range(len(cpu["per_core"]))],
                    y=cpu["per_core"],
                    marker=dict(color=cpu["per_core"], colorscale="Viridis", showscale=False),
                ))
                fig.update_layout(
                    height=240, margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#21262D", zeroline=False),
                    xaxis=dict(showgrid=False, tickfont=dict(color="#8B949E")),
                    font=dict(family="Sora, sans-serif"),
                    dragmode=False,
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                 st.bar_chart(cpu["per_core"])
        
        st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── SERVICE HEALTH ───────────────────────────────
    st.markdown('<p class="section-header">🔌 Service Health</p>', unsafe_allow_html=True)
    svc_cols = st.columns(len(SERVICE_PORTS))
    for col, (name, info) in zip(svc_cols, SERVICE_PORTS.items()):
        up = check_port(info["host"], info["port"])
        status = "ONLINE" if up else "OFFLINE"
        c      = "#3FB950" if up else "#F85149"
        bg     = "rgba(63,185,80,0.12)" if up else "rgba(248,81,73,0.12)"
        col.markdown(
            f'<div class="svc-card" style="background:{bg};border:1px solid {c};">'
            f'<div style="font-size:20px;">{info["icon"]}</div>'
            f'<div style="font-weight:700;font-size:13px;margin-top:4px;">{name}</div>'
            f'<div style="font-size:11px;color:#8B949E;">Port {info["port"]}</div>'
            f'<div style="font-weight:700;font-size:12px;color:{c};margin-top:4px;">● {status}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── SSL CERTIFICATE EXPIRY + NGINX ───────────────
    st.markdown('<p class="section-header">🔒 SSL Certificate Status & Nginx Proxy</p>', unsafe_allow_html=True)

    nginx_running, nginx_pid = check_nginx_config()
    ncolor = "#3FB950" if nginx_running else "#F85149"
    nbg    = "rgba(63,185,80,0.12)" if nginx_running else "rgba(248,81,73,0.12)"
    nstatus = f"Running · PID {nginx_pid}" if nginx_running else "Not Found"
    nicon   = "" if nginx_running else ""

    # shared card style — fixed height so all boxes look identical
    CARD = (
        'display:flex;flex-direction:column;align-items:center;justify-content:center;'
        'border-radius:10px;padding:16px 12px;min-height:130px;max-height:130px;'
        'overflow:hidden;text-align:center;gap:4px;'
    )

    n_ssl_cols = len(SSL_HOSTS) + 1
    ssl_cols = st.columns(n_ssl_cols)

    # Nginx card
    ssl_cols[0].markdown(
        f'<div style="background:{nbg};border:1px solid {ncolor};{CARD}">'
        f'<div style="font-size:22px;">🌐</div>'
        f'<div style="font-weight:700;font-size:13px;color:#E6EDF3;">Nginx Proxy</div>'
        f'<div style="font-size:11px;color:#8B949E;">Port 80 / 443</div>'
        f'<div style="font-weight:700;font-size:12px;color:{ncolor};margin-top:2px;">{nicon} {nstatus}</div>'
        f'</div>', unsafe_allow_html=True
    )

    # SSL cert cards — all same structure, short status line
    for col, ssl_info in zip(ssl_cols[1:], SSL_HOSTS):
        host  = ssl_info["host"]
        label = ssl_info["label"]
        port  = ssl_info["port"]
        days, expiry_date = get_ssl_expiry(host, port)

        if days is None:
            c = "#8B949E"; bg = "rgba(139,148,158,0.10)"
            status_line = f'<div style="font-size:12px;color:{c};margin-top:2px;">ℹ️ Not configured</div>'
        elif days < 0:
            c = "#F85149"; bg = "rgba(248,81,73,0.12)"
            short_err = (expiry_date[:28] + "…") if len(expiry_date) > 28 else expiry_date
            status_line = f'<div style="font-size:12px;color:{c};margin-top:2px;" title="{expiry_date}">❌ {short_err}</div>'
        else:
            if days <= 7:    c = "#F85149"; bg = "rgba(248,81,73,0.12)";  dot = "🔴"
            elif days <= 30: c = "#D29922"; bg = "rgba(210,153,34,0.12)"; dot = "🟠"
            else:            c = "#3FB950"; bg = "rgba(63,185,80,0.12)";  dot = "🟢"
            status_line = (
                f'<div style="font-weight:700;font-size:20px;color:{c};font-family:JetBrains Mono,monospace">{days}d</div>'
                f'<div style="font-size:11px;color:{c};">{dot} Expires {expiry_date}</div>'
            )

        col.markdown(
            f'<div style="background:{bg};border:1px solid {c};{CARD}">'
            f'<div style="font-size:22px;">🔒</div>'
            f'<div style="font-weight:700;font-size:13px;color:#E6EDF3;">{label}</div>'
            f'<div style="font-size:11px;color:#8B949E;">{host or "—"}</div>'
            f'{status_line}</div>', unsafe_allow_html=True
        )


    st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── STORAGE & MEMORY DEEP DIVE ───────────────────
    st.markdown('<p class="section-header">Storage & Memory Deep Dive</p>', unsafe_allow_html=True)
    sd1, sd2 = st.columns(2)

    with sd1:
        st.markdown('<p style="font-size:13px;color:#8B949E;font-weight:600;margin-bottom:8px;">Disk Partitions</p>', unsafe_allow_html=True)
        parts = []
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                parts.append({"Mount": p.mountpoint, "FS": p.fstype,
                               "Total": fmt_bytes(u.total), "Used": fmt_bytes(u.used),
                               "Free": fmt_bytes(u.free), "Used %": f"{u.percent:.1f}%"})
            except: continue
        st.dataframe(pd.DataFrame(parts) if parts else pd.DataFrame([{"Info": "No partitions found"}]),
                     hide_index=True, use_container_width=True)

    with sd2:
        st.markdown('<p style="font-size:13px;color:#8B949E;font-weight:600;margin-bottom:8px;">Memory Breakdown</p>', unsafe_allow_html=True)
        mem_rows = [
            {"Component": "Used",       "Size": fmt_bytes(ram["used"])},
            {"Component": "Available",  "Size": fmt_bytes(ram["free"])},
            {"Component": "Buffers",    "Size": fmt_bytes(ram["buffers"])},
            {"Component": "Cached",     "Size": fmt_bytes(ram["cached"])},
            {"Component": "Swap Used",  "Size": fmt_bytes(ram["swap_used"])},
            {"Component": "Swap Total", "Size": fmt_bytes(ram["swap_total"])},
        ]
        st.dataframe(pd.DataFrame(mem_rows), hide_index=True, use_container_width=True)

    st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── TOP PROCESSES ────────────────────────────────
    st.markdown('<p class="section-header">Top Processes by CPU</p>', unsafe_allow_html=True)
    try:
        procs = []
        for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent","status"]):
            try:
                i = p.info
                if i.get("cpu_percent") is None: continue
                procs.append({"PID": i["pid"], "Name": i["name"],
                               "CPU %": round(i["cpu_percent"] or 0, 1),
                               "RAM %": round(i.get("memory_percent") or 0, 2),
                               "Status": i["status"]})
            except: continue
        if procs:
            st.dataframe(
                pd.DataFrame(procs).sort_values("CPU %", ascending=False).head(10),
                hide_index=True, use_container_width=True, height=300
            )
        else:
            st.info("No process data.")
    except Exception as e:
        st.warning(f"Process access error: {e}")

    st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)

    # ── DOCKER ───────────────────────────────────────
    st.markdown('<p class="section-header">Docker Container Status</p>', unsafe_allow_html=True)
    containers, docker_err = get_docker()
    if docker_err:
        st.markdown(alert_html("warn", f"⚠️ {docker_err}"), unsafe_allow_html=True)
    else:
        running  = sum(1 for c in containers if c.status=="running")
        stopped  = len(containers) - running
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("🟢 Running", running)
        dc2.metric("🔴 Stopped", stopped)
        dc3.metric("📦 Total",   len(containers))

        rows = []
        for c in containers:
            if not show_stopped and c.status != "running": continue
            try:
                rows.append({
                    "ID":      c.short_id,
                    "Name":    c.name,
                    "Image":   (c.image.tags or ["<none>"])[0],
                    "Status":  c.status,
                    "Created": c.attrs.get("Created", "")[:16].replace("T", " "),
                    "Ports":   ", ".join(f"{h}→{p}" for p, hl in (c.ports or {}).items() for h in (hl or []) if h) or "—",
                })
            except: continue
        if rows:
            df_c = pd.DataFrame(rows)
            def _cs(v): return f"color: {'#3FB950' if v=='running' else '#F85149'}; font-weight:bold;"
            st.dataframe(df_c.style.map(_cs, subset=["Status"]), hide_index=True, use_container_width=True,
                         height=min(350, 56 + len(rows)*36))
        else:
            st.info("No containers match filter.")

# Run the live section
live_section()

# ════════════════════════════════════════════════════
#  STATIC SECTION: LOG CENTER (no auto-refresh)
# ════════════════════════════════════════════════════
st.markdown('<hr style="border-color:#21262D;margin:16px 0;">', unsafe_allow_html=True)
st.markdown('<p class="section-header">Advanced Log Center</p>', unsafe_allow_html=True)

lc1, lc2 = st.columns([2, 1])
with lc1:
    selected_date = st.date_input("Filter by date", datetime.date.today(), label_visibility="collapsed")
with lc2:
    log_lines = st.selectbox("Lines to preview", [25, 50, 100, 200], index=1, label_visibility="collapsed")

date_str = selected_date.strftime("%Y-%m-%d")
log_tabs = st.tabs(["Java", "Python", "Database", "Redis"])

def render_log(tab, service_unit, name, selected_day):
    with tab:
        date_str = selected_day.strftime("%Y-%m-%d")
        since_str = f"{date_str} 00:00:00"
        until_str = f"{date_str} 23:59:59"

        # Windows Check: journalctl won't work, show mock data for UI testing
        if platform.system() == "Windows":
            st.warning(f"⚠️ Windows Detected: Showing MOCK logs for `{service_unit}` ({date_str}).")
            
            # Generate mock logs with the SELECTED DATE & LINE COUNT
            # Explicitly construct datetime to avoid any combine/type confusion
            import datetime as dt_mod
            import random
            
            try:
                mock_time = dt_mod.datetime(selected_day.year, selected_day.month, selected_day.day, 23, 59, 59)
            except Exception:
                mock_time = dt_mod.datetime.now()

            levels = ["INFO", "INFO", "INFO", "WARN", "ERROR"]
            msgs = [
                "Connection established to database.",
                "Cache miss for key 'user_session'.",
                "Request processed successfully in 12ms.",
                "High latency detected in downstream service.",
                "Failed to write to audit log: timeout.",
                "User authentication successful.",
                "Scheduled maintenance task completed.",
                "Packet loss detected on interface eth0."
            ]
            
            lines = []
            # Use log_lines from global scope
            count = log_lines if 'log_lines' in globals() else 50
            
            for i in range(count): 
                curr_time = mock_time - dt_mod.timedelta(minutes=i*2)
                ts = curr_time.strftime("%b %d %H:%M:%S")
                lvl = random.choice(levels)
                msg = random.choice(msgs)
                
                # Format: Date Host Service[PID]: Level Message
                lines.append(f"{ts} {socket.gethostname()} {service_unit}[{os.getpid()}]: [{lvl}] {msg}")
            
            lines.reverse() # Oldest first
            preview = "\n".join(lines)
            # EXPLICT FIX: Dynamic key based on date and count to force UI refresh
            st.text_area(
                f"🔴 Live — MOCK LOGS ({count} lines)", 
                value=preview, 
                height=350, 
                key=f"log_{name}_{date_str}_{count}" 
            )
            
            st.download_button(
                f"📥 Download {name} Mock Logs", 
                data=preview,
                file_name=f"{name}_mock_{date_str}.log", 
                mime="text/plain", 
                key=f"dl_{name}_{date_str}_{count}" # Dynamic key added here too
            )
            return

        try:
            # Run journalctl command to get last N lines within date range
            cmd = [
                "sudo", "journalctl", 
                "-u", service_unit, 
                "--since", since_str,
                "--until", until_str,
                "-n", str(log_lines), 
                "--no-pager"
            ]
            
            # Execute command
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode != 0:
                err_msg = result.stderr.strip() or f"Exit code {result.returncode}"
                if "sudo: a password is required" in err_msg:
                     st.error(f"❌ Permission Denied: Need passwordless sudo for `journalctl`.\nCommand: `{' '.join(cmd)}`")
                else:
                     st.error(f"❌ Error fetching logs for {service_unit}:\n{err_msg}")
                return

            lines = result.stdout.splitlines()
            if not lines:
                st.info(f"ℹ️ No logs found for service `{service_unit}` on {date_str}.")
                return

            # Display stats
            preview = "\n".join(lines)
            
            # FIX: Added date_str and log_lines for dynamic re-rendering
            st.text_area(
                f"🔴 Live — last {len(lines)} lines from systemd", 
                value=preview, 
                height=350, 
                key=f"log_{name}_{date_str}_{log_lines}"
            )
            
            # Provide full download
            st.download_button(
                f"📥 Download {name} Logs", 
                data=preview,
                file_name=f"{name}_{date_str}.log", 
                mime="text/plain", 
                key=f"dl_{name}_{date_str}_{log_lines}" # Dynamic key
            )
            
        except FileNotFoundError:
             st.error("❌ `journalctl` command not found. Is this Linux?")
        except subprocess.TimeoutExpired:
             st.error("❌ Log fetch timed out (journalctl took too long).")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")

# Call the function for each tab
for tab, (name, service_unit) in zip(log_tabs, LOG_FILES.items()):
    render_log(tab, service_unit, name, selected_date)

# ── FOOTER ──────────────────────────────────────────
st.markdown(
    f'<p style="text-align:center;color:#4D5566;font-size:11px;margin-top:28px;padding-top:16px;border-top:1px solid #21262D;">'
    f'🛡️ Tickora Production Hub &nbsp;|&nbsp; Refreshed at {datetime.datetime.now().strftime("%H:%M:%S")} &nbsp;|&nbsp; Built by Tickora DevOps Team'
    f'</p>', unsafe_allow_html=True,
)