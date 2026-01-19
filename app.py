import streamlit as st
import anthropic
import base64

# 1. LEGAL SHIELD - MANDATORY OVERLAY
st.set_page_config(page_title="HVAC Expert AI", layout="centered")
if "legal_accepted" not in st.session_state:
    st.error("⚠️ LEGAL DISCLAIMER")
    st.write("This AI is a documentation tool for GAS SAFE REGISTERED ENGINEERS ONLY. It is not a substitute for professional judgment. Use at your own risk.")
    if st.button("I am a Qualified Engineer & I Accept Responsibility"):
        st.session_state.legal_accepted = True
        st.rerun()
    st.stop()

# 2. AUTHENTICATION (The "Company Gate")
access_code = st.sidebar.text_input("Enter Company Access Code", type="password")
if access_code != "UK-HVAC-2026": # Change this for your first client
    st.info("Please enter your company access code to begin.")
    st.stop()

st.title("🛠️ UK HVAC Field Agent")

# 3. RAG/KNOWLEDGE BASE (Simplified for MVP)
# In production, move these to text files in your GitHub repo
KNOWLEDGE_CONTEXT = """
VAILLANT AROTHERM PLUS: Error F.22 = Low water pressure. Fix: Check expansion vessel, fill to 1.5 bar.
MITSUBISHI ECODAN: Error L9 = Flow rate error. Fix: Check pump speed and strainer.
WILLIAMS REFRIGERATION: Controller 'Hi' alarm = Condenser blocked. Fix: Clean fins with soft brush.
"""

# 4. VISION UPLOAD
uploaded_file = st.file_uploader("Upload Image/Video of Unit or Error Code", type=["jpg", "png", "mp4"])

if uploaded_file:
    st.success("File Received. Analyzing...")
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
    # Logic to send to Claude 3.5 Sonnet
    # (Simplified for the 2-hour window - using text-based reasoning for MVP)
    if st.button("Generate Field SOP"):
        with st.spinner("Consulting Technical Manuals..."):
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=f"You are a UK Senior HVAC Engineer. Use this context: {KNOWLEDGE_CONTEXT}",
                messages=[{"role": "user", "content": "The technician is looking at a unit. Identify the brand and provide a 5-step SOP including PPE and Safety Warnings."}]
            )
            st.markdown(response.content[0].text)
            st.download_button("Export as Job Report", response.content[0].text, file_name="Job_Report.txt")
