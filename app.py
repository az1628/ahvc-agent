import streamlit as st
import anthropic
from datetime import datetime

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="HVAC Docu-Fix Pro",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === DARK MODE CSS ===
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    p, h1, h2, h3, li, span, label { color: #f8fafc !important; }
    .app-header {
        background-color: #1e293b;
        padding: 25px;
        margin: -65px -65px 25px -65px;
        border-bottom: 3px solid #3b82f6;
        text-align: center;
    }
    .header-title { font-size: 26px; font-weight: 800; color: #ffffff !important; margin: 0; }
    .header-sub { font-size: 13px; color: #94a3b8 !important; margin-top: 5px; text-transform: uppercase; }
    .module-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .stSelectbox div[data-baseweb="select"] div, .stTextInput input, .stTextArea textarea {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
    }
    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white !important;
        font-weight: 700;
        border-radius: 8px;
        height: 52px;
    }
    .result-box {
        background-color: #0f172a;
        border-left: 6px solid #3b82f6;
        padding: 25px;
        border-radius: 8px;
        margin-top: 20px;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# === DATA ENGINE ===
HVAC_DATABASE = {
    "Vaillant": {
        "aroTHERM Plus (R290)": {"faults": "F.022: Low Water. F.718: Fan. F.729: Low Temp."},
        "ecoTEC plus/pro": {"faults": "F.28: Ignition. F.75: Pressure. F.22: Dry Fire."}
    },
    "Mitsubishi Electric": {
        "Ecodan": {"faults": "U1: High Pressure. L9: Flow Rate. P6: Overheat."}
    },
    "Worcester Bosch": {
        "Greenstar 4000": {"faults": "EA: No Flame. E9: Overheat. C6: Fan."}
    }
}

def main():
    st.markdown('<div class="app-header"><div class="header-title">HVAC DOCU-FIX PRO</div><div class="header-sub">Technical Reference & Audit Guide</div></div>', unsafe_allow_html=True)

    # Auth
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        key = st.text_input("Site License Key", type="password")
        if st.button("Unlock Documentation"):
            if key == "TECH2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Invalid Key")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Equipment Selection
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    c_brand, c_model = st.columns(2)
    with c_brand:
        brand = st.selectbox("Manufacturer", ["Select Brand..."] + sorted(list(HVAC_DATABASE.keys())))
    
    selected_unit = ""
    if brand != "Select Brand...":
        with c_model:
            model = st.selectbox("Model Series", sorted(list(HVAC_DATABASE[brand].keys())))
            selected_unit = f"{brand} {model}"
    
    fault_desc = st.text_area("Fault Description / Error Codes")
    
    if st.button("🚀 GET TECHNICAL GUIDANCE"):
        if not selected_unit or not fault_desc:
            st.error("Please select a unit and describe the fault.")
        else:
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
            if not api_key:
                st.error("API Key missing in Secrets.")
                return
            
            client = anthropic.Anthropic(api_key=api_key)
            
            with st.spinner("Analyzing Manufacturer Data..."):
                try:
                    # UPDATED MODEL STRING AND ERROR HANDLING
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514", # Changed to 'latest' alias
                        max_tokens=800,
                        messages=[{"role": "user", "content": f"Expert HVAC Engineer advice for {selected_unit}. Fault: {fault_desc}"}]
                    )
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(response.content[0].text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except anthropic.NotFoundError:
                    st.error("Model Error: The system could not find the specified AI model. Try using 'claude-3-sonnet-20240229'.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
