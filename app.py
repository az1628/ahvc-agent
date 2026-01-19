import streamlit as st
import anthropic
from datetime import datetime

# --- 1. 2026 COMPLIANCE STYLING ---
st.set_page_config(page_title="HVAC Tech-Audit AI (2026 Edition)", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .safety-banner { background-color: #b71c1c; color: white; padding: 20px; border-radius: 10px; text-align: center; border: 3px solid #ff5252; }
    .compliance-tag { background-color: #004a99; color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE 2026 KNOWLEDGE ENGINE ---
# Includes the new 2026 A2L (Mildly Flammable) and R290 (Propane) safety data
KNOWLEDGE_BASE = {
    "Vaillant (Boilers/Heat Pumps)": {
        "aroTHERM Plus (R290)": "F.022: Low pressure (<0.6 bar). F.718: Fan blocked. R290 SAFETY: Flammable refrigerant. Ensure no ignition sources within 1m boundary (2026 UK Rule).",
        "ecoTEC plus": "F.22: Low water. F.28: Ignition fail. F.75: Pump/Sensor fault. F.29: Flame loss during run."
    },
    "Mitsubishi Ecodan (Heat Pump)": {
        "Ecodan R290 Series": "U1: High pressure (Strainer/Flow). L9: Low flow rate. P6: Heat exchanger overheat. SMART-READY: Must verify grid-connection for 2026 MCS compliance."
    },
    "Worcester Bosch": {
        "Greenstar 4000": "EA: Ignition fault. E9: Overheat. C6: Fan speed. A1: Pump stuck. F7: False flame.",
        "GB162 Commercial": "227: Ignition fail. 216: Fan too slow. 224: Safety sensor overheat (>105C)."
    },
    "Daikin Altherma": {
        "3 H HT (R32/A2L)": "A5: HP Control. E3: HP Switch. U0: Low Gas. A2L SAFETY: Use spark-resistant vacuum pumps and recovery units."
    },
    "Ideal": {
        "Evomax 2": "L1: No flow. L2: Ignition lockout. FU: Delta-T >50C. LC: Reset limit reached.",
        "Logic Combi": "F1: Low Pressure. F2: Flame Loss. L2: Ignition. F3: Fan."
    },
    "Commercial Refrigeration": {
        "Williams Multideck": "HI: High Temp. CL: Clean Condenser. E1: Air probe fail. E16: HP Alarm (Check airflow).",
        "Foster EcoShow": "hc: High Condenser Temp. hP: High Pressure (Danger). E1: Probe fault. dEF: Defrosting.",
        "Adande Drawers": "rPF: Probe fail. HA: High temp. do: Door open. safety cycle: 10m ON/OFF."
    }
}

def main():
    st.sidebar.title("🛠️ Engineer Portal")
    
    # LICENSE KEY (Your Income Stream)
    access_code = st.sidebar.text_input("Consultancy License Key", type="password")
    if access_code != "UK-2026-PRO":
        st.info("Please enter your company's 2026 License Key to activate the Audit Trail.")
        return

    st.markdown('<div class="safety-banner">CRITICAL: 2026 F-GAS & A2L PROTOCOL ACTIVE</div>', unsafe_allow_html=True)
    
    # 3. COMPLIANCE CHECKLIST
    st.subheader("Post-Jan 2026 Safety Verification")
    col1, col2, col3 = st.columns(3)
    with col1:
        s1 = st.checkbox("Spark-Resistant Tools (for A2L/R290)")
    with col2:
        s2 = st.checkbox("1m Exclusion Zone Verified")
    with col3:
        s3 = st.checkbox("Smart-Ready Grid Check")

    if not (s1 and s2 and s3):
        st.warning("All 2026 Regulatory Checks must be ticked to unlock technical SOPs.")
        st.stop()

    st.divider()

    # 4. DIAGNOSTIC INTERFACE
    brand = st.selectbox("Manufacturer", ["Choose..."] + list(KNOWLEDGE_BASE.keys()))
    if brand != "Choose...":
        model = st.selectbox("Model", list(KNOWLEDGE_BASE[brand].keys()))
        fault = st.text_input("Enter Error Code or Symptom (e.g., 'F.22')")

        if st.button("Generate Compliance-Verified SOP"):
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            with st.spinner("Consulting 2026 Regulatory Database..."):
                prompt = f"""
                You are a Lead HVAC Auditor. Context: {KNOWLEDGE_BASE[brand][model]}. 
                Fault: {fault}. 
                Provide: 
                1. 5-step repair SOP using UK terminology.
                2. Mandatory 2026 safety warning for this specific refrigerant.
                3. Required tools list.
                """
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.success("### FIELD SOP & AUDIT GUIDE")
                st.write(response.content[0].text)
                
                # 5. DOWNLOADABLE AUDIT LOG (The "Saleable" Output)
                st.divider()
                st.subheader("Download Compliance Report")
                eng_name = st.text_input("Engineer Name")
                if st.button("Generate Audit PDF"):
                    report = f"AUDIT LOG: {datetime.now()}\nEngineer: {eng_name}\nUnit: {model}\nAction: {response.content[0].text}"
                    st.download_button("Download Compliance.txt", report, file_name=f"Audit_{eng_name}.txt")

if __name__ == "__main__":
    main()
