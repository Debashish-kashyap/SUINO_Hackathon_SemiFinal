import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(
    page_title="Netflix NEXUS AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND = "http://127.0.0.1:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0a;
    color: #e5e5e5;
}

/* Main background */
.stApp { background-color: #0a0a0a; }

/* Sidebar — base styling (all screen sizes) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141414 0%, #0a0a0a 100%);
    border-right: 1px solid #222;
    z-index: 999999 !important; /* Extremely high z-index to stay above mobile overlay and custom headers */
    padding-top: 20px !important;
}

/* Desktop only — force sidebar always visible */
@media (min-width: 769px) {
    [data-testid="stSidebar"] {
        transform: none !important;
        width: 336px !important;
        min-width: 336px !important;
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
    }
    /* Hide the collapse (X) button on desktop */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
}

/* ── Native Streamlit Header — keep visible but transparent ── */
[data-testid="stHeader"] {
    background-color: transparent !important;
    border-bottom: none !important;
    box-shadow: none !important;
}

/*
 * Do NOT hide [data-testid="stToolbar"] on narrow screens: Streamlit places the
 * sidebar expand/collapse control in the header toolbar on mobile. Hiding the
 * whole toolbar removes the only way to open the sidebar.
 * Hide the toolbar only on desktop (sidebar is forced open there via CSS below).
 */
@media (min-width: 769px) {
    [data-testid="stToolbar"] {
        display: none !important;
    }
}

/* Hide the "Deploy" chip without removing toolbar (sidebar toggle stays available on mobile). */
.stAppDeployButton,
.stDeployButton {
    display: none !important;
}

/* ── Custom Branding Banner (inline, not fixed) ── */
.nexus-header {
    background: rgba(140, 5, 12, 0.55);
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border-bottom: 1px solid rgba(229, 9, 20, 0.3);
    box-shadow: 0 4px 30px rgba(0,0,0,0.6);
    padding: 18px 36px;
    margin: -1rem -1rem 1rem -1rem;
    position: relative;
    overflow: hidden;
}
.nexus-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.nexus-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 4px;
    color: #ffffff;
    margin: 0;
    line-height: 1;
}
.nexus-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Push content slightly for spacing */
.block-container {
    padding-top: 1rem !important;
}
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Metric cards */
.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #e50914; }
.metric-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #e50914;
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* Risk badge */
.risk-high   { background:#e50914; color:#fff; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.9rem; }
.risk-medium { background:#f5a623; color:#000; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.9rem; }
.risk-low    { background:#2ecc71; color:#000; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.9rem; }

/* Movie Poster Cards */
.poster-card {
    position: relative;
    border-radius: 6px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
    background: #0a0a0a;
    border: 1px solid #222;
    aspect-ratio: 2/3;
    display: flex;
    flex-direction: column;
    margin-bottom: 12px;
}
.poster-card:hover {
    transform: scale(1.05); /* Netflix hover scale */
    box-shadow: 0 10px 20px rgba(0,0,0,0.8);
    z-index: 10;
    border-color: #e50914;
}
.poster-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: filter 0.3s ease;
}
.poster-card:hover .poster-img {
    filter: brightness(0.4) blur(1px);
}
.poster-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(0deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.6) 50%, transparent 100%);
    padding: 16px 12px 12px;
}
.poster-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.25rem;
    color: #fff;
    letter-spacing: 1px;
    line-height: 1.1;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}
.poster-info-hover {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease, opacity 0.4s ease;
    opacity: 0;
}
.poster-card:hover .poster-info-hover {
    max-height: 150px;
    opacity: 1;
    margin-top: 8px;
}
.poster-info {
    font-size: 0.75rem;
    color: #ccc;
    margin-bottom: 6px;
}
.poster-badge {
    display: inline-block;
    background: #e50914;
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: bold;
    margin-bottom: 6px;
}
.poster-why {
    font-size: 0.7rem;
    color: #aaa;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Section titles */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 3px;
    color: #e50914;
    border-left: 4px solid #e50914;
    padding-left: 12px;
    margin: 24px 0 16px;
}

