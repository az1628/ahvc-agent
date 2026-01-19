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
    /* Corporate HVAC Theme - Clean & Professional */
    .stApp { 
        background-color: #f5f7fa;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 25px 20px;
        margin: -60px -60px 30px -60px;
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .app-title {
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .app-subtitle {
        font-size: 13px;
        color: #cbd5e1;
        margin-top: 5px;
        font-weight: 400;
    }
    
    /* Buttons - Corporate Blue */
    .stButton>button {
        width: 100%;
        background-color: #1e40af;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Info Cards */
    .info-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #1e40af;
        padding: 20px;
        border-radius: 6px;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        margin: 5px 5px 5px 0;
        text-transform: uppercase;
    }
    .badge-success { background: #10b981; color: white; }
    .badge-warning { background: #f59e0b; color: white; }
    .badge-info { background: #3b82f6; color: white; }
    
    /* Legal Disclaimer Box */
    .legal-box {
        background: #fef2f2;
        border: 2px solid #dc2626;
        border-radius: 6px;
        padding: 20px;
        margin: 20px 0;
        font-size: 13px;
        color: #991b1b;
        line-height: 1.6;
    }
    
    /* Results Container */
    .result-box {
        background: white;
        border-radius: 6px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    /* Input Fields - Better Contrast */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background-color: white;
        border: 1.5px solid #cbd5e1;
        color: #1e293b;
        font-size: 14px;
    }
    
    /* Section Headers */
    h2, h3 {
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Improve text readability */
    p, li, label {
        color: #334155;
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
⚖️ **IMPORTANT LEGAL NOTICE - READ BEFORE USE**

**This tool provides reference information only and does NOT constitute:**
- Professional engineering advice or instruction
- A substitute for qualified Gas Safe/OFTEC/F-Gas certification
- Warranty or guarantee of diagnosis accuracy
- Authorization to perform regulated gas/refrigerant work

**User Responsibilities:**
1. You MUST hold valid UK certifications (Gas Safe/OFTEC/F-Gas) for regulated work
2. You accept full liability for all installation, repair, and safety decisions
3. You will comply with Building Regulations Part L, Gas Safety Regulations 1998, and F-Gas Regulations 2015
4. You acknowledge AI-generated content may contain errors

**Liability Limitation:**
The provider accepts NO liability for property damage, injury, death, regulatory breaches, or business losses arising from use of this tool. Use at your own risk.

**Data Privacy:** Session data is not stored. No personal information is collected.

BY CLICKING "I ACCEPT", YOU AGREE TO THESE TERMS.
"""

# === MAIN APPLICATION ===
def main():
    # Header
    st.markdown("""
        <div class="app-header">
            <div class="app-title">🔧 HVAC DocPro</div>
            <div class="app-subtitle">Technical Documentation Assistant for UK Engineers</div>
        </div>
    """, unsafe_allow_html=True)
    
    # === STEP 1: LEGAL ACCEPTANCE ===
    if "legal_accepted" not in st.session_state:
        st.session_state.legal_accepted = False
    
    if not st.session_state.legal_accepted:
        st.markdown('<div class="legal-box">', unsafe_allow_html=True)
        st.markdown(LEGAL_DISCLAIMER)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✅ I Accept - I Am Qualified"):
                st.session_state.legal_accepted = True
                st.rerun()
        return
    
    # === STEP 2: PROFESSIONAL VERIFICATION ===
    if "verified" not in st.session_state:
        st.session_state.verified = False
    
    if not st.session_state.verified:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("🔐 Access HVAC DocPro")
        
        company = st.text_input("Company / Business Name", placeholder="e.g., Smith Heating Ltd")
        access_key = st.text_input("Access Key", type="password", placeholder="Enter your access key")
        
        st.info("💡 **Free Trial Key:** `TRIAL2026` | For full license, contact: sales@hvac-docpro.uk")
        
        if st.button("🚀 Start Session"):
            if access_key in ["TRIAL2026", "HVAC2026"] and company:
                st.session_state.verified = True
                st.session_state.company = company
                st.session_state.access_level = "Trial" if access_key == "TRIAL2026" else "Beta"
                st.success("✅ Access Granted")
                st.rerun()
            else:
                st.error("❌ Please enter your company name and a valid access key")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # === STEP 3: SAFETY CHECKLIST ===
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.subheader("⚠️ Pre-Work Safety Verification")
    st.caption("Complete before accessing diagnostic information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ppe = st.checkbox("PPE Worn", help="Safety boots, gloves, glasses")
    with col2:
        loto = st.checkbox("Isolation Done", help="Gas/electrical isolation confirmed")
    with col3:
        risk = st.checkbox("Risk Assessed", help="Site hazards identified")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not (ppe and loto and risk):
        st.warning("⚠️ Complete all safety checks to proceed")
        st.stop()
    else:
        st.markdown('<span class="badge badge-success">✓ SAFE TO WORK</span>', unsafe_allow_html=True)
    
    # === STEP 4: UNIT SELECTION ===
    st.markdown("---")
    st.subheader("📋 Equipment Documentation Lookup")
    
    tab1, tab2 = st.tabs(["🔍 Database Search", "✍️ Manual Entry"])
    
    selected_unit = ""
    context_data = {}
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox(
                "Manufacturer",
                ["Select Brand..."] + sorted(HVAC_DATABASE.keys()),
                help="Choose equipment manufacturer"
            )
        
        if brand != "Select Brand...":
            with col2:
                model = st.selectbox(
                    "Model / Series",
                    list(HVAC_DATABASE[brand].keys()),
                    help="Select specific model"
                )
            
            if model:
                selected_unit = f"{brand} {model}"
                context_data = HVAC_DATABASE[brand][model]
                
                # Display unit info
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                st.markdown(f"**Selected:** {selected_unit}")
                if "specs" in context_data:
                    st.caption(f"📊 Specs: {context_data['specs']}")
                if "safety" in context_data:
                    st.warning(f"⚠️ Safety: {context_data['safety']}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        custom_unit = st.text_area(
            "Describe Equipment",
            placeholder="e.g., Remeha Quinta 45kW commercial boiler, showing F.04 error",
            height=100
        )
        if custom_unit:
            selected_unit = f"Custom: {custom_unit}"
            context_data = {"faults": "General UK HVAC principles - verification required on-site"}
    
    # === STEP 5: FAULT INPUT ===
    st.markdown("---")
    fault_input = st.text_area(
        "🛠️ Fault Description / Error Code",
        placeholder="Describe symptoms, error codes, unusual behavior...\ne.g., 'F.22 displayed, radiators cold, pressure gauge at 0.3 bar'",
        height=100
    )
    
    # === STEP 6: AI ANALYSIS ===
    if st.button("🔍 Generate Technical Documentation", type="primary"):
        if not selected_unit or not fault_input:
            st.error("❌ Please select equipment and describe the fault")
            return
        
        # API Key Check
        if not st.secrets.get("ANTHROPIC_API_KEY"):
            st.error("🔴 API Configuration Error - Contact Administrator")
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
            prompt = f"""You are a UK Gas Safe registered senior HVAC engineer with 20+ years experience.

EQUIPMENT: {selected_unit}
CONTEXT DATA: {context_text if context_text else "Limited data - use general UK HVAC principles"}
REPORTED FAULT: {fault_input}

Provide a PROFESSIONAL TECHNICAL REFERENCE (not instructions) formatted as:

🔍 DIAGNOSIS:
[One-sentence likely cause]

🛠️ TECHNICAL REFERENCE:
[5-7 numbered investigation steps a qualified engineer would follow]

⚠️ CRITICAL SAFETY NOTES:
[Specific hazards for THIS equipment - gas, electrical, refrigerant, pressure]

📋 COMPLIANCE REFERENCES:
[Relevant UK regulations: Gas Safety (Installation & Use) Regs 1998, BS standards, F-Gas, Building Regs Part L]

🔧 PARTS COMMONLY REQUIRED:
[List 3-5 potential parts with typical part numbers if known]

IMPORTANT: Frame as reference documentation, NOT as instructions. Assume reader is qualified."""

            with st.spinner("🤖 Analyzing fault data..."):
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result_text = response.content[0].text
                
                # Display Results
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(f"### 📄 Technical Documentation")
                st.markdown(f"**Equipment:** {selected_unit}")
                st.markdown(f"**Generated:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"**Company:** {st.session_state.company} | **Access:** {st.session_state.access_level}")
                st.markdown("---")
                st.markdown(result_text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Save to session
                st.session_state.last_result = result_text
                st.session_state.last_unit = selected_unit
                
                # === JOB LOG EXPORT ===
                st.markdown("---")
                st.subheader("💾 Job Documentation")
                
                col1, col2 = st.columns(2)
                with col1:
                    job_ref = st.text_input("Job Reference", placeholder="JOB-2026-001")
                with col2:
                    customer = st.text_input("Customer Name", placeholder="Site/Client")
                
                notes = st.text_area("Engineer Notes", placeholder="Additional observations...", height=80)
                
                if st.button("📥 Download Job Report"):
                    report = f"""
HVAC DOCPRO - TECHNICAL DOCUMENTATION REPORT
{'='*60}
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Company: {st.session_state.company}
Access Level: {st.session_state.access_level}
Job Reference: {job_ref}
Customer: {customer}

EQUIPMENT: {selected_unit}
REPORTED FAULT: {fault_input}

{'='*60}
TECHNICAL ANALYSIS:
{'='*60}
{result_text}

{'='*60}
ENGINEER NOTES:
{notes if notes else 'None recorded'}

{'='*60}
LEGAL DISCLAIMER:
This document is a reference tool only. All work must be performed 
by qualified personnel in accordance with UK regulations. The engineer 
accepts full responsibility for all work carried out.
{'='*60}
                    """
                    
                    st.download_button(
                        label="💾 Download PDF Report",
                        data=report,
                        file_name=f"HVAC_Report_{job_ref}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                    st.success("✅ Report ready for download")
        
        except Exception as e:
            st.error(f"🔴 Error: {str(e)}")
            st.info("Please check your API configuration and try again")
    
    # === FOOTER ===
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #64748b; font-size: 12px; padding: 20px;'>
            <b>HVAC DocPro</b> | AI-Powered Technical Reference | <span class='badge badge-info'>MVP Beta</span><br>
            Not a substitute for professional training | © 2026
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
