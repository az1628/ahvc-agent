import streamlit as st
import anthropic
from datetime import datetime

# --- 1. PREMIUM BRANDING & UI ---
st.set_page_config(page_title="HVAC Sentinel Pro | 2026 Audit", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    .compliance-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 8px solid #002d62; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .safety-banner { 
        background: linear-gradient(90deg, #d32f2f 0%, #b71c1c 100%); 
        color: white; 
        padding: 15px; 
        border-radius: 8px; 
        text-align: center; 
        font-weight: 700;
        letter-spacing: 1px;
    }
    .brand-text { color: #002d62; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; margin-bottom: 0px; }
    .stButton>button { 
        background-color: #002d62; 
        color: white; 
        border-radius: 6px; 
        font-weight: bold; 
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004a99; border: 1px solid gold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MASTER KNOWLEDGE BASE ---
# Expanded to include Residential, Commercial, and Industrial units
KNOWLEDGE_BASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": "F.022: Low water (<0.6 bar). F.718: Fan blocked. F.729: Compressor outlet <0C. R290 SAFETY: Flammable. 1m Boundary.",
        "ecoTEC plus/pro": "F.22: Dry fire. F.28: Ignition fail. F.75: Pump sensor fault. F.29: Flame loss.",
        "flexoTHERM": "701: Brine flow error. 702: Ground source sensor fault."
    },
    "Mitsubishi Electric": {
        "Ecodan R290/R32": "U1: High pressure/flow. L9: Flow rate drop. P6: Overheat. F3: LP switch failure.",
        "City Multi VRF": "4115: Discharge temp error. 1500: Refrigerant overcharge. 1102: Discharge temp thermistor."
    },
    "Worcester Bosch": {
        "Greenstar 4000/8000": "EA: Ignition fault. E9: Overheat. C6: Fan speed. A1: Pump stuck. F7: False flame.",
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
        "Vitodens 100/200": "F2: Burner overheat. F4: No flame (Frozen condensate). F9: Fan speed low."
    },
    "Commercial Fridge (Williams/Foster)": {
        "Williams Multideck": "HI: High Temp. CL: Clean Condenser. E1: Air probe fail. E16: HP Alarm.",
        "Foster EcoShow": "hc: Condenser high temp. hP: High Pressure. dEF: Defrost active."
    },
    "Commercial Fridge (Adande/True)": {
        "Adande Drawers": "rPF: Probe fail. HA: High temp. do: Door open. safety cycle active.",
        "True GDM/T-Series": "P1: Probe fail. HA: Max temp. do: Door open. Short cycle: Dirty condenser."
    }
}

def main():
    # --- HEADER ---
    st.markdown('<h1 class="brand-text">HVAC SENTINEL <span style="color:#004a99">PRO</span></h1>', unsafe_allow_html=True)
    st.caption("v2.4 | UK Technical Compliance & Real-Time Audit Engine")

    # --- SIDEBAR / LICENSE GATE ---
    st.sidebar.markdown("### 🔐 Secure Login")
    access_code = st.sidebar.text_input("Consultancy License Key", type="password")
    if access_code != "UK-PRO-2026":
        st.sidebar.warning("Restricted Access. License Required.")
        return

    st.sidebar.success("✅ License: SME Premium")
    
    # --- SAFETY INTERLOCK ---
    st.markdown('<div class="safety-banner">⚠️ MANDATORY 2026 SAFETY PROTOCOL ACTIVE</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
        st.subheader("Step 1: Compliance Check")
        c1, c2, c3 = st.columns(3)
        with c1: v1 = st.checkbox("PPE: Gloves & Eye Pro")
        with c2: v2 = st.checkbox("Safe Isolation (LOTO)")
        with c3: v3 = st.checkbox("F-Gas Logbook / Gas Safe Record Opened")
        st.markdown('</div>', unsafe_allow_html=True)

    if not (v1 and v2 and v3):
        st.stop()

    # --- DIAGNOSTIC ENGINE ---
    st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
    st.subheader("Step 2: Unit Selection")
    
    mode = st.radio("Unit Selection Mode:", ["Search Database", "Enter Custom Model"], horizontal=True)
    
    selected_context = ""
    target_unit = ""

    if mode == "Search Database":
        d1, d2 = st.columns(2)
        with d1:
            brand = st.selectbox("Manufacturer", ["Select..."] + list(KNOWLEDGE_BASE.keys()))
        with d2:
            if brand != "Select...":
                model = st.selectbox("Model Series", list(KNOWLEDGE_BASE[brand].keys()))
                selected_context = KNOWLEDGE_BASE[brand][model]
                target_unit = f"{brand} {model}"
            else:
                st.selectbox("Model Series", ["Select Brand First..."], disabled=True)
    else:
        c1, c2 = st.columns(2)
        with c1: custom_brand = st.text_input("Enter Brand (e.g., Ariston)")
        with c2: custom_model = st.text_input("Enter Model (e.g., Clas One)")
        target_unit = f"CUSTOM: {custom_brand} {custom_model}"
        selected_context = "No verified manual in local DB. Use general engineering principles for this specific manufacturer."

    fault = st.text_input("Fault / Error Code (e.g. 'F.28' or 'Loud vibrating noise')")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 GENERATE COMPLIANCE-VERIFIED SOP"):
        if not st.secrets.get("ANTHROPIC_API_KEY"):
            st.error("API Key missing in Secrets.")
            return

        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        with st.spinner("Analyzing Technical Data..."):
            prompt = f"""
            Role: Lead UK HVAC/Gas Safe Auditor. 
            Unit: {target_unit}
            Verified Context: {selected_context}
            User Issue: {fault}
            
            Structure:
            1. DIAGNOSIS: Explain what is likely happening.
            2. SOP: 5 step repair guide for a qualified engineer.
            3. SAFETY: Crucial hazards (Gas/Electrical/Refrigerant).
            4. VERIFICATION: How to test the fix.
            """
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.markdown("### 📋 Automated Field Guidance")
            st.success(response.content[0].text)
            
            # --- AUDIT LOG ---
            st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
            st.subheader("Step 3: Close Job & Audit")
            eng_name = st.text_input("Engineer Name")
            job_ref = st.text_input("Job Reference Number")
            
            if st.button("📁 GENERATE OFFICIAL AUDIT LOG"):
                report = f"AUDIT LOG: {target_unit}\nRef: {job_ref}\nEng: {eng_name}\nPlan: {response.content[0].text}"
                st.download_button("Download Compliance Report", report, file_name=f"Audit_{job_ref}.txt")
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("<p style='text-align: center; color: #666;'>&copy; 2026 HVAC Sentinel | Licensed for Certified Professionals Only</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
