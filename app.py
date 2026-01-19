import streamlit as st
import anthropic
from datetime import datetime

# --- 1. CORPORATE MOBILE CONFIG ---
st.set_page_config(page_title="HVAC Sentinel Mobile", page_icon="📱", layout="centered")

# MOBILE-FIRST CSS
st.markdown("""
    <style>
    /* Global Clean Look */
    .stApp { background-color: #f0f2f6; }
    
    /* Corporate Header */
    .mobile-header {
        background-color: #003366;
        padding: 20px;
        border-radius: 0px 0px 15px 15px;
        color: white;
        text-align: center;
        margin-top: -50px; /* Pulls it to the top */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Full Width 'Thumb-Friendly' Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #003366; 
        color: white;
        font-weight: 600;
        border: none;
    }
    .stButton>button:active { background-color: #002244; }
    
    /* Cards */
    .app-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
    }
    
    /* Status Badges */
    .badge-safe { background-color: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-warn { background-color: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER DATA (Same Robust Data) ---
KNOWLEDGE_BASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": "F.022: Low water (<0.6 bar). F.718: Fan blocked. F.729: Compressor outlet <0C. R290 SAFETY: Flammable. 1m Boundary.",
        "ecoTEC plus": "F.22: Dry fire. F.28: Ignition fail. F.75: Pump sensor fault. F.29: Flame loss.",
        "flexoTHERM": "701: Brine flow error. 702: Ground source sensor fault."
    },
    "Mitsubishi Electric": {
        "Ecodan R290": "U1: High pressure/flow. L9: Flow rate drop. P6: Overheat. F3: LP switch failure.",
        "City Multi VRF": "4115: Discharge temp. 1500: Ref overcharge. 1102: Discharge temp thermistor."
    },
    "Worcester Bosch": {
        "Greenstar 4000": "EA: Ignition fault. E9: Overheat. C6: Fan speed. A1: Pump stuck.",
        "GB162 Commercial": "227: Ignition fail. 216: Fan too slow. 224: Overheat >105C."
    },
    "Daikin": {
        "Altherma 3 H HT": "A5: HP Control. E3: HP Switch. U0: Low Gas. E7: Fan motor lock.",
        "VAM Units": "A9: EEV fault. C4: Liquid pipe thermistor error."
    },
    "Baxi / Potterton": {
        "600/800 Combi": "E119: Low pressure. E133: Gas supply ignition. E110: Overheat.",
        "Assure Commercial": "E01: No flame. E03: Fan fault."
    },
    "Ideal": {
        "Logic / Vogue": "F1: Low Pressure. F2: Flame Loss. L2: Ignition. F3: Fan fault.",
        "Evomax 2": "L1: No flow. L2: Ignition lockout. FU: Delta-T >50C."
    },
    "Samsung": {
        "EHS Mono HT Quiet": "E911: Low flow. E101: Comms error. E912: Flow switch error."
    },
    "Viessmann": {
        "Vitodens 100/200": "F2: Burner overheat. F4: No flame. F9: Fan speed low."
    },
    "Commercial Fridge": {
        "Williams Multideck": "HI: High Temp. CL: Clean Condenser. E1: Air probe fail. E16: HP Alarm.",
        "Foster EcoShow": "hc: High Condenser. hP: High Pressure. dEF: Defrost active.",
        "Adande Drawers": "rPF: Probe fail. HA: High temp. do: Door open."
    }
}

def main():
    # --- MOBILE HEADER ---
    st.markdown("""
        <div class="mobile-header">
            <h2 style='margin:0; font-size: 20px;'>HVAC SENTINEL <span style="opacity:0.8">MOBILE</span></h2>
            <div style='font-size: 12px; margin-top: 5px; opacity: 0.8;'>Site Compliance & Audit Tool</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 1. LOGIN SCREEN ---
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("Engineer Login")
        password = st.text_input("License Key", type="password", placeholder="Enter Key (Try: UK-PRO-2026)")
        if st.button("Access Site Tool"):
            if password == "UK-PRO-2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Key")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --- 2. SAFETY DASHBOARD ---
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    with st.expander("🛡️ SITE SAFETY CHECK (Required)", expanded=True):
        st.caption("Confirm pre-work safety checks:")
        c1, c2 = st.columns(2)
        with c1: v1 = st.checkbox("PPE OK")
        with c2: v2 = st.checkbox("LOTO OK")
        v3 = st.checkbox("Risk Assessment Complete")
    
    if not (v1 and v2 and v3):
        st.warning("⚠️ Complete checks to unlock tool")
        st.stop()
    else:
        st.markdown('<span class="badge-safe">SITE SECURE</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. DIAGNOSTIC INPUT ---
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("📍 Unit Identification")
    
    tab1, tab2 = st.tabs(["Database Search", "Custom Unit"])
    
    target_unit = ""
    selected_context = ""
    
    with tab1:
        brand = st.selectbox("Brand", ["Select..."] + list(KNOWLEDGE_BASE.keys()))
        if brand != "Select...":
            model = st.selectbox("Model", list(KNOWLEDGE_BASE[brand].keys()))
            if model:
                target_unit = f"{brand} {model}"
                selected_context = KNOWLEDGE_BASE[brand][model]

    with tab2:
        custom_input = st.text_input("Manual Entry", placeholder="e.g., Remeha Quinta 45")
        if custom_input:
            target_unit = f"Custom: {custom_input}"
            selected_context = "General UK HVAC Engineering Principles (Non-Verified Manual)"

    st.markdown("---")
    fault = st.text_input("Symptom / Error Code", placeholder="e.g., F.22 or Leaking Water")
    
    if st.button("Analyze Fault"):
        if not fault or not target_unit:
            st.error("Please select a unit and enter a fault.")
        else:
            if not st.secrets.get("ANTHROPIC_API_KEY"):
                st.error("API Key Missing")
                return

            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            with st.spinner("Processing..."):
                prompt = f"""
                ACT AS: UK Senior HVAC Engineer.
                UNIT: {target_unit}
                CONTEXT: {selected_context}
                FAULT: {fault}
                
                OUTPUT FORMAT (Mobile Friendly):
                1. 🔍 DIAGNOSIS: One sentence.
                2. 🛠️ ACTION: 5 numbered bullet points.
                3. ⚠️ WARNING: One safety critical note.
                """
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=600,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.session_state.result = response.content[0].text
                st.session_state.unit_log = target_unit
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. RESULT & AUDIT CARD ---
    if "result" in st.session_state:
        st.markdown('<div class="app-card" style="border-left: 5px solid #003366;">', unsafe_allow_html=True)
        st.subheader("📋 Action Plan")
        st.markdown(st.session_state.result)
        st.markdown("---")
        
        # Quick Audit
        st.caption("Job Completion")
        col_eng, col_ref = st.columns(2)
        with col_eng: eng = st.text_input("Engineer", placeholder="Initials")
        with col_ref: ref = st.text_input("Job #", placeholder="1234")
        
        if st.button("💾 Save & Close Job"):
            report = f"AUDIT: {st.session_state.unit_log} | Ref: {ref} | Eng: {eng} | Plan: {st.session_state.result}"
            st.download_button("Download Log", report, file_name=f"Job_{ref}.txt")
            st.success("Job Logged Locally")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
