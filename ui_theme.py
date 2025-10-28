# ui_theme.py
import streamlit as st

def apply_theme():
    """Injects global UI/UX theme and animation styles."""
    st.markdown(
        """
        <style>
        /* ===== BASE COLORS ===== */
        :root {
          --primary: #13349b;
          --accent: #9aa7ff;
          --bg1: #f5f7ff;
          --text: #0f172a;
        }

        /* ===== PAGE BACKGROUND ===== */
        .stApp {
          background: linear-gradient(120deg, var(--primary), var(--accent));
          background-size: 400% 400%;
          animation: gradientShift 16s ease infinite;
          color: var(--text);
        }

        @keyframes gradientShift {
          0% {background-position: 0% 50%;}
          50% {background-position: 100% 50%;}
          100% {background-position: 0% 50%;}
        }

        /* ===== CARD + CONTAINER ANIMATIONS ===== */
        .stContainer, .stExpander {
          animation: fadeIn 0.6s ease forwards;
          border-radius: 14px;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stContainer:hover, .stExpander:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 28px rgba(19,52,155,0.25);
        }

        @keyframes fadeIn {
          from {opacity: 0; transform: translateY(8px);}
          to {opacity: 1; transform: translateY(0);}
        }

        /* ===== BUTTONS ===== */
        button[kind="primary"], button[role="button"] {
          background: var(--primary) !important;
          color: white !important;
          border-radius: 10px !important;
          border: none !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 6px 14px rgba(19,52,155,0.3);
          font-weight: 600;
        }
        button[kind="primary"]:hover, button[role="button"]:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 24px rgba(19,52,155,0.4);
        }
        button[kind="primary"]:active, button[role="button"]:active {
          transform: translateY(0);
          opacity: 0.9;
        }

        /* ===== TEXT INPUTS ===== */
        input, textarea {
          border-radius: 8px !important;
          border: 1px solid rgba(19,52,155,0.15) !important;
          padding: 8px !important;
          transition: box-shadow 0.2s ease;
        }
        input:focus, textarea:focus {
          border-color: var(--accent) !important;
          box-shadow: 0 0 0 3px rgba(154,167,255,0.25);
          outline: none !important;
        }

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {
          background: rgba(255,255,255,0.1);
          backdrop-filter: blur(14px);
          border-right: 1px solid rgba(255,255,255,0.2);
          box-shadow: 4px 0 12px rgba(0,0,0,0.15);
          animation: slideIn 0.6s ease;
        }
        @keyframes slideIn {
          from {transform: translateX(-12px); opacity: 0;}
          to {transform: translateX(0); opacity: 1;}
        }
        section[data-testid="stSidebar"] .css-1d391kg, 
        section[data-testid="stSidebar"] .css-1v3fvcr {
          color: white !important;
        }
        [data-testid="stSidebarNav"] a {
          color: white !important;
          font-weight: 500;
        }

        /* ===== HEADINGS ===== */
        h1, h2, h3, h4 {
          color: white;
          text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        /* ===== CUSTOM SPINNER ===== */
        .stSpinner > div {
          border-top-color: var(--accent) !important;
          border-right-color: transparent !important;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from {transform: rotate(0deg);}
          to {transform: rotate(360deg);}
        }

        /* ===== DARK MODE COMPATIBILITY ===== */
        @media (prefers-color-scheme: dark) {
          :root {
            --bg1: #0a0e2a;
            --text: #f9fafb;
          }
          .stApp {
            background: linear-gradient(120deg, #0a0e2a, #13349b);
          }
          section[data-testid="stSidebar"] {
            background: rgba(18,18,50,0.7);
            border-right: 1px solid rgba(255,255,255,0.1);
          }
          h1, h2, h3, h4 {
            color: #eaeaea;
          }
          input, textarea {
            background: rgba(255,255,255,0.05);
            color: #f5f5f5;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Draws custom sidebar header with icons (same navigation as user’s)."""
    st.sidebar.markdown(
        """
        <div style="text-align:center; padding:10px 0;">
          <h2 style="color:white;">⚖️ LegalLite</h2>
          <p style="font-size:13px; color:#dbe3ff;">Simplify, Summarize, Secure.</p>
        </div>
        <hr style="border:1px solid rgba(255,255,255,0.2); margin:0 0 12px 0;">
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <style>
        .nav-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 14px;
          border-radius: 10px;
          margin-bottom: 6px;
          transition: all 0.2s ease;
          color: white;
          cursor: pointer;
        }
        .nav-item:hover {
          background: rgba(255,255,255,0.2);
          transform: translateX(4px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Static display; navigation still handled by Streamlit radio
    st.sidebar.markdown(
        """
        <div class="nav-item">📑 Upload & Simplify</div>
        <div class="nav-item">👤 Profile</div>
        <div class="nav-item">🚨 Risky Terms Detector</div>
        <div class="nav-item">⏳ My History</div>
        <div class="nav-item">❓ Help & Feedback</div>
        """,
        unsafe_allow_html=True,
    )