/* Retain button */
.stButton > button {
    background: linear-gradient(135deg, #e50914, #b20710) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 10px 28px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Input labels */
label { color: #ccc !important; font-size: 0.82rem !important; }

/* Divider */
hr { border-color: #222 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #e50914; border-radius: 3px; }

/* WhatsApp message box */
.wa-box {
    background: #1a1a2e;
    border: 1px solid #e50914;
    border-radius: 12px;
    padding: 20px;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #e5e5e5;
    margin-top: 12px;
}

/* ═══════════════════════════════════════════
   MOBILE RESPONSIVE — Tablet (≤768px)
   ═══════════════════════════════════════════ */
@media (max-width: 768px) {

    /* Sidebar narrower on mobile */
    [data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 240px !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.6) !important;
    }
    /* Sidebar toggle button styling is managed in the inline CSS below the header */

    /* Main content takes full width */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.5rem !important;
        max-width: 100% !important;
    }
    [data-testid="stAppViewBlockContainer"] {
        max-width: 100% !important;
    }

    /* Scale down header */
    .nexus-header {
        padding: 14px 18px;
        margin: -1rem -1rem 0.75rem -1rem;
    }
    .nexus-title { font-size: 1.25rem; letter-spacing: 2px; }
    .nexus-sub   { font-size: 0.62rem; letter-spacing: 1px; }

    /* Smaller section titles */
    .section-title {
        font-size: 1.2rem;
        letter-spacing: 2px;
        margin: 16px 0 10px;
    }

    /* Metric cards — smaller on tablet */
    .metric-card { padding: 14px 16px; }
    .metric-value { font-size: 1.8rem; }
    .metric-label { font-size: 0.68rem; letter-spacing: 1px; }

    /* Stack Streamlit columns vertically */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
    }

    /* Tabs — smaller font */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.78rem !important;
        padding: 8px 10px !important;
    }
}

/* ═══════════════════════════════════════════
   MOBILE RESPONSIVE — Small phone (≤480px)
   ═══════════════════════════════════════════ */
@media (max-width: 480px) {

    [data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 200px !important;
    }

    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    .nexus-header { padding: 10px 12px; }
    .nexus-title  { font-size: 1.05rem; letter-spacing: 1.5px; }
    .nexus-sub    { font-size: 0.55rem; letter-spacing: 0.5px; }

    .section-title {
        font-size: 1rem;
        letter-spacing: 1.5px;
        padding-left: 8px;
        margin: 12px 0 8px;
    }

    .metric-card { padding: 10px 12px; border-radius: 8px; }
    .metric-value { font-size: 1.5rem; }
    .metric-label { font-size: 0.62rem; }

    .risk-high, .risk-medium, .risk-low {
        font-size: 0.75rem;
        padding: 3px 10px;
    }

    .stButton > button {
        padding: 8px 16px !important;
        font-size: 0.82rem !important;
    }

    /* Tabs horizontally scrollable */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.7rem !important;
        padding: 6px 8px !important;
        white-space: nowrap !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="nexus-header">
    <div style="display:flex; align-items:center; gap:16px;">
        <div>
            <p class="nexus-title">🎬 NETFLIX NEXUS AI</p>
            <p class="nexus-sub">Hybrid AI Growth Engine &nbsp;·&nbsp; Churn Prediction &nbsp;·&nbsp; Regional Intelligence &nbsp;·&nbsp; Retention Automation</p>
        </div>
    </div>
</div>

<!-- Remove custom JS toggle and use pure Streamlit native buttons styled distinctly on mobile -->
<style>
@media (max-width: 768px) {
    /* Style Streamlit's native Expand button to look like our red hamburger */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 15px !important;
        right: 15px !important;
        left: auto !important;
        z-index: 999999 !important;
        background: linear-gradient(135deg, #e50914, #b20710) !important;
        border-radius: 8px !important;
        width: 44px !important;
        height: 44px !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 14px rgba(229,9,20,0.5) !important;
        cursor: pointer !important;
        transition: transform 0.2s ease !important;
    }
    
    /* Style the internal SVG of the expand button */
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #fff !important;
        width: 24px !important;
        height: 24px !important;
    }

    /* Button resets inside controls to remove default Streamlit formatting */
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button {
        color: #fff !important;
        background: transparent !important;
        border: none !important;
        width: 100% !important;
        height: 100% !important;
        padding: 0 !important;
    }

    /* Style the native Collapse (X) button inside the open sidebar */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: absolute !important;
        top: 15px !important;
        right: 15px !important;
        left: auto !important;
        z-index: 999999 !important;
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        width: 36px !important;
        height: 36px !important;
        backdrop-filter: blur(5px) !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #fff !important;
    }

    /* Keep sidebar at a good responsive width */
    [data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 260px !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.8) !important;
    }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_movie_poster(movie_title):
    import urllib.parse
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Try getting the API key from secrets, then environment variable
    try:
        api_key = st.secrets["OMDB_API_KEY"]
    except Exception:
        api_key = os.environ.get("OMDB_API_KEY", "")
        
    query = urllib.parse.quote(movie_title)
    
    if api_key:
        try:
            url = f"http://www.omdbapi.com/?t={query}&apikey={api_key}"
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            data = r.json()
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster
        except Exception:
            pass
            
    # Fallback to a placeholder image if API is missing or fails
    return f"https://placehold.co/500x750/1a1a1a/e50914.png?text={query}"

