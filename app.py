# app.py — Updated UI/UX, single color #13349b, fixes double-click behavior.
import streamlit as st
import fitz  # PyMuPDF
import requests
import hashlib
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from db import init_db, register_user, login_user, save_upload, get_user_history
from gtts import gTTS   # 🎤 Voice summary

# Load Hugging Face token
try:
    hf_token = st.secrets["HF_TOKEN"]
except Exception:
    hf_token = ""

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalLite", layout="wide", page_icon="⚖️")

# --- THEME & CUSTOM CSS ---
PRIMARY = "#13349b"
ACCENT = "#13349b"
TEXT = "#0f172a"
BACKGROUND = "#f7f9ff"

st.markdown(
    f"""
    <style>
    :root {{
      --primary: {PRIMARY};
      --accent: {ACCENT};
      --text: {TEXT};
      --bg: {BACKGROUND};
    }}
    /* Page background and font */
    .stApp {{
      background: linear-gradient(180deg, var(--bg) 0%, #ffffff 100%);
      color: var(--text);
      animation: pageFade 600ms ease both;
    }}
    @keyframes pageFade {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Header */
    .logo-anim {{
      display:inline-block;
      transform-origin:center;
      animation: logoPulse 2400ms ease-in-out infinite;
    }}
    @keyframes logoPulse {{
      0% {{ transform: scale(1); }}
      50% {{ transform: scale(1.02); }}
      100% {{ transform: scale(1); }}
    }}

    /* Buttons */
    button[role="button"] {{
      background: var(--primary) !important;
      color: white !important;
      border-radius: 10px !important;
      padding: 10px 14px !important;
      box-shadow: 0 6px 18px rgba(19,52,155,0.08);
      border: none !important;
      transition: transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
      font-weight: 600;
    }}
    button[role="button"]:hover {{
      transform: translateY(-3px) scale(1.01);
      box-shadow: 0 12px 28px rgba(19,52,155,0.12);
      cursor: pointer;
    }}
    button[role="button"]:active {{
      transform: translateY(0px) scale(0.995);
      opacity: 0.98;
    }}

    /* Inputs & textareas */
    input, textarea {{
      border-radius: 10px !important;
      padding: 10px !important;
      border: 1px solid rgba(19,52,155,0.12) !important;
      box-shadow: none !important;
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
      transition: box-shadow 140ms ease, transform 140ms ease;
    }}
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
      box-shadow: 0 6px 18px rgba(19,52,155,0.08);
      transform: translateY(-2px);
      outline: none;
      border-color: var(--primary) !important;
    }}

    /* Cards / containers */
    .stContainer, .stExpander {{
      border-radius: 12px;
      padding: 12px;
      transition: transform 200ms ease, box-shadow 200ms ease;
    }}
    .stExpander:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(19,52,155,0.05);
    }}

    /* Sidebar tweaks */
    .css-1d391kg .css-1d391kg {{
      color: var(--text);
    }}

    /* Tiny footer */
    footer {{
      color: #666;
      font-size: 12px;
    }}

    /* Make download buttons consistent */
    .stDownloadButton>button {{
      border-radius: 10px !important;
      background: var(--primary) !important;
      color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER BRANDING ---
st.markdown(
    f"<h1 style='text-align:center; color: var(--text); margin-bottom:6px;'><span class='logo-anim'>⚖️</span> <span style='color: {PRIMARY};'>LegalLite</span></h1>",
    unsafe_allow_html=True,
)

# --- SESSION STATE INIT ---
base_keys = [
    "logged_in", "user_email", "mode", "api_key", "mode_chosen",
    # button flags to avoid double-click issues
    "btn_login", "btn_signup", "btn_demo", "btn_api_mode", "btn_hf",
    "btn_continue_api", "btn_back", "btn_logout", "btn_simplify",
    "btn_run_ai_risk"
]
for key in base_keys:
    if key not in st.session_state:
        st.session_state[key] = False if key.startswith("btn_") or key == "logged_in" else ""

# --- UTILITY ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_pdf(summary_text, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    margin = 40
    y = height - margin

    c.drawString(margin, y, f"LegalLite Summary - {filename}")
    y -= 20
    c.drawString(margin, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    lines = summary_text.split('\n')
    for line in lines:
        for subline in [line[i:i+90] for i in range(0, len(line), 90)]:
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - margin
            c.drawString(margin, y, subline)
            y -= 20

    c.save()
    buffer.seek(0)
    return buffer
    
# 🎤 --- VOICE SUMMARY ---
def generate_voice(summary_text):
    try:
        tts = gTTS(summary_text, lang='en')
        audio_path = "summary_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"❌ Voice generation failed: {e}")
        return None
        
# --- HUGGING FACE API WRAPPER ---
@st.cache_data
def query_huggingface_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/csebuetnlp/mT5_multilingual_XLSum"
    headers = {"Authorization": f"Bearer {hf_token}"}

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {"max_length": 200, "do_sample": False},
            "options": {"wait_for_model": True}
        })
        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        output = response.json()
        if isinstance(output, list) and len(output) > 0:
            return output[0].get("summary_text", str(output[0]))
        if isinstance(output, dict) and "summary_text" in output:
            return output["summary_text"]
        else:
            return f"⚠️ Unexpected output: {output}"

    except Exception as e:
        return f"❌ Exception: {str(e)}"

# Helper to set button flags (used as on_click)
def _set_flag(key):
    st.session_state[key] = True

# --- LOGIN SECTION ---
def login_section():
    with st.container():
        st.subheader("🔐 Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        st.button("Login", key="login_btn_ui", on_click=_set_flag, args=("btn_login",))
        # perform action after render if flag set
        if st.session_state.get("btn_login"):
            st.session_state["btn_login"] = False
            user = login_user(email, hash_password(password))
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success(f"Welcome back, {email}!")
            else:
                st.error("Invalid email or password.")

# --- MODE SELECTION ---
def choose_mode():
    st.markdown("### 🎛️ Choose how you'd like to use LegalLite:")
    st.markdown("Pick a mode based on your preference:")

    col1, col2, col3 = st.columns(3)

    # initialize a session variable to hold temporary API input
    if "api_input" not in st.session_state:
        st.session_state.api_input = ""

    with col1:
        st.button("🧪 Demo Mode", key="demo_btn_ui", on_click=_set_flag, args=("btn_demo",))
        if st.session_state.get("btn_demo"):
            st.session_state["btn_demo"] = False
            st.session_state.mode = "Demo Mode"
            st.session_state.mode_chosen = True

    with col2:
        st.button("🔐 Use Your API Key", key="api_btn_ui", on_click=_set_flag, args=("btn_api_mode",))
        if st.session_state.get("btn_api_mode"):
            st.session_state["btn_api_mode"] = False
            st.session_state.mode = "Use Your Own OpenAI API Key"
            st.session_state.mode_chosen = False  # wait for key entry

    with col3:
        st.button("🌐 Hugging Face", key="hf_btn_ui", on_click=_set_flag, args=("btn_hf",))
        if st.session_state.get("btn_hf"):
            st.session_state["btn_hf"] = False
            st.session_state.mode = "Use Open-Source AI via Hugging Face"
            st.session_state.mode_chosen = True

    if st.session_state.mode == "Use Your Own OpenAI API Key" and not st.session_state.mode_chosen:
        st.session_state.api_input = st.text_input("Paste your OpenAI API Key", type="password", key="api_input_field")
        st.button("➡️ Continue", key="continue_api_ui", on_click=_set_flag, args=("btn_continue_api",))
        if st.session_state.get("btn_continue_api"):
            st.session_state["btn_continue_api"] = False
            if st.session_state.api_input.strip() == "":
                st.warning("Please enter your API key.")
            else:
                st.session_state.api_key = st.session_state.api_input
                st.session_state.mode_chosen = True

# ---SIGNUP SECTION ---
def signup_section():
    with st.container():
        st.subheader("📝 Create an Account")
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_password")
        st.button("Sign Up", key="signup_btn_ui", on_click=_set_flag, args=("btn_signup",))
        if st.session_state.get("btn_signup"):
            st.session_state["btn_signup"] = False
            if register_user(email, hash_password(password)):
                st.success("Account created! You can now login.")
            else:
                st.error("User already exists.")  

# --- RISKY TERMS FINDER ---
def find_risky_terms(text):
    risky_keywords = [
        "penalty", "termination", "breach", "fine",
        "automatic renewal", "binding arbitration",
        "liquidated damages", "non-compete", "non-disclosure",
        "late fee", "without notice", "waiver of rights",
        "exclusive jurisdiction", "governing law", "intellectual property"
    ]
    found_terms = []
    for keyword in risky_keywords:
        if keyword.lower() in text.lower():
            found_terms.append(keyword)
    return list(set(found_terms))

# --- AI RISK TERMS ---
def ai_risk_analysis(text, api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal risk analysis assistant. Identify clauses in contracts that could pose legal or financial risks to the signer, explain why, and suggest ways to mitigate them."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Analysis failed: {e}"


# --- MAIN APP ---
def app_main():
    # Back to mode selection
    st.button("◀️ Back to Mode Selection", key="back_btn_ui", on_click=_set_flag, args=("btn_back",))
    if st.session_state.get("btn_back"):
        st.session_state["btn_back"] = False
        st.session_state.mode_chosen = False
        st.session_state.mode = ""
        st.session_state.api_key = ""
        return

    st.sidebar.title("🔍 Navigation")
    choice = st.sidebar.radio("Go to", [ "📑 Upload & Simplify","👤 Profile","🚨 Risky Terms Detector",  "⏳ My History", "❓ Help & Feedback"])

    if choice == "👤 Profile":
        st.subheader("👤 Your Profile")
        st.write(f"**Logged in as:** `{st.session_state.user_email}`")
        st.button("🚪 Logout", key="logout_btn_ui", on_click=_set_flag, args=("btn_logout",))
        if st.session_state.get("btn_logout"):
            st.session_state["btn_logout"] = False
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.success("Logged out. Refresh to login again.")

    if choice == "📑 Upload & Simplify":
        st.subheader("📑 Upload Your Legal Document (PDF)")
        uploaded_file = st.file_uploader("Select a legal PDF", type=["pdf"], key="upload_simplify")

        full_text = ""
        doc_name = ""
        if uploaded_file:
            doc_name = uploaded_file.name.lower()
            if uploaded_file.size > 3 * 1024 * 1024:
                st.error("⚠️ File too large. Please upload PDFs under 3MB.")
            else:
                try:
                    with st.spinner("Reading and extracting text..."):
                        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                        full_text = "".join([page.get_text() for page in doc])
                    st.success("✅ Text extracted from PDF.")
                    with st.expander("📄 View Extracted Text"):
                        st.text_area("", full_text, height=300, key="extracted_text_area")
                except Exception as e:
                    st.error(f"❌ Error reading PDF: {str(e)}")
        
        st.button("🧐 Simplify Document", key="simplify_btn_ui", on_click=_set_flag, args=("btn_simplify",))
        if st.session_state.get("btn_simplify"):
            st.session_state["btn_simplify"] = False
            simplified = None
            if st.session_state.mode == "Use Your Own OpenAI API Key":
                 if not st.session_state.api_key:
                     st.error("❌ API key not found. Please go back and enter your key.")
                 else:
                     try:
                         st.warning("✅ Entered OpenAI summarization block")
                         from openai import OpenAI
                         client=OpenAI(api_key = st.session_state.api_key)
                         response = client.chat.completions.create(
                             model = "gpt-3.5-turbo",
                             messages=[
                                 {"role":"system","content": "You are a legal assistant. Simplify legal documents in plain English."},
                                 {"role": "user", "content": full_text}
                             ]
                         )
                         simplified = response.choices[0].message.content
                         
                     except Exception as e:
                         st.error(f"❌ OpenAI Error: {str(e)}")
                        
            elif st.session_state.mode == "Use Open-Source AI via Hugging Face":
                prompt = f"""Summarize the following document in bullet points:\n\n{full_text}"""
                with st.spinner("Simplifying using Hugging Face..."):
                    simplified = query_huggingface_api(prompt)

            else:
                if uploaded_file:
                    doc_name = uploaded_file.name.lower()
                    if "rental" in doc_name:
                        simplified = """
This is a rental agreement made between Mr. Rakesh Kumar (the property owner) and Mr. Anil Reddy (the person renting).

- The house is in Jubilee Hills, Hyderabad.
- Rent is ₹18,000/month, paid by the 5th.
- Anil pays a ₹36,000 security deposit.
- The rental period is 11 months: from August 1, 2025, to June 30, 2026.
- Either side can cancel the agreement with 1 month’s written notice.
- Anil can't sub-rent the house to anyone else unless Rakesh agrees.

In short: this document explains the rules of staying in the rented house, money terms, and how both sides can exit the deal.
                        """
                    elif "nda" in doc_name:
                        simplified =  """
This Non-Disclosure Agreement (NDA) is between TechNova Pvt. Ltd. and Mr. Kiran Rao.

- Kiran will receive sensitive business information from TechNova.
- He agrees to keep this confidential and not use it for anything other than their business discussions.
- This includes technical data, strategies, client info, designs, etc.
- He cannot share it, even after the project ends, for 3 years.
- Exceptions: if info is public, received legally from others, or required by law.
- If he breaks the agreement, TechNova can take legal action, including asking the court to stop him immediately.

In short: Kiran must not reveal or misuse any business secrets he gets from TechNova during their potential partnership.
                        """
                    elif "employment" in doc_name:
                        simplified =  """
This is an official job contract between GlobalTech Ltd. and Ms. Priya Sharma.

- Priya will join as a Senior Software Engineer from August 1, 2025.
- She will earn Rs. 12,00,000/year, including bonuses and allowances.
- She must work 40+ hours/week, either from office or remotely.
- First 6 months = probation, 15-day notice for quitting or firing.
- After that, it becomes 60-day notice.
- She must not share company secrets or join rival companies for 1 year after leaving.
- Any inventions or code she builds belong to the company.
- She gets 20 paid leaves + public holidays.

In short: This contract outlines Priya’s job, salary, rules during and after employment, and what happens if she quits or is fired.
                        """
                    else:
                        simplified = "📜 Demo Summary: Unable to identify document type. This is a general contract."
                else:
                    st.info("Upload a document first or use Demo mode.")

            if simplified:
                st.subheader("✅ Simplified Summary")
                st.success(simplified)
                if st.session_state.user_email:
                    save_upload(st.session_state.user_email, uploaded_file.name, simplified)
                # PDF download
                pdf_file = generate_pdf(simplified, uploaded_file.name if uploaded_file else "demo.pdf")
                st.download_button(
                    label="📥 Download Summary as PDF",
                    data=pdf_file,
                    file_name=f"simplified_{(uploaded_file.name.replace('.pdf','') if uploaded_file else 'summary')}.pdf",
                    mime="application/pdf"
                )
                # 🎤 Voice Summary
                audio_file_path = generate_voice(simplified)
                if audio_file_path:
                    with open(audio_file_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button(
                            label="🎧 Download Voice Summary",
                            data=audio_bytes,
                            file_name="summary_audio.mp3",
                            mime="audio/mp3"
                        )

    if choice == "⏳ My History":
        st.subheader("⏳ Your Uploaded History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file_name, summary, timestamp in history:
                with st.expander(f"📄 {file_name} | 🕒 {timestamp}"):
                    st.text(summary)
                    
    if choice == "❓ Help & Feedback":
      st.subheader("❓ Help & Feedback")
      st.markdown("""
      - **About LegalEase**: This tool simplifies legal documents in plain English using AI.
      - **Modes**:
          - *Demo Mode*: Uses sample summaries.
          - *OpenAI API*: Your key, high-quality output.
          - *Hugging Face*: Free, open-source summarization.
      - **Suggestions or bugs?** Drop a message at `support@legalease.com`.

      ### 👀 How It Works?
      Below is a visual guide to how LegalLite works:
        
