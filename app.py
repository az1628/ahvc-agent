import streamlit as st
import anthropic
from datetime import datetime

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="HVAC Doc Pro | Technical Reference",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === PROFESSIONAL UI STYLING ===
st.markdown("""
<style>
    /* Global App Styling */
    .stApp { background-color: #f8f9fa; }
    
    /* Header Styling */
    .app-header {
        background-color: #003366;
        padding: 30px 20px;
        margin: -70px -70px 30px -70px;
        text-align: center;
        border-bottom: 4px solid #b71c1c;
    }
    .app-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: 1px;
    }
    .app-subtitle {
        font-size: 14px;
        color: #e0e0e0;
        margin-top: 5px;
        font-weight: 400;
    }
    
    /* Input & Dropdown Styling */
    .stSelectbox label, .stTextInput label, .stTextArea label {
        font-weight: 700;
        color: #003366;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px;
        font-weight: 600;
        font-size: 16px;
        margin-top: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #004a99;
    }
    
    /* Card/Box Styling */
    .info-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Badge Styling */
    .badge-success { 
        background-color: #2e7d32; 
        color: white; 
        padding: 6px 12px; 
        border-radius: 4px; 
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    
    /* Result Box Styling */
    .result-box {
        background: #ffffff;
        border-left: 6px solid #003366;
        padding: 25px;
        border-radius: 8px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Legal Warning Box */
    .legal-box {
        background: #fff3e0;
        border: 2px solid #ff9800;
        border-radius: 8px;
        padding: 20px;
        color: #e65100;
        font-size: 0.9em;
    }

    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# === THE KNOWLEDGE BASE (DATA ENGINE) ===
HVAC_DATABASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": {
            "faults": "F.022: Low pressure (<0.6 bar) - Check PRV/auto-air-vent. F.718: Fan blocked/thermistor fault. F.729: Compressor discharge <0°C - refrigerant issue. F.724: Brine flow error.",
            "safety": "R290 FLAMMABLE. 1m exclusion zone. No naked flames. Leak detector mandatory.",
            "specs": "7-15kW output. COP 4.5 @ A7/W35. Requires G3 ticket for F-Gas work."
        },
        "ecoTEC plus 825/835": {
            "faults": "F.22: Dry fire protection (low pressure). F.28: Ignition lockout (gas/ignition). F.75: Pump circulation fault. F.29: Flame loss during operation. F.62: Gas valve delay.",
            "safety": "Gas Safe registered engineer only. Check ventilation. CO detector mandatory.",
            "specs": "Combi 25-35kW. Min 1.5 bar pressure. Annual service required."
        },
        "flexoTHERM exclusive": {
            "faults": "701: Brine/water flow error. 702: Ground source sensor fault. 704: Evaporator NTC error. F.2016: Low brine temp.",
            "safety": "Glycol antifreeze toxic. Pressurized system. Isolation required.",
            "specs": "Ground source 5.6-15.6kW. Requires MCS certification for RHI."
        }
    },
    "Worcester Bosch": {
        "Greenstar 4000/8000": {
            "faults": "EA/224: Ignition fault - check gas/electrodes. E9/227: Overheat >95°C. C6: Fan speed error. A1: Pump blocked. 227: Flame detection. 216: Fan too slow.",
            "safety": "LPG models require LPGA cert. Ventilation critical. Gas tightness test 1 min hold.",
            "specs": "18-40kW range. 94% efficiency. 5yr warranty (registered). Complies BS 6798."
        },
        "GB162 Commercial": {
            "faults": "227: Ignition lockout (3 attempts). 216: Fan underspeed. 224: Overheat >105°C. EA: Electrode/gas fault. 260: Flue thermistor.",
            "safety": "Commercial ticket required. Flue analyser mandatory. CO <200ppm.",
            "specs": "100-199kW. Cascade up to 1MW. Annual PSSR inspection required."
        },
        "Greenstar Highflow CDi": {
            "faults": "E9: DHW overheat. EA: Ignition fail. A7: Diverter valve stuck. D5: Internal fault. 227: Flame sensor.",
            "safety": "Unvented cylinder regs apply. G3 ticket required. 3 bar PRV test.",
            "specs": "440 CDi = 35kW + 110L store. Legionella cycle 60°C weekly."
        }
    },
    "Mitsubishi Electric": {
        "Ecodan R290 Monobloc": {
            "faults": "U1: High pressure/Low flow. L9: Abnormal flow rate. P6: Overheat protection. F3: LP switch fail. U4: Transmission error. P1: Voltage imbalance.",
            "safety": "R290 FLAMMABLE. Spark-free tools only. 1m boundary. Nitrogen purge during brazing.",
            "specs": "8.5-14kW @ -7°C. Flow temp 60°C max. MCS 020 certified."
        },
        "City Multi VRF R32": {
            "faults": "4115: Discharge temp >115°C. 1500: Refrigerant overcharge. 1102: Discharge thermistor. 6800: Compressor temp. E203: Transmission PCB.",
            "safety": "R32 mildly flammable (A2L). Room size calculations BS EN 378. F-Gas Cat I.",
            "specs": "Up to 135kW. Heat recovery. BEMS integration. 50Hz 3-phase."
        }
    },
    "Daikin": {
        "Altherma 3 H HT": {
            "faults": "A5: High pressure control PCB. E3: HP switch trip. U0: Low refrigerant. E7: Fan motor lock. U4: Indoor/outdoor comms. AH: Water pump fault.",
            "safety": "R410A system. Pressure test 42 bar. F-Gas handling certificate required.",
            "specs": "16-18kW @ -10°C. 70°C flow temp. Buffer tank recommended <radiators."
        }
    },
    "Baxi": {
        "800 Combi": {
            "faults": "E119: Low pressure (<0.5 bar). E133: Gas supply/ignition. E110: Overheat stat. E125: Pump blockage. E117: Water pressure sensor.",
            "safety": "Ventilation MUST comply with BS 5440. CO alarm within 1m horizontal.",
            "specs": "24-30kW combi. Min inlet 1.5 bar. Built-in filling loop (keyed)."
        },
        "Assure Commercial": {
            "faults": "E01: No flame detected. E03: Fan fault. E09: Safety stat. E28: Flame loss. E125: Circulation fault.",
            "safety": "Commercial gas ticket. Flue flow test. Ventilation calc per BS 6644.",
            "specs": "80-250kW. Cascade control. PSSR annual exam. 95% gross efficiency."
        }
    },
    "Ideal": {
        "Logic Max Combi": {
            "faults": "F1: Low pressure (<0.5 bar). F2: Flame loss. L2: Ignition lockout (6 tries). F3: Fan fault. FD: Flame detection. FL: False flame.",
            "safety": "25mm copper required on gas. Compression fittings only (no solder near valve).",
            "specs": "24-35kW. 10yr warranty (registered). ErP A-rated."
        },
        "Evomax 2 System": {
            "faults": "L1: No flow detected. L2: Ignition lockout. FU: Delta-T fault >50°C. F3: Fan underspeed. F9: Gas valve fault.",
            "safety": "System boiler - unvented regs apply if DHW cylinder. Benchmark checklist.",
            "specs": "60-150kW. Low NOx Class 6. Weather comp + OpenTherm."
        }
    },
    "Viessmann": {
        "Vitodens 100/200": {
            "faults": "F2: Burner overheat. F4: No flame signal. F9: Fan speed too low. F5: External error. FD: Flame monitoring.",
            "safety": "Condensate pH <4. Neutralizer required (commercial). Trap prime 0.5L.",
            "specs": "19-35kW. Lambda Pro Control. ViCare app. 5-10yr warranty."
        }
    },
    "Samsung": {
        "EHS Mono HT Quiet": {
            "faults": "E911: Low flow (<12 L/min). E101: Indoor/outdoor comms error. E912: Flow switch stuck. E121: Indoor temp sensor. E441: Discharge temp.",
            "safety": "R32 refrigerant. Room volume check. 2.5mm² min cable. RCD protection.",
            "specs": "12-16kW. 65°C flow temp. ErP A+++. 7yr compressor warranty."
        }
    },
    "Commercial Refrigeration": {
        "Williams Multideck": {
            "faults": "HI: High temp alarm. CL: Condenser blocked. E1: Air probe fail. E16: HP alarm. dEF: Defrost cycle. E2: Evaporator probe.",
            "safety": "R404A/R448A. F-Gas record keeping. Leak test annual. Door seals weekly check.",
            "specs": "Medium temp +1/+4°C. Night blind. LED lighting. IP20 rating."
        },
        "Foster EcoShow": {
            "faults": "hc: High condenser temp. hP: High pressure trip. dEF: Defrost active. LS: Low superheat. E3: Evap probe error.",
            "safety": "HFC refrigerant. Ventilation check. Door alarms functional. HACCP compliance.",
            "specs": "Remote/integral. Glass doors. Anti-sweat heaters. Temp log weekly."
        }
    }
}

# === LEGAL DISCLAIMER ===
LEGAL_DISCLAIMER = """
### ⚠️ IMPORTANT LEGAL NOTICE

**This tool provides REFERENCE information only.**

**What this is NOT:**
- Professional engineering advice
- A replacement for Gas Safe/OFTEC certification
- A guarantee of accuracy

**Your responsibilities:**
- You MUST hold valid UK certifications for regulated gas/refrigerant work
- You accept FULL liability for all work decisions
- You will comply with UK Gas Safety Regulations, F-Gas Regulations, and Building Regulations

**BY CLICKING ACCEPT, YOU AGREE TO THESE TERMS.**
"""

def main():
    # --- HEADER ---
    st.markdown("""
        <div class="app-header">
            <div class="app-title">HVAC DOC PRO</div>
            <div class="app-subtitle">2026 Technical Reference System</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 1. LEGAL ACCEPTANCE ---
    if "legal_accepted" not in st.session_state:
        st.session_state.legal_accepted = False
    
    if not st.session_state.legal_accepted:
        st.markdown('<div class="legal-box">', unsafe_allow_html=True)
        st.markdown(LEGAL_DISCLAIMER)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("✅ I Accept - I Am Qualified"):
            st.session_state.legal_accepted = True
            st.rerun()
        return

    # --- 2. LOGIN (SIMULATED) ---
    if "verified" not in st.session_state:
        st.session_state.verified = False

    if not st.session_state.verified:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("Engineer Login")
        company = st.text_input("Company Name", placeholder="e.g. British Gas")
        key = st.text_input("License Key", type="password")
        st.caption("🔑 Demo Key: `HVAC2026`")
        
        if st.button("Login"):
            if key in ["HVAC2026", "TRIAL"] and company:
                st.session_state.verified = True
                st.session_state.company = company
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # --- 3. SAFETY CHECKS ---
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Site Safety Verification")
    c1, c2, c3 = st.columns(3)
    with c1: ppe = st.checkbox("PPE Worn")
    with c2: loto = st.checkbox("Isolated (LOTO)")
    with c3: risk = st.checkbox("Risk Assessed")
    
    if ppe and loto and risk:
        st.markdown('<span class="badge-success">SAFE TO PROCEED</span>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Complete safety checks to unlock tool.")
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 4. DATA SELECTION (DYNAMIC DROPDOWNS) ---
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("📍 Equipment Selector")
    
    tab1, tab2 = st.tabs(["Database Search", "Manual Entry"])
    
    selected_unit = ""
    context_data = {}
    
    with tab1:
        # Step 1: Select Brand
        brand_list = ["Select Manufacturer..."] + sorted(list(HVAC_DATABASE.keys()))
        brand = st.selectbox("Manufacturer", brand_list)
        
        # Step 2: Select Model (Logic ensures this only shows if Brand is selected)
        if brand != "Select Manufacturer...":
            model_list = sorted(list(HVAC_DATABASE[brand].keys()))
            model = st.selectbox("Model Series", model_list)
            
            if model:
                selected_unit = f"{brand} {model}"
                context_data = HVAC_DATABASE[brand][model]
                st.info(f"📚 Loaded Manual: **{selected_unit}**")
                # Show safety warning immediately if available
                if "safety" in context_data:
                    st.caption(f"⚠️ **Safety Note:** {context_data['safety']}")
        else:
            # Placeholder to keep UI consistent
            st.selectbox("Model Series", ["Please Select Manufacturer First"], disabled=True)

    with tab2:
        custom_entry = st.text_input("Enter Unit Name", placeholder="e.g. Remeha Quinta 45")
        if custom_entry:
            selected_unit = f"Custom: {custom_entry}"
            context_data = {"faults": "Standard UK HVAC Engineering Principles apply."}

    st.markdown("---")
    fault_input = st.text_area("Describe Fault / Error Code", placeholder="e.g. F.22, Radiators cold, Pressure 0 bar")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5. AI GENERATION ENGINE ---
    if st.button("🚀 GENERATE REPAIR GUIDE"):
        if not selected_unit or not fault_input:
            st.error("Please select a unit and enter a fault description.")
            return

        if not st.secrets.get("ANTHROPIC_API_KEY"):
            st.error("Configuration Error: API Key missing.")
            return
            
        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            # Context builder
            tech_context = ""
            if context_data:
                tech_context = f"SPECS: {context_data.get('specs', 'N/A')}\nKNOWN FAULTS: {context_data.get('faults', 'N/A')}\nSAFETY: {context_data.get('safety', 'Critical')}"

            # PROMPT ENGINEERING WITH DIAGRAM TRIGGERS
            prompt = f"""
            You are a Senior UK HVAC Engineer.
            UNIT: {selected_unit}
            USER FAULT: {fault_input}
            DATA: {tech_context}
            
            Create a Field Reference Guide. 
            
            STRATEGIC DIAGRAMMING:
            If a visual aid would significantly help the user (e.g. wiring diagram, valve location, multimeter test points), insert a tag on its own line like  or . Only use images if they add instructive value.
            
            FORMAT:
            1. 🔍 DIAGNOSIS: (Likely cause)
            2. 🛠️ ACTION PLAN: (5 numbered steps)
            3. ⚠️ SAFETY HAZARD: (Specific to this unit/gas type)
            4. 🔩 PARTS: (Likely parts needed)
            5. 📜 REGULATORY: (Relevant BS/Gas Safe regulation)
            """
            
            with st.spinner("Consulting Technical Library..."):
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result_text = response.content[0].text
                
                # --- RESULTS DISPLAY ---
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.subheader("📋 Field Technical Reference")
                st.markdown(f"**Unit:** {selected_unit} | **Ref:** {datetime.now().strftime('%H:%M')}")
                st.markdown("---")
                st.markdown(result_text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # --- EXPORT ---
                report = f"HVAC DOC PRO REPORT\nUnit: {selected_unit}\nFault: {fault_input}\n\n{result_text}"
                st.download_button("💾 Download Audit Log", report, file_name=f"Job_{datetime.now().strftime('%Y%m%d')}.txt")

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

    # --- FOOTER ---
    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#888; font-size:12px;'>HVAC DOC PRO | Licensed to Qualified Engineers Only</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