def api(method, path, **kwargs):
    try:
        fn = requests.get if method == "GET" else requests.post
        r = fn(f"{BACKEND}{path}", timeout=8, **kwargs)
        return r.json()
    except Exception as e:
        st.error(f"Backend error: {e}")
        return None

def risk_badge(risk):
    cls = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}.get(risk, "risk-low")
    return f'<span class="{cls}">{risk} Risk</span>'

def gauge_chart(prob):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 36, "color": "#e5e5e5", "family": "Bebas Neue"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#555", "tickfont": {"color": "#555"}},
            "bar": {"color": "#e50914" if prob > 0.6 else ("#f5a623" if prob > 0.35 else "#2ecc71")},
            "bgcolor": "#1a1a1a",
            "bordercolor": "#2a2a2a",
            "steps": [
                {"range": [0,  40], "color": "#0d2b1a"},
                {"range": [40, 70], "color": "#2b1e0a"},
                {"range": [70, 100],"color": "#2b0a0a"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2}, "thickness": 0.75, "value": prob * 100},
        },
        title={"text": "Churn Probability", "font": {"color": "#888", "size": 14}},
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
        font={"color": "#e5e5e5"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=220,
    )
    return fig


with st.sidebar:
    st.markdown("### 👤 User Profile Input")
    st.markdown("---")

    # ── PRIMARY FIELDS (always visible)
    age          = st.slider("Age", 16, 70, 24)
    account_age  = st.slider("Account Age (months)", 0, 120, 3)
    sub_type     = st.selectbox("Subscription", ["Basic", "Standard", "Premium", "Mobile"])
    monthly_fee  = st.number_input("Monthly Fee (₹)", 49, 799, 199)
    avg_watch    = st.slider("Avg Watch Time (min/session)", 0, 180, 25)
    sessions_pw  = st.slider("Watch Sessions / Week", 0, 30, 4)
    completion   = st.slider("Content Completion Rate", 0.0, 1.0, 0.5, 0.05)
    days_login   = st.slider("Days Since Last Login", 0, 60, 15)
    region       = st.selectbox("Region Type", ["Tier-1", "Tier-2", "Tier-3"])
    language     = st.selectbox("Language", ["Hindi", "Assamese", "Tamil", "Kannada", "Marathi", "English"])

    st.markdown("---")

    # ── SECONDARY FIELDS (collapsible)
    with st.expander("⚙️ Advanced Options (optional)"):
        gender       = st.selectbox("Gender", ["— Not specified —", "Male", "Female", "Other"])
        payment      = st.selectbox("Payment Method", ["— Not specified —", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"])
        device       = st.selectbox("Primary Device", ["— Not specified —", "Mobile", "Tablet", "Laptop", "Smart TV", "Desktop"])
        city         = st.selectbox("City", ["— Not specified —", "Mumbai", "Delhi", "Bangalore", "Chennai",
                                              "Guwahati", "Pune", "Jaipur", "Lucknow",
                                              "Dibrugarh", "Silchar", "Tezpur", "Jorhat"])
        devices_used   = st.slider("Devices Used", 0, 5, 0)
        genre          = st.selectbox("Favourite Genre", ["— Not specified —", "Drama", "Action", "Comedy", "Horror", "Romance", "Sci-Fi", "Thriller", "Documentary"])
        binge          = st.slider("Binge Sessions", 0, 20, 0)
        rating         = st.slider("Rating Given (0 = not specified)", 0.0, 5.0, 0.0, 0.5)
        interactions   = st.slider("Content Interactions (0 = not specified)", 0, 100, 0)
        click_rate     = st.slider("Recommendation Click Rate (0 = not specified)", 0.0, 1.0, 0.0, 0.05)
        churned_before = st.selectbox("Churned Before?", ["— Not specified —", "No", "Yes"])

    predict_btn = st.button("🔍 Analyse User", use_container_width=True)

    # ── RESOLVE OPTIONAL VALUES (None if not specified)
    gender_val       = None if gender == "— Not specified —" else gender
    payment_val      = None if payment == "— Not specified —" else payment
    device_val       = None if device == "— Not specified —" else device
    city_val         = None if city == "— Not specified —" else city
    genre_val        = None if genre == "— Not specified —" else genre
    devices_used_val = None if devices_used == 0 else devices_used
    binge_val        = None if binge == 0 else binge
    rating_val       = None if rating == 0.0 else rating
    interactions_val = None if interactions == 0 else interactions
    click_rate_val   = None if click_rate == 0.0 else click_rate
    churned_val      = None if churned_before == "— Not specified —" else (1 if churned_before == "Yes" else 0)



tab1, tab2, tab3 = st.tabs(["🛡️ Churn Shield AI", "🗺️ Regional Intelligence", "📊 Growth Dashboard"])


with tab1:
    if predict_btn:
        payload = {
            "age": age,
            "account_age_months": account_age,
            "subscription_type": sub_type,
            "monthly_fee": monthly_fee,
            "avg_watch_time_minutes": float(avg_watch),
            "watch_sessions_per_week": float(sessions_pw),
            "completion_rate": completion,
            "days_since_last_login": days_login,
            "region_type": region,
            "language": language,

            "gender": gender_val,
            "payment_method": payment_val,
            "primary_device": device_val,
            "city": city_val,
            "favorite_genre": genre_val,
            "devices_used": devices_used_val,
            "binge_watch_sessions": binge_val,
            "rating_given": rating_val,
            "content_interactions": interactions_val,
            "recommendation_click_rate": click_rate_val,
            "churned": churned_val,
        }

        with st.spinner("Running Churn Shield AI..."):
            result = api("POST", "/predict", json=payload)

        if result:
            st.session_state["prediction_result"] = result
            # Store sidebar values so the retain button can use them on rerun
            st.session_state["last_language"] = language
            st.session_state["last_region"] = region
            st.session_state["last_city"] = city_val
            st.session_state["last_age"] = age
            # Clear any previous retain result when a new prediction is made
            st.session_state.pop("retain_result", None)

    if "prediction_result" in st.session_state:
        result = st.session_state["prediction_result"]
        prob  = result["churn_prob"]
        risk  = result["user_risk"]
        label = result["churn_label"]
        factors = result["risk_factors"]
        rec   = result["recommendation"]

        c1, c2 = st.columns([1, 1.6])
        with c1:
            st.plotly_chart(gauge_chart(prob), use_container_width=True)
        with c2:
            st.markdown(f"<div class='section-title'>PREDICTION RESULT</div>", unsafe_allow_html=True)
            st.markdown(f"**Risk Level:** {risk_badge(risk)}", unsafe_allow_html=True)
            st.markdown(f"**Churn Probability:** `{prob*100:.1f}%`")
            st.markdown(f"**Model Decision:** {'⚠️ Will Churn' if label else '✅ Will Retain'}")
            st.markdown("---")
            st.markdown(f"💡 **AI Recommendation:** {rec}")

        st.markdown("<div class='section-title'>RISK FACTORS</div>", unsafe_allow_html=True)
        for f in factors:
            st.markdown(f"🔴 {f}")

        st.markdown("<div class='section-title'>RETENTION ACTION</div>", unsafe_allow_html=True)

        retain_btn = st.button("📲 Trigger WhatsApp Retention Nudge", use_container_width=True)

        if retain_btn:
            # Use stored sidebar values from session_state so they survive rerun
            stored_city = st.session_state.get("last_city", None)
            stored_language = st.session_state.get("last_language", language)
            stored_region = st.session_state.get("last_region", region)
            stored_age = st.session_state.get("last_age", age)

            retain_payload = {
                "user_id": f"USR_{stored_city[:3].upper() if stored_city else 'GEN'}_{stored_age}",
                "language": stored_language,
                "region_type": stored_region,
                "churn_prob": prob,
            }

            with st.spinner("📡 Sending WhatsApp message..."):
                time.sleep(1)
                r2 = api("POST", "/retain", json=retain_payload)
            if r2:
                st.session_state["retain_result"] = r2    

        if "retain_result" in st.session_state:
            r2 = st.session_state["retain_result"]

            if r2.get("action") == "none":
                st.info("ℹ️ User risk is LOW — no retention action required.")
            else:
                user_id = r2.get("user_id", "Unknown")
                offer = r2.get("offer", "Special Offer")
                msg = r2.get("message_preview", "")
                channel = r2.get("channel", "")
                ts = r2.get("timestamp", "")

                st.markdown(
                    f'<div style="background:#ECE5DD;border-radius:14px;'
                    f'padding:0;max-width:540px;margin-top:14px;border:1px solid #d1ccc0;overflow:hidden;">'
                    f'<div style="background:#075E54;padding:14px 20px;display:flex;align-items:center;gap:10px;">'
                    f'<span style="font-size:1.3rem;">📲</span>'
                    f'<span style="color:#fff;font-weight:700;font-size:1.05rem;letter-spacing:0.5px;">WhatsApp Message Sent</span>'
                    f'</div>'
                    f'<div style="padding:18px 20px;">'
                    f'<div style="color:#555;font-size:0.78rem;margin-bottom:12px;">To: <span style="color:#075E54;font-weight:700;">{user_id}</span> &nbsp;·&nbsp; Offer: <span style="color:#075E54;font-weight:700;">{offer}</span></div>'
                    f'<div style="background:#DCF8C6;border-radius:8px;padding:12px 14px;color:#303030;font-size:0.92rem;line-height:1.65;box-shadow:0 1px 2px rgba(0,0,0,0.1);">'
                    f'{msg}'
                    f'<div style="text-align:right;margin-top:8px;color:#6b9b7d;font-size:0.72rem;">✓✓ Delivered &nbsp;·&nbsp; {ts}</div>'
                    f'</div>'
                    f'<div style="color:#999;font-size:0.72rem;margin-top:10px;">📡 {channel}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    else:
        st.markdown("<div class='section-title'>HOW IT WORKS</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            **1. Input User Profile**
            Fill in the sidebar with user demographics, subscription info, and viewing behavior.
            """)
        with c2:
            st.markdown("""
            **2. Run Churn Shield AI**
            RandomForest model trained on Indian Netflix user data predicts churn probability.
            """)
        with c3:
            st.markdown("""
            **3. Trigger Retention**
            High-risk users get an instant personalised WhatsApp nudge with a tier-specific offer.
            """)
        st.info("👈 Fill in the sidebar and click **Analyse User** to get started.")


with tab2:
    st.markdown("<div class='section-title'>HYPER-LOCAL CONTENT RECOMMENDATIONS</div>", unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        r_lang   = st.selectbox("Language", ["Assamese", "Hindi", "Tamil", "Kannada", "Marathi", "English"], key="r_lang")
    with rc2:
        r_region = st.selectbox("Region", ["Tier-1", "Tier-2", "Tier-3"], key="r_region")
    with rc3:
        r_genre  = st.selectbox("Genre (optional)", ["", "Drama", "Action", "Comedy", "Thriller", "Romance", "Sci-Fi"], key="r_genre")

    if st.button("🎯 Get Regional Recommendations"):
        payload = {"language": r_lang, "region_type": r_region}
        if r_genre:
            payload["genre_pref"] = r_genre

        with st.spinner("Regional AI scanning content graph..."):
            result = api("POST", "/recommend", json=payload)

        if result:
            st.success(f"📍 Showing top picks for **{r_lang}** speakers in **{r_region}** cities")
            st.caption(f"🤖 {result['ai_note']}")

            items = result.get("content", [])

            if len(items) == 0:
                st.warning("⚠️ No recommendations found")
            else:
                cols = st.columns(min(len(items), 5))  # max 5 cards

                for i, item in enumerate(items[:5]):
                    with cols[i]:
                        poster_url = get_movie_poster(item['title'])
                        st.markdown(f"""
                        <div class='poster-card'>
                            <img src='{poster_url}' class='poster-img' alt='{item['title']}'>
                            <div class='poster-overlay'>
                                <div class='poster-title'>{item['title']}</div>
                                <div class='poster-info-hover'>
                                    <div class='poster-info'>
                                        {item['genre']} · ⭐ {item['score']}
                                    </div>
                                    <div>
                                        <span class='poster-badge'>{'📱 Mobile Optimised' if item['mobile_optimised'] else '🖥️ All Devices'}</span>
                                    </div>
                                    <div class='poster-why'>
                                        {item.get('why', 'AI recommended for you')}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-title'>INDIA CONTENT REACH MAP</div>", unsafe_allow_html=True)

    map_data = pd.DataFrame({
        "city":      ["Mumbai", "Delhi", "Bangalore", "Chennai", "Guwahati", "Pune", "Jaipur", "Lucknow", "Dibrugarh", "Silchar"],
        "lat":       [19.076, 28.613, 12.972, 13.082, 26.144, 18.520, 26.912, 26.850, 27.469, 24.832],
        "lon":       [72.877, 77.209, 77.595, 80.270, 91.736, 73.856, 75.788, 80.946, 95.015, 92.797],
        "churn_rate":[0.12,  0.18,   0.15,   0.20,   0.35,   0.22,   0.40,   0.38,   0.55,   0.48],
        "tier":      ["Tier-1","Tier-1","Tier-1","Tier-1","Tier-2","Tier-2","Tier-2","Tier-2","Tier-3","Tier-3"],
    })

    fig = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", size="churn_rate",
        color="churn_rate", color_continuous_scale=["#2ecc71","#f5a623","#e50914"],
        hover_name="city", hover_data={"tier": True, "churn_rate": ":.0%"},
        size_max=35, zoom=4, mapbox_style="carto-darkmatter",
        labels={"churn_rate": "Churn Rate"},
    )
    fig.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font_color="#e5e5e5", height=420,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="Churn Rate", tickformat=".0%", tickfont=dict(color="#888")),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔴 Larger = higher churn risk · Tier-3 cities show highest churn rates")


with tab3:
    with st.spinner("Loading growth metrics..."):
        data = api("GET", "/dashboard")

    if data:
        st.markdown("<div class='section-title'>PLATFORM OVERVIEW</div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        kpis = [
            (data["total_users"], "Total Users"),
            (data["high_risk_users"], "High Risk Users"),
            (data["retentions_triggered"], "Retentions Triggered"),
            (f"{data['churn_rate_overall']:.0%}", "Overall Churn Rate"),
        ]
        for col, (val, label) in zip([k1,k2,k3,k4], kpis):
            with col:
                display_val = f"{val:,}" if isinstance(val, int) else val
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{display_val}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown("<div class='section-title'>PLAN DISTRIBUTION</div>", unsafe_allow_html=True)
            plan_df = pd.DataFrame(list(data["plan_distribution"].items()), columns=["Plan","Share"])
            fig = px.pie(plan_df, names="Plan", values="Share",
                         color_discrete_sequence=["#e50914","#f5a623","#2ecc71","#3498db"],
                         hole=0.5)
            fig.update_layout(paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
                              font_color="#e5e5e5", height=300,
                              margin=dict(l=10,r=10,t=10,b=10),
                              legend=dict(font=dict(color="#888")))
            fig.update_traces(textfont_color="#fff")
            st.plotly_chart(fig, use_container_width=True)

        with ch2:
            st.markdown("<div class='section-title'>LANGUAGE DISTRIBUTION</div>", unsafe_allow_html=True)
            lang_df = pd.DataFrame(list(data["language_distribution"].items()), columns=["Language","Share"])
            lang_df = lang_df.sort_values("Share", ascending=True)
            fig = px.bar(lang_df, x="Share", y="Language", orientation="h",
                         color="Share", color_continuous_scale=["#7a0008","#e50914"],
                         text=lang_df["Share"].apply(lambda x: f"{x:.0%}"))
            fig.update_layout(paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
                              font_color="#e5e5e5", height=300,
                              margin=dict(l=10,r=10,t=10,b=10),
                              coloraxis_showscale=False,
                              xaxis=dict(tickformat=".0%", gridcolor="#222"),
                              yaxis=dict(gridcolor="#222"))
            fig.update_traces(textfont_color="#fff", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='section-title'>REGIONAL PERFORMANCE HEATMAP</div>", unsafe_allow_html=True)
        heat = data["regional_heatmap"]
        heat_df = pd.DataFrame([
            {"City": city, "Churn Rate": f"{v['churn_rate']:.0%}",
             "Avg Watch Hrs": v["avg_watch_hrs"], "Top Language": v["top_language"]}
            for city, v in heat.items()
        ])
        st.dataframe(
            heat_df.style.applymap(
                lambda v: "color: #e50914; font-weight:bold" if "%" in str(v) and float(str(v).strip("%"))/100 > 0.4
                else ("color: #f5a623" if "%" in str(v) else ""),
                subset=["Churn Rate"]
            ),
            use_container_width=True, hide_index=True,
        )

        st.caption(f"Last updated: {data['last_updated']} · Top churn segment: {data['top_churn_segment']}")