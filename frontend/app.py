import streamlit as st
import requests, plotly.graph_objects as go, plotly.express as px, time

# --- 🛰️ INTERNAL LINK TO BACKEND ---
# We point this to 8000 because your run.sh will start the API there.
API_URL = "http://localhost:8000"

st.set_page_config(page_title="TITAN COMMAND | v21", layout="wide")

# --- 🎨 DARK SCI-FI CSS ---
st.markdown("<style>.stApp { background-color: #050b14; color: #e0e0e0; } [data-testid='stMetricValue'] { color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff; }</style>", unsafe_allow_html=True)

# --- 📡 CONNECTION HANDSHAKE ---
try:
    # Increased timeout slightly for container internal networking
    response = requests.get(f"{API_URL}/status", timeout=2)
    data = response.json()
except Exception as e:
    st.error("🔴 NEURAL LINK SEVERED. START BACKEND FIRST.")
    st.info(f"Technical Detail: {e}")
    st.stop()

# --- 🏆 FINAL EVALUATION ---
if data.get('is_done'):
    st.balloons()
    surv, integ = data.get('lives_saved', 0), data.get('integrity', 0)
    # Balanced grading thresholds
    if surv > 5000 and integ > 80:
        grade = "A+ (LEGENDARY)"
    elif surv > 2000:
        grade = "B (VETERAN)"
    else:
        grade = "F (COLLAPSE)"
        
    st.markdown(f"<h1 style='text-align:center;'>GRADE: {grade}</h1>", unsafe_allow_html=True)
    if st.button("REDEPLOY FLEET", use_container_width=True, type="primary"):
        requests.post(f"{API_URL}/reset")
        st.rerun()
    st.stop()

# --- SIDEBAR: FLEET STATUS ---
st.sidebar.title("🎖️ FLEET STATUS")
for u, l in data.get('unit_levels', {}).items():
    cd = data.get('cooldowns', {}).get(u, 0)
    status_text = "✅ READY" if cd == 0 else f"⏳({cd}s)"
    st.sidebar.write(f"**{u.upper()}** (Lvl {l}) {status_text}")
    # Progress calculation based on XP thresholds
    xp_ratio = min(data.get('unit_xp', {}).get(u, 0) / (l * 30), 1.0)
    st.sidebar.progress(xp_ratio)

auto = st.sidebar.toggle("ENABLE AUTO-PILOT")
speed = st.sidebar.slider("HEARTBEAT SPEED", 0.5, 5.0, 1.5)

# --- HUD METRICS ---
h = data.get('history', {})
drain_val = h.get('drain', [0])[-1] if h.get('drain') else 150
st.markdown("## 🛰️ TITAN_COMMAND // MASTER_COMMAND_CENTER")
c1, c2, c3, c4 = st.columns(4)
c1.metric("TREASURY", f"${data.get('budget', 0):,}", f"-${drain_val}")
c2.metric("SAVED", f"{data.get('lives_saved', 0):,}")
c3.metric("INTEGRITY", f"{data.get('integrity', 0):.1f}%")
c4.metric("STEP", f"{data.get('steps_taken', 0)}/100")

# --- DISPATCH COMMANDS ---
st.divider()
st.write("### 🕹️ TACTICAL DISPATCH CENTER")
incidents = data.get('incidents', [])
if not incidents:
    st.info("Scanning for threats...")
else:
    for inc in incidents:
        col_i, col_u = st.columns([1, 2])
        col_i.write(f"**{inc['type'].upper()}** (Sev: {inc['severity']:.1f})")
        u1, u2, u3 = col_u.columns(3)
        
        # Unit Ready checks
        units_ready = data.get('unit_ready', {})
        
        if u1.button("🚁 HELI", key=f"h_{inc['id']}", disabled=not units_ready.get('helicopter')):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "helicopter"})
            st.rerun()
        if u2.button("🚒 FIRE", key=f"f_{inc['id']}", disabled=not units_ready.get('fire_truck')):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "fire_truck"})
            st.rerun()
        if u3.button("🚑 AMBU", key=f"a_{inc['id']}", disabled=not units_ready.get('ambulance')):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "ambulance"})
            st.rerun()

# --- ANALYTICS ROW ---
st.divider()
col_an, col_map = st.columns([1, 2])
with col_an:
    st.write("#### 📊 FLEET MIX & RECOVERIES")
    fleet = data.get('fleet_usage', {})
    if any(fleet.values()):
        fig_pie = px.pie(values=list(fleet.values()), names=list(fleet.keys()), hole=0.5)
        fig_pie.update_layout(height=220, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    rec = data.get('recovery_types', {})
    if any(rec.values()):
        fig_bar = px.bar(x=list(rec.keys()), y=list(rec.values()), color=list(rec.keys()))
        fig_bar.update_layout(height=220, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)

with col_map:
    st.write("#### 📡 THREAT MATRIX")
    fig_3d = go.Figure()
    for inc in incidents:
        fig_3d.add_trace(go.Scatter3d(x=[inc['x']], y=[inc['y']], z=[inc['severity']], mode='markers', marker=dict(size=10, color='red')))
    
    # Predictions logic
    for p in data.get('predictions', []):
        fig_3d.add_trace(go.Scatter3d(x=[p['x']], y=[p['y']], z=[0.5], mode='markers+text', text=[f"T-{p['steps']}"], marker=dict(size=12, color='yellow', opacity=0.3, symbol='diamond')))
    
    fig_3d.update_layout(height=450, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', scene_xaxis_visible=False)
    st.plotly_chart(fig_3d, use_container_width=True)

# --- FINANCIAL FORENSICS ---
st.divider()
st.write("#### 📉 THE DEATH SPIRAL: INTEGRITY vs. DRAIN")
steps = h.get('steps', [])
if len(steps) > 1:
    fig_spiral = go.Figure()
    fig_spiral.add_trace(go.Scatter(x=steps, y=h.get('integrity', []), name="Integrity (%)", line=dict(color='#00f2ff', width=3)))
    fig_spiral.add_trace(go.Scatter(x=steps, y=h.get('drain', []), name="Drain ($)", yaxis="y2", line=dict(color='#ff4b4b', dash='dot')))
    fig_spiral.update_layout(
        height=300, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font_color="white", 
        yaxis=dict(title="Integrity (%)"), 
        yaxis2=dict(title="Drain ($)", overlaying="y", side="right")
    )
    st.plotly_chart(fig_spiral, use_container_width=True)

# --- HEARTBEAT ---
if auto:
    ready_units = [u for u, r in data.get('unit_ready', {}).items() if r]
    if incidents and ready_units:
        top = sorted(incidents, key=lambda x: x['severity'], reverse=True)[0]
        requests.post(f"{API_URL}/dispatch", json={"incident_id": top['id'], "unit_type": ready_units[0]})
    else:
        # Standard environment heartbeat
        requests.post(f"{API_URL}/dispatch", json={"incident_id": 0, "unit_type": "none"})
    time.sleep(speed)
    st.rerun()
else:
    # Manual mode keeps the clock pulsing without actions
    time.sleep(speed)
    st.rerun()