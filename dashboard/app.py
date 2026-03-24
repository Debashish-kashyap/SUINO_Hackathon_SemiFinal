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

/* Sidebar — always visible, cannot be collapsed */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141414 0%, #0a0a0a 100%);
    border-right: 1px solid #222;
    z-index: 999 !important;
    padding-top: 20px !important;
    transform: none !important;
    width: 336px !important;
    min-width: 336px !important;
    visibility: visible !important;
    display: flex !important;
    opacity: 1 !important;
}
/* Hide the collapse (X) button inside sidebar */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Native Streamlit Header — keep visible but transparent ── */
[data-testid="stHeader"] {
    background-color: transparent !important;
    border-bottom: none !important;
    box-shadow: none !important;
}

/* Hide the deploy/hamburger menu */
[data-testid="stToolbar"] {
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
""", unsafe_allow_html=True)


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

    age              = st.slider("Age", 16, 70, 24)
    gender           = st.selectbox("Gender", ["Male", "Female", "Other"])
    account_age      = st.slider("Account Age (months)", 0, 120, 3)
    sub_type         = st.selectbox("Subscription", ["Basic", "Standard", "Premium", "Mobile"])
    monthly_fee      = st.number_input("Monthly Fee (₹)", 49, 799, 199)
    payment          = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"])

    st.markdown("---")
    region           = st.selectbox("Region Type", ["Tier-1", "Tier-2", "Tier-3"])
    city             = st.selectbox("City", ["Mumbai", "Delhi", "Bangalore", "Chennai",
                                              "Guwahati", "Pune", "Jaipur", "Lucknow",
                                              "Dibrugarh", "Silchar", "Tezpur", "Jorhat"])
    language         = st.selectbox("Language", ["Hindi", "Assamese", "Tamil", "Kannada", "Marathi", "English"])

    st.markdown("---")
    device           = st.selectbox("Primary Device", ["Mobile", "Tablet", "Laptop", "Smart TV", "Desktop"])
    devices_used     = st.slider("Devices Used", 1, 5, 1)
    genre            = st.selectbox("Favourite Genre", ["Drama", "Action", "Comedy", "Horror", "Romance", "Sci-Fi", "Thriller", "Documentary"])
    avg_watch        = st.slider("Avg Watch Time (min/session)", 0, 180, 25)
    sessions_pw      = st.slider("Watch Sessions / Week", 0, 30, 4)
    binge            = st.slider("Binge Sessions", 0, 20, 1)
    completion       = st.slider("Completion Rate", 0.0, 1.0, 0.5, 0.05)
    rating           = st.slider("Rating Given", 0.0, 5.0, 3.5, 0.5)
    interactions     = st.slider("Content Interactions", 0, 100, 8)
    click_rate       = st.slider("Recommendation Click Rate", 0.0, 1.0, 0.3, 0.05)
    days_login       = st.slider("Days Since Last Login", 0, 60, 15)
    churned_before   = st.selectbox("Churned Before?", [0, 1], format_func=lambda x: "Yes" if x else "No")

    predict_btn = st.button("🔍 Analyse User", use_container_width=True)



tab1, tab2, tab3 = st.tabs(["🛡️ Churn Shield AI", "🗺️ Regional Intelligence", "📊 Growth Dashboard"])


with tab1:
    if predict_btn:
        payload = {
            "age": age, "gender": gender,
            "account_age_months": account_age,
            "subscription_type": sub_type,
            "monthly_fee": monthly_fee,
            "payment_method": payment,
            "primary_device": device,
            "devices_used": devices_used,
            "favorite_genre": genre,
            "avg_watch_time_minutes": float(avg_watch),
            "watch_sessions_per_week": float(sessions_pw),
            "binge_watch_sessions": binge,
            "completion_rate": completion,
            "rating_given": rating,
            "content_interactions": interactions,
            "recommendation_click_rate": click_rate,
            "days_since_last_login": days_login,
            "churned": churned_before,
            "region_type": region,
            "city": city,
            "language": language,
        }

        with st.spinner("Running Churn Shield AI..."):
            result = api("POST", "/predict", json=payload)

        if result:
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
                retain_payload = {
                    "user_id": f"USR_{city[:3].upper()}_{age}",
                    "language": language,
                    "region_type": region,
                    "churn_prob": prob,
                }
                with st.spinner("Dispatching retention nudge..."):
                    time.sleep(1)
                    r2 = api("POST", "/retain", json=retain_payload)

                if r2 and r2.get("action") != "none":
                    st.success(f"✅ Retention nudge sent! Offer: **{r2['offer']}**")
                    st.markdown(f"""
                    <div class='wa-box'>
                    📱 <b>WhatsApp Message Preview</b><br><br>
                    {r2['message_preview']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"Channel: {r2['channel']} · {r2['timestamp']}")
                elif r2:
                    st.info("ℹ️ User risk is LOW — no retention action required.")

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

            cols = st.columns(len(result["content"]))
            for i, item in enumerate(result["content"]):
                with cols[i]:
                    st.markdown(f"""
                    <div class='metric-card' style='text-align:left;'>
                        <div style='font-size:1.4rem;margin-bottom:6px'>🎬</div>
                        <div style='font-family:Bebas Neue;font-size:1.2rem;color:#fff;letter-spacing:1px'>{item['title']}</div>
                        <div style='color:#888;font-size:0.8rem;margin:4px 0'>{item['genre']} · ⭐ {item['score']}</div>
                        <div style='color:#e50914;font-size:0.75rem'>{'📱 Mobile Optimised' if item['mobile_optimised'] else '🖥️ All Devices'}</div>
                       <div style='color:#666;font-size:0.72rem;margin-top:6px'>{item.get('why', 'AI recommended for you')}</div>
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