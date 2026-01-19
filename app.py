import streamlit as st
import anthropic
from datetime import datetime
import json

# === PAGE CONFIG ===
st.set_page_config(
    page_title="HVAC Doc Pro | Technical Reference",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === PROFESSIONAL UI STYLING ===
st.markdown("""
<style>
    /* Simple Clean Theme */
    .stApp { 
        background-color: #ffffff;
    }
    
    /* Simple Header */
    .app-header {
        background-color: #2c5282;
        padding: 30px 20px;
        margin: -70px -70px 40px -70px;
        text-align: center;
    }
    .app-title {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .app-subtitle {
        font-size: 15px;
        color: #ffffff;
        opacity: 0.9;
        margin-top: 8px;
    }
    
    /* Simple Buttons */
    .stButton>button {
        width: 100%;
        background-color: #2c5282;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 24px;
        font-weight: 600;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #1e3a5f;
    }
    
    /* Simple Cards */
    .info-card {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        padding: 25px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    /* Status Badges */
    .badge-success { 
        background-color: #28a745; 
        color: white; 
        padding: 8px 16px; 
        border-radius: 6px; 
        font-weight: 600;
        display: inline-block;
    }
    
    /* Legal Box */
    .legal-box {
        background: #fff3cd;
        border: 3px solid #ffc107;
        border-radius: 8px;
        padding: 25px;
        margin: 25px 0;
    }
    
    /* Results Box */
    .result-box {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 30px;
        margin: 25px 0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# === EXPANDED UK HVAC KNOWLEDGE BASE ===
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
        },
        "Mr Slim PEA Wall Units": {
            "faults": "E6: Indoor/outdoor comms. E1: Indoor PCB. E3: High pressure switch. E7: Fan motor lock. P8: High temp detection.",
            "safety": "R32 room volume check mandatory. Leak detection <3kg charge exempt.",
            "specs": "2.5-7.1kW cooling. SCOP 4.3. WiFi MELCloud ready."
        }
    },
    "Daikin": {
        "Altherma 3 H HT": {
            "faults": "A5: High pressure control PCB. E3: HP switch trip. U0: Low refrigerant. E7: Fan motor lock. U4: Indoor/outdoor comms. AH: Water pump fault.",
            "safety": "R410A system. Pressure test 42 bar. F-Gas handling certificate required.",
            "specs": "16-18kW @ -10°C. 70°C flow temp. Buffer tank recommended <radiators."
        },
        "VAM Air Handling": {
            "faults": "A9: EEV fault (expansion valve). C4: Liquid pipe thermistor. L5: Compressor overheat. U2: Voltage drop/phase loss. C9: Suction thermistor.",
            "safety": "HVAC Zone 1. Lockout/tagout for fan access. Belt guards mandatory.",
            "specs": "500-10,000 m³/h. FGAS <3kg exempt. Thermal wheel option."
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
        },
        "Duo-tec Combi HE": {
            "faults": "E160: Fan fault. E125: Pump overrun. E133: Ignition. E110: Overheat. E28: Flame rectification.",
            "safety": "Magnetic filter mandatory (warranty). System cleanse before install.",
            "specs": "24-40kW. 7yr heat exchanger warranty. Weather compensation ready."
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
        },
        "Vitocal 250-A": {
            "faults": "E7: Compressor error. 10: Flow temp sensor. 21: Return temp sensor. 92: HP switch. 0A: Communication fault.",
            "safety": "R407C refrigerant. Qualified F-Gas engineer. Pressure test 28 bar.",
            "specs": "11-13kW @ A7/W35. COP 4.6. EHPA approved. MCS certified."
        }
    },
    "Samsung": {
        "EHS Mono HT Quiet": {
            "faults": "E911: Low flow (<12 L/min). E101: Indoor/outdoor comms error. E912: Flow switch stuck. E121: Indoor temp sensor. E441: Discharge temp.",
            "safety": "R32 refrigerant. Room volume check. 2.5mm² min cable. RCD protection.",
            "specs": "12-16kW. 65°C flow temp. ErP A+++. 7yr compressor warranty."
        },
        "System 5 VRF": {
            "faults": "E202: Communication. 121: Temp sensor. 441: High discharge. 554: EEV fault. E102: Outdoor PCB.",
            "safety": "R410A. 3-phase supply. Earth bonding critical. Vibration isolators required.",
            "specs": "22.4-168kW. HR model heat recovery. BMS Modbus RTU."
        }
    },
    "Grant": {
        "Aerona³ R32": {
            "faults": "E02: Flow temp sensor. E03: Return sensor. E08: HP switch. E10: Compressor overheat. E13: Comm error.",
            "safety": "R32 A2L class. Installation cert required. Outdoor unit 300mm clearance.",
            "specs": "6-17kW. MCS certified. -20°C operation. Weather comp included."
        },
        "Vortex Eco Combi": {
            "faults": "Lockout: Reset after 1 hour. Nozzle: 0.40-0.75 USGPH. Pump pressure 7-10 bar. Photocell dirty.",
            "safety": "Oil tank 1.8m min from boiler. Fire valve mandatory. CO alarm KIWA approved.",
            "specs": "26-36kW. Kerosene C2. 90% efficiency. OFTEC registered installer."
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
        },
        "Adande Drawers": {
            "faults": "rPF: Probe failure. HA: High temp alarm. do: Door open >2 min. E1: NTC error. LS: Low speed compressor.",
            "safety": "R290 FLAMMABLE. No ignition sources. Service by Adande only. 1kg charge.",
            "specs": "-2/+10°C multi-temp. VCR compressor. 680mm depth. 5yr warranty."
        },
        "True Refrigeration": {
            "faults": "AL: Alarm condition. dF: Defrost mode. OP: Door open. Pr: Probe fault. HC: High condenser pressure.",
            "safety": "R290/R600a models - spark-free area. NSF certified. HACCP digital logs.",
            "specs": "Prep tables/cabinets. Self-close doors. 33-38°F holding temp."
        }
    },
    "Controls & BMS": {
        "Honeywell EvoHome": {
            "faults": "Battery low: Replace AAA x2. Zone not responding: 10m range check. Boiler relay clicking: Load 3A max. Binding failed: Factory reset.",
            "safety": "230V relay. Qualified electrician. Zone valves: Manual override test monthly.",
            "specs": "12 zones max. OpenTherm. WiFi 2.4GHz. iOS/Android app."
        },
        "Siemens RVL/RVP": {
            "faults": "Fault code: Long press OK. Sensor open circuit. Actuator 0-10V check. Modbus timeout: Termination resistor 120Ω.",
            "safety": "Mains powered. IP20 rating. Circuit breaker 6A Type B. Surge protection.",
            "specs": "Weather comp. Cascade control 16 boilers. BACnet/Modbus. Touchscreen HMI."
        },
        "Tado Smart Thermostat": {
            "faults": "E91: No power detected at relay. E92: Short circuit. E01: Calibration. Offline: Router 2.4GHz only.",
            "safety": "Wireless installer. Relay 230V 5A. Wall mounting 1.5m height. CR2032 battery backup.",
            "specs": "Geofencing. Multi-room. Heat pump compatible. Alexa/Google Home."
        }
    }
}

# === LEGAL DISCLAIMER (CRITICAL FOR MVP) ===
LEGAL_DISCLAIMER = """
### ⚠️ IMPORTANT LEGAL NOTICE

**This tool provides REFERENCE information only.**

**What this is NOT:**
- Professional engineering advice
- A replacement for Gas Safe/OFTEC certification
- A guarantee of accuracy
- Authorization to perform regulated work

**Your responsibilities:**
- You MUST hold valid UK certifications for regulated gas/refrigerant work
- You accept FULL liability for all work decisions
- You will comply with UK Gas Safety Regulations, F-Gas Regulations, and Building Regulations
- You understand AI content may contain errors

**Our liability:**
We accept NO liability for property damage, injury, death, or regulatory breaches from using this tool.

**BY CLICKING ACCEPT, YOU AGREE TO THESE TERMS.**
"""

# === MAIN APPLICATION ===
def main():
    # Header
    st.markdown("""
        <div class="app-header">
            <div class="app-title">HVAC Technical Documentation</div>
            <div class="app-subtitle">AI-Powered Fault Reference System</div>
        </div>
    """, unsafe_allow_html=True)
    
    # === STEP 1: LEGAL ACCEPTANCE ===
    if "legal_accepted" not in st.session_state:
        st.session_state.legal_accepted = False
    
    if not st.session_state.legal_accepted:
        st.markdown('<div class="legal-box">', unsafe_allow_html=True)
        st.markdown(LEGAL_DISCLAIMER)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("✅ I Accept - I Am a Qualified Engineer"):
            st.session_state.legal_accepted = True
            st.rerun()
        return
    
    # === STEP 2: PROFESSIONAL VERIFICATION ===
    if "verified" not in st.session_state:
        st.session_state.verified = False
    
    if not st.session_state.verified:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("Login")
        
        company = st.text_input("Your Company Name", placeholder="e.g., ABC Heating Services")
        access_key = st.text_input("Access Key", type="password", placeholder="Enter key")
        
        st.info("🔑 **Free Trial Key:** `TRIAL2026`")
        
        if st.button("Start Session"):
            if access_key in ["TRIAL2026", "HVAC2026"] and company:
                st.session_state.verified = True
                st.session_state.company = company
                st.session_state.access_level = "Trial"
                st.success("✅ Access Granted")
                st.rerun()
            else:
                st.error("Please enter company name and valid access key")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # === STEP 3: SAFETY CHECKLIST ===
    st.markdown("---")
    st.subheader("⚠️ Safety Verification")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ppe = st.checkbox("PPE Worn")
    with col2:
        loto = st.checkbox("Isolation Complete")
    with col3:
        risk = st.checkbox("Risk Assessment Done")
    
    if not (ppe and loto and risk):
        st.warning("Complete all safety checks to proceed")
        st.stop()
    else:
        st.markdown('<span class="badge-success">✓ SAFE TO WORK</span>', unsafe_allow_html=True)
    
    # === STEP 4: UNIT SELECTION ===
    st.markdown("---")
    st.subheader("Equipment Selection")
    
    tab1, tab2 = st.tabs(["Database Search", "Manual Entry"])
    
    selected_unit = ""
    context_data = {}
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Manufacturer", ["Select..."] + sorted(HVAC_DATABASE.keys()))
        
        if brand != "Select...":
            with col2:
                model = st.selectbox("Model", list(HVAC_DATABASE[brand].keys()))
            
            if model:
                selected_unit = f"{brand} {model}"
                context_data = HVAC_DATABASE[brand][model]
                
                # Display unit info
                st.info(f"**Selected:** {selected_unit}")
                if "safety" in context_data:
                    st.warning(f"⚠️ {context_data['safety']}")
    
    with tab2:
        custom_unit = st.text_area("Describe Equipment", placeholder="e.g., Remeha Quinta 45kW showing F.04 error", height=80)
        if custom_unit:
            selected_unit = f"Custom: {custom_unit}"
            context_data = {"faults": "General UK HVAC principles"}
    
    # === STEP 5: FAULT INPUT ===
    st.markdown("---")
    fault_input = st.text_area("Fault Description / Error Code", placeholder="e.g., F.22 displayed, radiators cold, pressure at 0.3 bar", height=100)
    
    # === STEP 6: AI ANALYSIS ===
    if st.button("Generate Technical Documentation"):
        if not selected_unit or not fault_input:
            st.error("Please select equipment and describe the fault")
            return
        
        # API Key Check
        if not st.secrets.get("ANTHROPIC_API_KEY"):
            st.error("API Configuration Error - Contact Support")
            return
        
        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            
            # Build context
            context_text = ""
            if context_data:
                if "faults" in context_data:
                    context_text += f"Known Faults: {context_data['faults']}\n"
                if "safety" in context_data:
                    context_text += f"Safety Data: {context_data['safety']}\n"
                if "specs" in context_data:
                    context_text += f"Specifications: {context_data['specs']}\n"
            
            # AI Prompt
            prompt = f"""You are a UK Gas Safe registered HVAC engineer with 15+ years field experience.

EQUIPMENT: {selected_unit}
TECHNICAL DATA: {context_text if context_text else "Limited data - use UK HVAC best practices"}
FAULT REPORTED: {fault_input}

Provide a TECHNICAL REFERENCE in this format:

**LIKELY CAUSE:**
[One clear sentence explaining what's probably wrong]

**INVESTIGATION STEPS:**
1. [First check - most common cause]
2. [Second check]
3. [Third check]
4. [Fourth check]
5. [Fifth check - if needed]

**SAFETY WARNINGS:**
- [Specific hazards for this equipment - gas, electrical, pressure, refrigerant]

**PARTS LIKELY NEEDED:**
- [List 2-4 common parts with part numbers if known]

**UK COMPLIANCE:**
[Relevant regulations: Gas Safety Regs, F-Gas, Building Regs Part L, BS standards]

Keep it practical and field-ready. This is a REFERENCE for a qualified engineer."""

            with st.spinner("Analyzing fault..."):
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result_text = response.content[0].text
                
                # Display Results
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(f"### Technical Documentation")
                st.markdown(f"**Equipment:** {selected_unit}")
                st.markdown(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"**Company:** {st.session_state.company}")
                st.markdown("---")
                st.markdown(result_text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Save to session
                st.session_state.last_result = result_text
                st.session_state.last_unit = selected_unit
                
                # === JOB LOG EXPORT ===
                st.markdown("---")
                st.subheader("Export Job Report")
                
                col1, col2 = st.columns(2)
                with col1:
                    job_ref = st.text_input("Job Reference", placeholder="JOB-001")
                with col2:
                    customer = st.text_input("Customer", placeholder="Client name")
                
                notes = st.text_area("Additional Notes", placeholder="Engineer observations...", height=60)
                
                if st.button("Download Report"):
                    report = f"""HVAC TECHNICAL DOCUMENTATION REPORT
{'='*50}
Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Company: {st.session_state.company}
Job Ref: {job_ref}
Customer: {customer}

EQUIPMENT: {selected_unit}
FAULT: {fault_input}

{'='*50}
TECHNICAL ANALYSIS:
{'='*50}
{result_text}

{'='*50}
ENGINEER NOTES:
{notes if notes else 'None'}

{'='*50}
DISCLAIMER: Reference tool only. Engineer accepts 
full responsibility for all work performed.
{'='*50}
                    """
                    
                    st.download_button(
                        label="Download Report (.txt)",
                        data=report,
                        file_name=f"HVAC_{job_ref}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                    st.success("Report ready")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # === FOOTER ===
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6c757d; font-size: 13px; padding: 15px;'>
            HVAC Technical Documentation | Reference Tool Only | Not a substitute for professional training
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
