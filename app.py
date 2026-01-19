import streamlit as st
import anthropic
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import httpx

# Page Config
st.set_page_config(page_title="HVAC Documentation Tool", page_icon="🔧", layout="centered")

# Dark Mode CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    *, p, span, div, label, h1, h2, h3 {
        color: #ffffff !important;
    }
    
    .header {
        background-color: #2b5797;
        padding: 30px;
        text-align: center;
        margin: -70px -70px 40px -70px;
    }
    .header h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 32px;
    }
    
    .stButton>button {
        background-color: #2b5797;
        color: #ffffff !important;
        width: 100%;
        padding: 12px;
        font-size: 16px;
        border-radius: 5px;
        border: none;
        font-weight: 600;
    }
    
    .result {
        background-color: #2a2a2a;
        padding: 30px;
        border-radius: 8px;
        margin: 20px 0;
        border: 2px solid #444;
        color: #ffffff !important;
    }
    
    input, textarea, select {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid #555 !important;
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# HVAC Database
HVAC_DATABASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": "F.022: Low pressure (<0.6 bar). F.718: Fan blocked. F.729: Compressor discharge <0°C. R290 FLAMMABLE. 1m exclusion zone required.",
        "ecoTEC plus 825/835": "F.22: Dry fire (low pressure). F.28: Ignition lockout. F.75: Pump circulation fault. F.29: Flame loss. Gas Safe engineer only.",
        "flexoTHERM exclusive": "701: Brine/water flow error. 702: Ground source sensor fault. 704: Evaporator NTC error. Glycol antifreeze toxic."
    },
    "Worcester Bosch": {
        "Greenstar 4000/8000": "EA/224: Ignition fault. E9/227: Overheat >95°C. C6: Fan speed error. A1: Pump blocked. 227: Flame detection. Ventilation critical.",
        "GB162 Commercial": "227: Ignition lockout (3 attempts). 216: Fan underspeed. 224: Overheat >105°C. Commercial ticket required.",
        "Greenstar Highflow CDi": "E9: DHW overheat. EA: Ignition fail. A7: Diverter valve stuck. G3 ticket required for unvented."
    },
    "Mitsubishi Electric": {
        "Ecodan R290 Monobloc": "U1: High pressure/Low flow. L9: Abnormal flow rate. P6: Overheat protection. R290 FLAMMABLE - spark-free tools only.",
        "City Multi VRF R32": "4115: Discharge temp >115°C. 1500: Refrigerant overcharge. 1102: Discharge thermistor. R32 mildly flammable (A2L).",
        "Mr Slim PEA Wall Units": "E6: Indoor/outdoor comms. E1: Indoor PCB. E3: High pressure switch. E7: Fan motor lock. R32 room volume check mandatory."
    },
    "Daikin": {
        "Altherma 3 H HT": "A5: High pressure control PCB. E3: HP switch trip. U0: Low refrigerant. E7: Fan motor lock. R410A system. Pressure test 42 bar.",
        "VAM Air Handling": "A9: EEV fault (expansion valve). C4: Liquid pipe thermistor. L5: Compressor overheat. U2: Voltage drop/phase loss."
    },
    "Baxi": {
        "800 Combi": "E119: Low pressure (<0.5 bar). E133: Gas supply/ignition. E110: Overheat stat. E125: Pump blockage. Ventilation per BS 5440.",
        "Assure Commercial": "E01: No flame detected. E03: Fan fault. E09: Safety stat. E28: Flame loss. Commercial gas ticket required.",
        "Duo-tec Combi HE": "E160: Fan fault. E125: Pump overrun. E133: Ignition. E110: Overheat. Magnetic filter mandatory for warranty."
    },
    "Ideal": {
        "Logic Max Combi": "F1: Low pressure (<0.5 bar). F2: Flame loss. L2: Ignition lockout (6 tries). F3: Fan fault. 25mm copper required on gas.",
        "Evomax 2 System": "L1: No flow detected. L2: Ignition lockout. FU: Delta-T fault >50°C. F3: Fan underspeed. Low NOx Class 6."
    },
    "Viessmann": {
        "Vitodens 100/200": "F2: Burner overheat. F4: No flame signal. F9: Fan speed too low. F5: External error. Condensate pH <4. Neutralizer required.",
        "Vitocal 250-A": "E7: Compressor error. 10: Flow temp sensor. 21: Return temp sensor. 92: HP switch. R407C refrigerant. F-Gas engineer required."
    },
    "Samsung": {
        "EHS Mono HT Quiet": "E911: Low flow (<12 L/min). E101: Indoor/outdoor comms error. E912: Flow switch stuck. R32 refrigerant. Room volume check.",
        "System 5 VRF": "E202: Communication. 121: Temp sensor. 441: High discharge. 554: EEV fault. R410A. 3-phase supply. Earth bonding critical."
    },
    "Grant": {
        "Aerona³ R32": "E02: Flow temp sensor. E03: Return sensor. E08: HP switch. E10: Compressor overheat. R32 A2L class. Installation cert required.",
        "Vortex Eco Combi": "Lockout: Reset after 1 hour. Nozzle: 0.40-0.75 USGPH. Pump pressure 7-10 bar. Oil tank 1.8m min from boiler."
    },
    "Commercial Refrigeration": {
        "Williams Multideck": "HI: High temp alarm. CL: Condenser blocked. E1: Air probe fail. E16: HP alarm. R404A/R448A. F-Gas record keeping.",
        "Foster EcoShow": "hc: High condenser temp. hP: High pressure trip. dEF: Defrost active. LS: Low superheat. HFC refrigerant. HACCP compliance.",
        "Adande Drawers": "rPF: Probe failure. HA: High temp alarm. do: Door open >2 min. R290 FLAMMABLE. No ignition sources. Service by Adande only.",
        "True Refrigeration": "AL: Alarm condition. dF: Defrost mode. OP: Door open. Pr: Probe fault. HC: High condenser pressure. NSF certified."
    }
}

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "legal_accepted" not in st.session_state:
    st.session_state.legal_accepted = False

