import streamlit as st
import anthropic
from datetime import datetime

# --- 1. CONFIGURATION & SELLABLE BRANDING ---
st.set_page_config(page_title="HVAC Tech-Audit AI", page_icon="🔧", layout="wide")

# This CSS makes it look like a professional corporate tool, not a hobby project
st.markdown("""
    <style>
    .report-header { font-size: 24px; font-weight: bold; color: #004a99; }
    .safety-banner { background-color: #d32f2f; color: white; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #b71c1c; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .success-box { background-color: #e8f5e9; padding: 20px; border-left: 5px solid #2e7d32; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE COMPREHENSIVE KNOWLEDGE ENGINE (RAG) ---
# This is your proprietary "Moat."
KNOWLEDGE_BASE = {
    "Vaillant (Boilers/Heat Pumps)": {
        "aroTHERM Plus (HP)": "F.022: Low water pressure (<0.6 bar). F.718: Fan blocked. F.729: Compressor outlet <0C (EEV fault). F.731: HP Switch open. 70C flow capability.",
        "ecoTEC plus (Boiler)": "F.22: Dry fire/No water. F.28: Ignition failed (Check gas/spark). F.75: No pressure change on pump start (Check sensor/pump). F.29: Flame loss during operation.",
        "General": "Gas valve adjustment requires calibrated flue gas analyser."
    },
    "Mitsubishi Ecodan (Heat Pump)": {
        "R290/R32 Models": "U1: High pressure (Check strainer/pump flow). L9: Low flow rate error. P6: Overheating heat exchanger. F3: Low pressure switch failure. U2: High discharge temp."
    },
    "Worcester Bosch (Boilers)": {
        "Greenstar 4000": "C7: Fan not running on start. E9: High limit thermostat (Overheat). EA: No flame signal. A1: Pump stuck/dry. F7: False flame.",
        "GB162 (Commercial)": "227/6A: Ignition failure (check ionisation). 215/C6: Fan speed too high. 216/3P: Fan speed too low. 224/E9: Safety sensor >105C."
    },
    "Baxi (Boilers)": {
        "Duo-tec/Platinum": "E110: Overheat (Check pump/valves). E119: Low water pressure. E133: Gas supply/Ignition. E160: Fan fault.",
        "600/800 Series": "H.01: Gas valve comms. E.04: Flow sensor open. E.01.12: Return temp > Flow temp (Check circulation)."
    },
    "Ideal (Boilers)": {
        "Evomax 2 (Commercial)": "L1: No water flow. L2: Ignition lockout. FU: Flow/Return Diff >50C (Check pump). LC: Too many resets.",
        "Logic Combi": "F1: Low Pressure. F2: Flame Loss. L2: Ignition fault. F3: Fan fault."
    },
    "Samsung EHS (Heat Pump)": {
        "Mono HT Quiet": "E911: Low flow rate. E101: Comms error between units. E912: Flow switch error. Operation down to -25C."
    },
    "Daikin Altherma (Heat Pump)": {
        "LT/HT Split": "A1: PCB Defect. A5: HP Control (Dirty heat exchanger). E3: HP Switch tripped. U0: Low Refrigerant. E7: Fan motor lock."
    },
    "Viessmann (Boilers)": {
        "Vitodens 100-W": "F2: Burner overheat. F4: No flame (Check condensate pipe if frozen). F9: Fan speed low. Code 10: Outdoor sensor fault."
    },
    "Commercial Refrigeration (Williams/Foster/Adande)": {
        "Williams Multideck": "HI: High temp alarm. LO: Low temp. CL: Clean condenser. E1: Air probe fail. E16: Compressor High Pressure.",
        "Foster EcoShow": "hc: Condenser high temp. hP: Condenser high pressure. dEF: Defrost active. E1/E2: Probe fault.",
        "Adande Drawers": "rPF/EPF: Probe failure. HA: High temp (+7C above set). do: Drawer open >3 mins."
    },
    "Commercial Refrigeration (True/Arneg)": {
        "True T-Series": "P1/E1: Probe fail. HA: Max temp alarm. do: Door open. Short Cycle: Low gas or dirty coils."
    }
}

# --- 3. THE AUDIT & SAFETY GATES ---
def main():
    st.sidebar.markdown("## 🛡️ Admin Portal")
    
    # Sellable Feature: Access Control
    access_code = st.sidebar.text_input("Enter Company License Key", type="password")
    if access_code != "UK-SME-PREMIUM-2026":
        st.warning("🔒 Access Restricted. Please enter a valid license key.")
        st.info("Contact your consultancy lead for a demo key.")
        return

    # MANDATORY DISCLAIMER
    st.markdown('<div class="safety-banner">CRITICAL SAFETY WARNING: GAS SAFE & F-GAS COMPLIANCE</div>', unsafe_allow_html=True)
    st.caption("This tool provides automated technical references. It does NOT replace the onsite assessment of a qualified engineer. All work must be verified by a certified professional.")
    
    st.divider()

    # SAFETY CHECKBOXES (Liability Shield)
    st.subheader("Engineer Pre-Work Verification")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        v1 = st.checkbox("PPE Confirmed (Gloves/Eyes)")
    with col_b:
        v2 = st.checkbox("Power Isolated (LOTO)")
    with col_c:
        v3 = st.checkbox("Gas Supply Checked")

    if not (v1 and v2 and v3):
        st.error("🛑 You must confirm all safety protocols before the AI Agent will provide repair steps.")
        st.stop()

    # --- 4. IDENTIFICATION & ANALYSIS ---
    st.header("1. Identify Unit & Diagnostic")
    
    brand_list = list(KNOWLEDGE_BASE.keys())
    selected_brand = st.selectbox("Select Manufacturer", ["Choose Brand..."] + brand_list)
    
    if selected_brand != "Choose Brand...":
        models = list(KNOWLEDGE_BASE[selected_brand].keys())
        selected_model = st.selectbox("Select Model Series", models)
        manual_context = KNOWLEDGE_BASE[selected_brand][selected_model]
        
        st.info(f"📚 Context Loaded: {selected_model}")

        # Input Section
        user_input = st.text_area("Describe the fault or enter the Error Code (e.g. 'F.28' or 'Compressor not starting')")
        
        if st.button("🚀 Analyze & Generate SOP"):
            if not st.secrets.get("ANTHROPIC_API_KEY"):
                st.error("System Error: API Configuration Missing.")
                return

            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            with st.spinner("Analyzing Technical Database..."):
                # THE PROMPT (Hardened for Accuracy)
                prompt = f"""
                You are a Master HVAC & Refrigeration Engineer in the UK. 
                STRICT KNOWLEDGE BASE: {manual_context}
                TECH ISSUE: {user_input}
                
                RESPONSE STRUCTURE:
                1. IDENTIFICATION: Confirm the error code meaning from the provided data.
                2. SAFETY FIRST: Note specific hazards for THIS model (e.g. R290 flammability).
                3. STEP-BY-STEP REPAIR: 5 clear steps using UK terminology (e.g. 'Spanner', 'Multimeter').
                4. TOOL LIST: List specific tools needed.
                5. DISMISSIVE WARNING: Remind the tech to check gas pressures only if Gas Safe.
                
                If the error code is NOT in the knowledge base, state 'Code not found in official manual' and provide general troubleshooting based on UK standards.
                """
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # --- 5. THE OUTPUT (Sellable Audit Trail) ---
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown("### 📋 AI-Generated Field SOP")
                st.write(response.content[0].text)
                st.markdown('</div>', unsafe_allow_html=True)

                st.divider()
                st.subheader("2. Job Completion & Compliance Log")
                eng_name = st.text_input("Engineer Name")
                site_ref = st.text_input("Site Reference / Job Number")
                
                if st.button("📥 Export Audit Report"):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    report_data = f"""
                    --- HVAC TECH-AUDIT REPORT ---
                    Generated: {timestamp}
                    Engineer: {eng_name}
                    Site Ref: {site_ref}
                    Model Identified: {selected_model}
                    Action Plan Provided:
                    {response.content[0].text}
                    -----------------------------------
                    LEGAL: This report confirms AI assistance was used as a reference. 
                    The signing engineer ({eng_name}) confirms all safety checks were met.
                    """
                    st.download_button("Download Report as TXT", report_data, file_name=f"Audit_{site_ref}.txt")

if __name__ == "__main__":
    main()
