import streamlit as st
import requests, plotly.graph_objects as go, plotly.express as px, time

API_URL = "http://127.0.0.1:7860"
st.set_page_config(page_title="TITAN COMMAND | v21", layout="wide")

# --- 🎨 DARK SCI-FI CSS ---
st.markdown("<style>.stApp { background-color: #050b14; color: #e0e0e0; } [data-testid='stMetricValue'] { color: #00f2ff !important; text-shadow: 0 0 10px #00f2ff; }</style>", unsafe_allow_html=True)

try:
    data = requests.get(f"{API_URL}/status", timeout=1).json()
except:
    st.error("🔴 NEURAL LINK SEVERED. START BACKEND FIRST."); st.stop()

# --- 🏆 FINAL EVALUATION ---
if data.get('is_done'):
    st.balloons()
    surv, integ = data.get('lives_saved', 0), data.get('integrity', 0)
    grade = "A+ (LEGENDARY)" if surv > 5000 and integ > 80 else "B (VETERAN)" if surv > 2000 else "F (COLLAPSE)"
    st.markdown(f"<h1 style='text-align:center;'>GRADE: {grade}</h1>", unsafe_allow_html=True)
    if st.button("REDEPLOY FLEET", use_container_width=True, type="primary"):
        requests.post(f"{API_URL}/reset"); st.rerun()
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🎖️ FLEET STATUS")
for u, l in data['unit_levels'].items():
    cd = data['cooldowns'].get(u, 0)
    st.sidebar.write(f"**{u.upper()}** (Lvl {l}) {'✅ READY' if cd==0 else f'⏳({cd}s)'}")
    st.sidebar.progress(min(data['unit_xp'].get(u, 0) / (l * 30), 1.0))

auto = st.sidebar.toggle("ENABLE AUTO-PILOT")
speed = st.sidebar.slider("HEARTBEAT SPEED", 0.5, 5.0, 1.5)

# --- HUD METRICS ---
h = data.get('history', {})
drain = h['drain'][-1] if h.get('drain') else 150
st.markdown("## 🛰️ TITAN_COMMAND // MASTER_COMMAND_CENTER")
c1, c2, c3, c4 = st.columns(4)
c1.metric("TREASURY", f"${data['budget']:,}", f"-${drain}")
c2.metric("SAVED", f"{data['lives_saved']:,}")
c3.metric("INTEGRITY", f"{data['integrity']:.1f}%")
c4.metric("STEP", f"{data['steps_taken']}/100")

# --- DISPATCH COMMANDS ---
st.divider()
st.write("### 🕹️ TACTICAL DISPATCH CENTER")
if not data['incidents']: st.info("Scanning for threats...")
else:
    for inc in data['incidents']:
        col_i, col_u = st.columns([1, 2])
        col_i.write(f"**{inc['type'].upper()}** (Sev: {inc['severity']:.1f})")
        u1, u2, u3 = col_u.columns(3)
        if u1.button("🚁 HELI", key=f"h_{inc['id']}", disabled=not data['unit_ready']['helicopter']):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "helicopter"}); st.rerun()
        if u2.button("🚒 FIRE", key=f"f_{inc['id']}", disabled=not data['unit_ready']['fire_truck']):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "fire_truck"}); st.rerun()
        if u3.button("🚑 AMBU", key=f"a_{inc['id']}", disabled=not data['unit_ready']['ambulance']):
            requests.post(f"{API_URL}/dispatch", json={"incident_id": inc['id'], "unit_type": "ambulance"}); st.rerun()

# --- ANALYTICS ROW ---
st.divider()
col_an, col_map = st.columns([1, 2])
with col_an:
    st.write("#### 📊 FLEET MIX & RECOVERIES")
    fleet = data.get('fleet_usage', {})
    if any(fleet.values()):
        st.plotly_chart(px.pie(values=list(fleet.values()), names=list(fleet.keys()), hole=0.5).update_layout(height=220, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color="white"))
    
    rec = data.get('recovery_types', {})
    if any(rec.values()):
        st.plotly_chart(px.bar(x=list(rec.keys()), y=list(rec.values()), color=list(rec.keys())).update_layout(height=220, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_color="white"))

with col_map:
    st.write("#### 📡 THREAT MATRIX")
    fig_3d = go.Figure()
    for inc in data['incidents']:
        fig_3d.add_trace(go.Scatter3d(x=[inc['x']], y=[inc['y']], z=[inc['severity']], mode='markers', marker=dict(size=10, color='red')))
    for p in data.get('predictions', []):
        fig_3d.add_trace(go.Scatter3d(x=[p['x']], y=[p['y']], z=[0.5], mode='markers+text', text=[f"T-{p['steps']}"], marker=dict(size=12, color='yellow', opacity=0.3, symbol='diamond')))
    fig_3d.update_layout(height=450, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', scene_xaxis_visible=False)
    st.plotly_chart(fig_3d, use_container_width=True)

# --- FINANCIAL FORENSICS ---
st.divider()
st.write("#### 📉 THE DEATH SPIRAL: INTEGRITY vs. DRAIN")
if len(h.get('steps', [])) > 1:
    fig_spiral = go.Figure()
    fig_spiral.add_trace(go.Scatter(x=h['steps'], y=h['integrity'], name="Integrity (%)", line=dict(color='#00f2ff', width=3)))
    fig_spiral.add_trace(go.Scatter(x=h['steps'], y=h['drain'], name="Drain ($)", yaxis="y2", line=dict(color='#ff4b4b', dash='dot')))
    fig_spiral.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", yaxis=dict(title="Integrity (%)"), yaxis2=dict(title="Drain ($)", overlaying="y", side="right"))
    st.plotly_chart(fig_spiral, use_container_width=True)

# --- HEARTBEAT ---
if auto:
    ready = [u for u, r in data['unit_ready'].items() if r]
    if data['incidents'] and ready:
        top = sorted(data['incidents'], key=lambda x: x['severity'], reverse=True)[0]
        requests.post(f"{API_URL}/dispatch", json={"incident_id": top['id'], "unit_type": ready[0]})
    else: requests.post(f"{API_URL}/dispatch", json={"incident_id": 0, "unit_type": "none"})
    time.sleep(speed); st.rerun()
else:
    time.sleep(speed); st.rerun() # Manual mode doesn't pulse clock automatically