# Header
st.markdown('<div class="header"><h1>HVAC Documentation Tool</h1></div>', unsafe_allow_html=True)

# Legal Disclaimer
if not st.session_state.legal_accepted:
    st.markdown("### ⚠️ Legal Notice")
    st.warning("""
**This is a REFERENCE TOOL ONLY**

- NOT professional engineering advice
- NOT a substitute for Gas Safe/OFTEC certification  
- NOT a guarantee of accuracy
- You MUST hold valid UK certifications for regulated work
- You accept FULL liability for all work decisions
- AI content may contain errors

**We accept NO liability for property damage, injury, or death from using this tool.**
    """)
    
    if st.button("I Accept - I Am a Qualified Engineer"):
        st.session_state.legal_accepted = True
        st.rerun()
    st.stop()

# Login
if not st.session_state.authenticated:
    st.markdown("### Login")
    
    company = st.text_input("Company Name", placeholder="Your company name")
    trial_key = st.text_input("Trial Key", type="password", placeholder="Enter trial key")
    
    st.info("**Free Trial Key:** TRIAL2026")
    
    if st.button("Access Tool"):
        if trial_key == "TRIAL2026" and company:
            st.session_state.authenticated = True
            st.session_state.company = company
            st.rerun()
        else:
            st.error("Invalid trial key or missing company name")
    st.stop()

# Equipment Selection
st.markdown(f"**Company:** {st.session_state.company}")
st.markdown("---")
st.markdown("### Select Equipment")

col1, col2 = st.columns(2)
with col1:
    brand = st.selectbox("Manufacturer", ["Select..."] + sorted(HVAC_DATABASE.keys()))

if brand != "Select...":
    with col2:
        model = st.selectbox("Model", list(HVAC_DATABASE[brand].keys()))
else:
    model = None

# Fault Input
st.markdown("### Describe the Fault")
fault = st.text_area("Fault Description / Error Code", 
                     placeholder="e.g., F.22 error showing, radiators cold, pressure at 0.3 bar",
                     height=100)

