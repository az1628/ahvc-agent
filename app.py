import streamlit as st
import anthropic
from datetime import datetime

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="HVAC Sentinel | Dark Mode",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === DARK MODE CSS (VISIBILITY FIX) ===
st.markdown("""
<style>
    /* 1. Main Background - Dark Slate */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* 2. Text Visibility Fixes */
    p, h1, h2, h3, li, span, div {
        color: #e0e0e0 !important;
    }
    
    /* 3. Header - Deep Navy */
    .app-header {
        background-color: #1a1c24;
        padding: 20px;
        margin: -60px -60px 20px -60px;
        border-bottom: 2px solid #4a90e2;
        text-align: center;
    }
    .header-title {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: 1px;
        margin: 0;
    }
    .header-sub {
        font-size: 12px;
        color: #4a90e2 !important;
        margin-top: 5px;
    }

    /* 4. Cards/Boxes - Lighter Dark Grey */
    .info-card {
        background-color: #262730;
        border: 1px solid #363945;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    /* 5. Inputs & Dropdowns (Dark Backgrounds) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] div {
        background-color: #1a1c24 !important;
        color: white !important;
        border: 1px solid #4a4a4a;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #4a90e2 !important;
        font-weight: bold;
    }

    /* 6. Buttons - Neon Blue Accent */
    .stButton > button {
        width: 100%;
        background-color: #4a90e2;
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        height: 50px;
    }
    .stButton > button:hover {
        background-color: #357abd;
    }

    /* 7. Results Box */
    .result-box {
        background-color: #1c2e4a; /* Navy Tint */
        border-left: 5px solid #4a90e2;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
    
    /* 8. Safety Badges */
    .badge-safe {
        background-color: #1b5e20;
        color: #a5d6a7 !important;
        padding: 8px;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #2e7d32;
    }

    /* Hide Streamlit Junk */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# === DATA ENGINE ===
HVAC_DATABASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": {
            "specs": "7-15kW Monobloc Heat Pump.",
            "faults": "F.022: Low pressure. F.729: Compressor cold start. F.718: Fan blocked.",
            "safety": "R290 FLAMMABLE Refrigerant. 1m Safety Zone Mandatory."
        },
        "ecoTEC plus": {
            "specs": "Gas Combi Boiler.",
            "faults": "F.28: Ignition Failure. F.75: Pump/Pressure Sensor. F.22: Dry Fire.",
            "safety": "Gas Safe Regs apply. CO check required."
        }
    },
    "Mitsubishi Electric": {
        "Ecodan R290": {
            "specs": "Air Source Heat Pump.",
            "faults": "U1: High Pressure. L9: Flow Rate Low. P6: Overheat.",
            "safety": "High Voltage & Flammable Gas Risk."
        }
    },
    "Daikin": {
        "Altherma 3 H HT": {
            "specs": "High Temp Heat Pump.",
            "faults": "A5: HP Control. E7: Fan Motor. U0: Low Gas.",
            "safety": "R32 Mildly Flammable. F-Gas Cat 1 required."
        }
    },
    "Commercial Fridge": {
        "Williams Multideck": {
            "specs": "Commercial Display Fridge.",
            "faults": "HI: High Temp. CL: Clean Condenser. E1: Probe Fail.",
            "safety": "Food Safety Danger Zone >8°C."
        }
    }
}

def main():
    # --- DARK HEADER ---
    st.markdown("""
        <div class="app-header">
            <div class="header-title">HVAC SENTINEL</div>
            <div class="header-sub">PRO AUDIT | DARK MODE</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 1. LOGIN ---
    if "verified" not in st.session_state:
        st.session_state.verified = False

    if not st.session_state.verified:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("🔐 Engineer Login")
        key = st.text_input("License Key", type="password")
        st.caption("Try Key: `PRO2026`")
        if st.button("Unlock System"):
            if key == "PRO2026":
                st.session_state.verified = True
                st.rerun()
            else:
                st.error("Invalid Key")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --- 2. SAFETY CHECK ---
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Safety Interlock")
    c1, c2, c3 = st.columns(3)
    with c1: ppe = st.checkbox("PPE OK")
    with c2: loto = st.checkbox("LOTO OK")
    with c3: risk = st.checkbox("Risk Check")

    if not (ppe and loto and risk):
        st.warning("⚠️ Complete checks to enable tool")
        st.stop()
    else:
        st.markdown('<div class="badge-safe">SITE SECURE - ACTIVE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. DIAGNOSTIC TOOL ---
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📍 Fault Diagnosis")

    # Dynamic Dropdowns
    col_brand, col_model = st.columns(2)
    with col_brand:
        brand_list = ["Select Brand..."] + sorted(list(HVAC_DATABASE.keys()))
        brand = st.selectbox("Manufacturer", brand_list)
    
    selected_unit = ""
    context = {}
    
    with col_model:
        if brand != "Select Brand...":
            model_list = sorted(list(HVAC_DATABASE[brand].keys()))
            model = st.selectbox("Model", model_list)
            if model:
                selected_unit = f"{brand} {model}"
                context = HVAC_DATABASE[brand][model]
        else:
            st.selectbox("Model", ["Select Brand First"], disabled=True)
            
    # Manual Entry Fallback
    if brand == "Select Brand...":
        st.markdown("---")
        manual_unit = st.text_input("Or Enter Custom Unit Name")
        if manual_unit:
            selected_unit = f"Custom: {manual_unit}"
            context = {"faults": "Standard Engineering Principles"}

    # Fault Input
    st.markdown("---")
    fault = st.text_area("Fault / Error Code", placeholder="e.g. F.22, Low Pressure, Leaking...")
    
    if st.button("🚀 ANALYZE & GENERATE SOP"):
        if not selected_unit or not fault:
            st.error("Missing Unit or Fault info")
        else:
            if not st.secrets.get("ANTHROPIC_API_KEY"):
                st.error("API Key Missing")
                return
                
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            with st.spinner("AI analyzing technical manuals..."):
                prompt = f"""
                Role: Senior UK HVAC Tech.
                Unit: {selected_unit}
                Data: {context}
                Fault: {fault}
                
                Provide a short, professional field guide.
                Structure:
                1. DIAGNOSIS (What is wrong)
                2. STEP-BY-STEP REPAIR (5 steps max)
                3. PARTS REQUIRED
                4. SAFETY WARNING
                """
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=600,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.subheader("📋 Solution Found")
                st.markdown(response.content[0].text)
                st.markdown("---")
                
                # Audit Log Button
                log_content = f"AUDIT LOG\nUnit: {selected_unit}\nFault: {fault}\nSolution: {response.content[0].text}"
                st.download_button("💾 Save Audit Log", log_content, file_name="Audit_Log.txt")
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