# Generate Documentation
if st.button("Generate Documentation"):
    if not model or not fault:
        st.error("Please select a model and describe the fault")
    else:
        if not st.secrets.get("ANTHROPIC_API_KEY"):
            st.error("API key not configured. Add ANTHROPIC_API_KEY to Streamlit secrets.")
            st.stop()
        
        selected_unit = f"{brand} {model}"
        context = HVAC_DATABASE[brand][model]
        
        # Create HTTP client without proxy
        http_client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=True
        )
        
        # Create Anthropic client
        client = anthropic.Anthropic(
            api_key=st.secrets["ANTHROPIC_API_KEY"],
            http_client=http_client
        )
        
        prompt = f"""You are a UK HVAC engineer with 15+ years experience.

EQUIPMENT: {selected_unit}
KNOWN FAULTS: {context}
REPORTED FAULT: {fault}

Provide a technical reference in this format:

LIKELY CAUSE:
[One sentence explaining the problem]

INVESTIGATION STEPS:
1. [First check]
2. [Second check]
3. [Third check]
4. [Fourth check]
5. [Fifth check]

SAFETY:
[Key safety warnings for this equipment]

PARTS NEEDED:
[List 2-4 likely parts]

UK COMPLIANCE:
[Relevant regulations]

Keep it practical and field-ready."""

        with st.spinner("Generating documentation..."):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1200,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            
            # Display result
            st.markdown('<div class="result">', unsafe_allow_html=True)
            st.markdown("## Technical Documentation")
            st.markdown(f"**Equipment:** {selected_unit}")
            st.markdown(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            st.markdown(f"**Company:** {st.session_state.company}")
            st.markdown("---")
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download section
            st.markdown("### Download Report")
            job_ref = st.text_input("Job Reference (optional)", placeholder="JOB-001")
            
            # Text report
            report_txt = f"""HVAC TECHNICAL DOCUMENTATION
{'='*50}
Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Company: {st.session_state.company}
Job Reference: {job_ref if job_ref else 'N/A'}

Equipment: {selected_unit}
Fault: {fault}

{'='*50}
{result}

{'='*50}
DISCLAIMER: Reference tool only. Engineer accepts 
full responsibility for work performed.
{'='*50}
"""
            
            # PDF generation function
            def create_pdf(content, equipment, company, job_ref):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)
                heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, spaceBefore=12)
                normal_style = styles['BodyText']
                
                story = []
                
                # Title
                story.append(Paragraph("HVAC TECHNICAL DOCUMENTATION", title_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Header info
                story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
                story.append(Paragraph(f"<b>Company:</b> {company}", normal_style))
                story.append(Paragraph(f"<b>Job Reference:</b> {job_ref if job_ref else 'N/A'}", normal_style))
                story.append(Paragraph(f"<b>Equipment:</b> {equipment}", normal_style))
                story.append(Paragraph(f"<b>Fault:</b> {fault}", normal_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Content
                for line in content.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line.replace('\n', '<br/>'), normal_style))
                        story.append(Spacer(1, 0.1*inch))
                
                story.append(Spacer(1, 0.5*inch))
                
                # Disclaimer
                disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['BodyText'], fontSize=9, alignment=TA_CENTER)
                story.append(Paragraph("DISCLAIMER: Reference tool only. Engineer accepts full responsibility for work performed.", disclaimer_style))
                
                doc.build(story)
                buffer.seek(0)
                return buffer
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📄 Download TXT",
                    report_txt,
                    file_name=f"HVAC_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                pdf_buffer = create_pdf(result, selected_unit, st.session_state.company, job_ref)
                st.download_button(
                    "📕 Download PDF",
                    pdf_buffer,
                    file_name=f"HVAC_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )

st.markdown("---")
st.markdown("<div style='text-align: center; color: #aaa; font-size: 13px;'>HVAC Documentation Tool | Reference Only</div>", unsafe_allow_html=True)
