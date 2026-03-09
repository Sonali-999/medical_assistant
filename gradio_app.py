import gradio as gr
import os
from dotenv import load_dotenv

load_dotenv()
from auth import register_user, login_user
from chat_db import save_user_chat, get_user_chats
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_audio_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts
from chat_db import save_user_chat, get_user_chats
from simulation import measure_time, generate_latency_graph
from drug_recommender import recommend_drugs, get_drug_list
from datetime import datetime
from mongo_db import prescriptions_collection
from dashboard import build_dashboard_ui, refresh_dashboard
# ── Ensure prescriptions collection exists in MongoDB on startup ──
try:
    if "prescriptions" not in prescriptions_collection.database.list_collection_names():
        prescriptions_collection.database.create_collection("prescriptions")
    print("[mongo] prescriptions collection ready")
except Exception as e:
    print(f"[mongo] prescriptions collection init warning: {e}")

def edge_step(user_msg):
    return user_msg.strip()

# Session state
current_user = {"uid": None, "email": None}

system_prompt = (
    "You have to act as a professional doctor, I know you are not but this is for learning purpose. "
    "What's in this image? Do you find anything wrong with it medically? "
    "If you make a differential, suggest some remedies for them. Do not add any numbers or special characters in "
    "your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person. "
    "Don't say 'In the image, I see...' or 'In the image, I found...'. Rather say 'With what I see, I think you have....' "
    "Don't respond as an AI model, but rather as a doctor who is talking to a patient. "
    "Keep your response short and to the point, do not add any extra information. No preamble, start your answer right away."
)

# ─── CSS ────────────────────────────────────────────────────────────────────

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Light Theme Variables ── */
:root {
    --bg-base:            #f4f6f9;
    --bg-surface:         #ffffff;
    --bg-surface-2:       #f8fafc;
    --bg-surface-3:       #f1f5f9;
    --border:             #e2e8f0;
    --border-2:           #cbd5e1;
    --text-primary:       #0f172a;
    --text-secondary:     #475569;
    --text-muted:         #94a3b8;
    --accent:             #0891b2;
    --accent-light:       #e0f2fe;
    --accent-dark:        #0e7490;
    --sidebar-bg:         #0c4a6e;
    --sidebar-bg2:        #0369a1;
    --sidebar-text:       rgba(255,255,255,0.72);
    --sidebar-active-bg:  rgba(255,255,255,0.13);
    --card-shadow:        0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    --user-bubble-bg:     #eff6ff;
    --user-bubble-border: #bfdbfe;
    --user-bubble-text:   #1e3a5f;
    --doc-bubble-bg:      #f0fdf4;
    --doc-bubble-border:  #bbf7d0;
    --doc-bubble-text:    #14532d;
    --input-bg:           #ffffff;
    --sim-bg:             #0f172a;
    --sim-text:           #38bdf8;
}

/* ── Dark Theme Variables ── */
body.dark-theme {
    --bg-base:            #0d1117;
    --bg-surface:         #161b22;
    --bg-surface-2:       #1c2333;
    --bg-surface-3:       #21262d;
    --border:             #30363d;
    --border-2:           #3d444d;
    --text-primary:       #e6edf3;
    --text-secondary:     #8b949e;
    --text-muted:         #6e7681;
    --accent:             #38bdf8;
    --accent-light:       #1a3147;
    --accent-dark:        #0891b2;
    --sidebar-bg:         #010409;
    --sidebar-bg2:        #0d1117;
    --sidebar-text:       rgba(255,255,255,0.58);
    --sidebar-active-bg:  rgba(56,189,248,0.12);
    --card-shadow:        0 1px 3px rgba(0,0,0,0.3), 0 4px 16px rgba(0,0,0,0.2);
    --user-bubble-bg:     #1a2d42;
    --user-bubble-border: #1d4ed8;
    --user-bubble-text:   #93c5fd;
    --doc-bubble-bg:      #0f2a1c;
    --doc-bubble-border:  #166534;
    --doc-bubble-text:    #86efac;
    --input-bg:           #1c2333;
    --sim-bg:             #010409;
    --sim-text:           #38bdf8;
}

/* ── Gradio Resets ── */
body, .gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-primary) !important;
    min-height: 100vh;
}
.gradio-container { max-width: 100% !important; padding: 0 !important; }
footer { display: none !important; }
.tabs > .tab-nav { display: none !important; }
.gr-padded { padding: 0 !important; }

/* ── Floating Theme Toggle ── */
#theme-toggle-btn {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 9999;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    border: 1.5px solid var(--border);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 1.05rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--card-shadow);
    transition: all 0.2s ease;
    line-height: 1;
}
#theme-toggle-btn:hover { border-color: var(--accent); color: var(--accent); }

/* ══════════════════════════════════════════
   AUTH SCREEN
══════════════════════════════════════════ */
#auth-screen {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #0c4a6e 0%, #0369a1 55%, #0891b2 100%);
    padding: 2rem;
}

/* ══════════════════════════════════════════
   APP LAYOUT
══════════════════════════════════════════ */
#app-layout { display: flex; min-height: 100vh; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
#sidebar {
    width: 252px;
    min-width: 252px;
    background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bg2) 100%);
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0;
    height: 100vh;
    z-index: 200;
    box-shadow: 2px 0 16px rgba(0,0,0,0.18);
    overflow-y: auto;
    overflow-x: hidden;
}

.sb-brand {
    padding: 1.4rem 1.2rem 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    display: flex;
    align-items: center;
    gap: 0.7rem;
    flex-shrink: 0;
}

.sb-brand-icon {
    width: 34px; height: 34px;
    background: rgba(255,255,255,0.11);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}

.sb-brand-text h2 {
    color: #fff;
    font-size: 0.92rem;
    font-weight: 700;
    margin: 0; line-height: 1.3;
}

.sb-brand-text p {
    color: rgba(255,255,255,0.4);
    font-size: 0.68rem;
    margin: 0;
}

.sb-user {
    margin: 0.8rem 0.8rem 0.2rem;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 9px;
    padding: 0.7rem 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    flex-shrink: 0;
}

.sb-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #0891b2, #06b6d4);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: white; font-size: 0.85rem;
    flex-shrink: 0;
}

.sb-user-name { color: #fff; font-size: 0.78rem; font-weight: 600; }
.sb-user-role { color: rgba(255,255,255,0.42); font-size: 0.67rem; margin-top: 1px; }

.sb-section-label {
    padding: 0.9rem 1.2rem 0.35rem;
    font-size: 0.63rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.32);
    flex-shrink: 0;
}

.sb-nav {
    flex: 1;
    padding: 0.2rem 0.55rem;
    display: flex;
    flex-direction: column;
    gap: 1px;
}

/* Nav buttons */
.sb-nav button {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    padding: 0.6rem 0.85rem !important;
    border-radius: 7px !important;
    border: none !important;
    background: transparent !important;
    color: var(--sidebar-text) !important;
    font-size: 0.855rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    letter-spacing: 0.005em !important;
}

.sb-nav button:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #fff !important;
}

.sb-nav-bottom {
    padding: 0.55rem;
    border-top: 1px solid rgba(255,255,255,0.07);
    flex-shrink: 0;
}

.sb-nav-bottom button {
    width: 100% !important;
    padding: 0.6rem 0.85rem !important;
    border-radius: 7px !important;
    border: none !important;
    background: transparent !important;
    color: rgba(252,165,165,0.75) !important;
    font-size: 0.855rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

.sb-nav-bottom button:hover {
    background: rgba(239,68,68,0.1) !important;
    color: #fca5a5 !important;
}

/* ══════════════════════════════════════════
   MAIN CONTENT
══════════════════════════════════════════ */
#main-content {
    flex: 1;
    margin-left: 252px;
    min-height: 100vh;
    background: var(--bg-base);
}

.pg-head {
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    padding: 1.1rem 2rem;
    position: sticky;
    top: 0; z-index: 100;
}

.pg-head-title {
    color: var(--text-primary);
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0 0 0.1rem;
    letter-spacing: -0.02em;
}

.pg-head-sub {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin: 0;
}

.pg-body {
    padding: 1.75rem 2rem;
    max-width: 1160px;
    width: 100%;
}

/* ══════════════════════════════════════════
   CARDS
══════════════════════════════════════════ */
.card {
    background: var(--bg-surface);
    border-radius: 12px;
    padding: 1.375rem 1.5rem;
    box-shadow: var(--card-shadow);
    border: 1px solid var(--border);
    margin-bottom: 1.25rem;
}

.card-head {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-muted);
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.card-head-icon {
    width: 26px; height: 26px;
    background: var(--accent-light);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════
   HOME PAGE
══════════════════════════════════════════ */
.welcome-banner {
    background: linear-gradient(120deg, #0891b2 0%, #0e7490 100%);
    border-radius: 14px;
    padding: 1.625rem 1.875rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    box-shadow: 0 5px 20px rgba(8,145,178,0.2);
}

.wb-text h2 {
    font-size: 1.3rem;
    font-weight: 800;
    color: white;
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
}

.wb-text p { color: rgba(255,255,255,0.76); font-size: 0.855rem; margin: 0; }

.wb-badge {
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 9px;
    padding: 0.625rem 1.1rem;
    text-align: center;
    flex-shrink: 0;
}

.wb-badge span { display: block; color: rgba(255,255,255,0.7); font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.wb-badge strong { color: white; font-size: 1.1rem; font-weight: 800; }

.quick-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 0.875rem;
    margin-bottom: 1.25rem;
}

.qc {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.18s ease;
}

.qc:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 18px rgba(8,145,178,0.1);
    transform: translateY(-2px);
}

.qc-tag {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--accent);
    margin-bottom: 0.35rem;
}

.qc h4 { color: var(--text-primary); font-size: 0.9rem; font-weight: 700; margin: 0 0 0.25rem; }
.qc p  { color: var(--text-muted); font-size: 0.77rem; margin: 0; line-height: 1.5; }

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
button.primary-btn {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.68rem 1.5rem !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 3px 10px rgba(8,145,178,0.26) !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
}
button.primary-btn:hover {
    box-shadow: 0 5px 16px rgba(8,145,178,0.38) !important;
    transform: translateY(-1px) !important;
}

button.secondary-btn {
    background: var(--bg-surface) !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent) !important;
    padding: 0.68rem 1.5rem !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
}
button.secondary-btn:hover { background: var(--accent-light) !important; }

/* ══════════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════════ */
.gradio-textbox label span, label span {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.775rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.065em !important;
}

textarea, input[type="text"], input[type="email"], input[type="password"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.68rem 0.875rem !important;
    font-size: 0.875rem !important;
    transition: all 0.18s ease !important;
    background: var(--input-bg) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

textarea:focus, input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(8,145,178,0.09) !important;
    outline: none !important;
}

/* ══════════════════════════════════════════
   CHAT HISTORY
══════════════════════════════════════════ */
.ch-scroll {
    max-height: 68vh;
    overflow-y: auto;
    padding-right: 2px;
}
.ch-scroll::-webkit-scrollbar { width: 4px; }
.ch-scroll::-webkit-scrollbar-track { background: var(--bg-surface-3); border-radius: 4px; }
.ch-scroll::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 4px; }

.ch-empty {
    text-align: center;
    padding: 3.5rem 1rem;
    color: var(--text-muted);
}
.ch-empty p { font-size: 0.875rem; margin: 0.5rem 0 0; line-height: 1.6; }

.ch-item {
    border: 1px solid var(--border);
    border-radius: 11px;
    overflow: hidden;
    background: var(--bg-surface);
    margin-bottom: 1rem;
    transition: box-shadow 0.18s ease;
}
.ch-item:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.07); }

.ch-item-header {
    background: var(--bg-surface-3);
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.ch-item-num {
    background: var(--accent);
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    letter-spacing: 0.04em;
    margin-right: 0.5rem;
}

.ch-item-label { color: var(--text-secondary); font-size: 0.775rem; font-weight: 600; }
.ch-item-time  { color: var(--text-muted); font-size: 0.7rem; }

.ch-item-body  { padding: 0.875rem 1rem; display: flex; flex-direction: column; gap: 0.7rem; }

.ch-role-label {
    font-size: 0.67rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.25rem;
}

.ch-bubble {
    padding: 0.7rem 0.9rem;
    border-radius: 8px;
    font-size: 0.86rem;
    line-height: 1.65;
    border: 1px solid;
}

.ch-user   .ch-role-label { color: #3b82f6; }
.ch-user   .ch-bubble { background: var(--user-bubble-bg); border-color: var(--user-bubble-border); color: var(--user-bubble-text); }

.ch-doctor .ch-role-label { color: #16a34a; }
.ch-doctor .ch-bubble { background: var(--doc-bubble-bg); border-color: var(--doc-bubble-border); color: var(--doc-bubble-text); }

/* ══════════════════════════════════════════
   PROFILE
══════════════════════════════════════════ */
.profile-banner {
    background: linear-gradient(120deg, #0891b2, #0e7490);
    border-radius: 14px;
    padding: 1.75rem;
    display: flex;
    align-items: center;
    gap: 1.375rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 5px 20px rgba(8,145,178,0.18);
}

.profile-avatar-lg {
    width: 68px; height: 68px;
    background: rgba(255,255,255,0.18);
    border: 2px solid rgba(255,255,255,0.28);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.65rem; font-weight: 800; color: white;
    flex-shrink: 0;
}

.profile-banner-info h3 { color: white; font-size: 1.1rem; font-weight: 700; margin: 0 0 0.2rem; }
.profile-banner-info p  { color: rgba(255,255,255,0.68); font-size: 0.8rem; margin: 0; }

.pf-row {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border);
}
.pf-row:last-child { border-bottom: none; padding-bottom: 0; }

.pf-label {
    color: var(--text-muted);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    min-width: 76px;
    padding-top: 2px;
    flex-shrink: 0;
}

.pf-value {
    color: var(--text-primary);
    font-size: 0.875rem;
    font-weight: 500;
    word-break: break-all;
    flex: 1;
}

/* ══════════════════════════════════════════
   SIMULATION
══════════════════════════════════════════ */
.sim-terminal textarea {
    background: var(--sim-bg) !important;
    color: var(--sim-text) !important;
    font-family: 'JetBrains Mono', 'Fira Mono', 'Courier New', monospace !important;
    font-size: 0.84rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 1.25rem !important;
    line-height: 1.85 !important;
}

/* ══════════════════════════════════════════
   OUTPUT BOXES
══════════════════════════════════════════ */
.output-box textarea {
    background: var(--bg-surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
}

/* ══════════════════════════════════════════
   STATUS MESSAGES
══════════════════════════════════════════ */
.status-ok  { background:#dcfce7!important; color:#166534!important; border:1px solid #bbf7d0!important; border-radius:8px!important; padding:0.7rem 1rem!important; font-size:0.855rem!important; font-weight:600!important; }
.status-err { background:#fee2e2!important; color:#991b1b!important; border:1px solid #fecaca!important; border-radius:8px!important; padding:0.7rem 1rem!important; font-size:0.855rem!important; font-weight:600!important; }

/* ══════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════ */
@media (max-width: 960px) {
    #sidebar { width: 58px; min-width: 58px; }
    .sb-brand-text, .sb-user-name, .sb-user-role, .sb-section-label { display: none !important; }
    .sb-brand { justify-content: center; padding: 1.2rem 0; }
    .sb-user  { justify-content: center; padding: 0.7rem 0.4rem; }
    .sb-nav button, .sb-nav-bottom button { justify-content: center !important; padding: 0.65rem !important; }
    #main-content { margin-left: 58px; }
}

@media (max-width: 600px) {
    #sidebar { display: none; }
    #main-content { margin-left: 0; }
    .pg-body { padding: 1rem; }
    .quick-grid { grid-template-columns: 1fr 1fr; }
    .welcome-banner { flex-direction: column; align-items: flex-start; }
    .wb-badge { display: none; }
}

/* ══════════════════════════════════════════
   AUTH SCREEN  – tab toggle card
══════════════════════════════════════════ */

/* Card container: centered, flex column, consistent gap between fields */
#auth-card {
    background: var(--bg-surface);
    border-radius: 20px;
    padding: 2.25rem 2rem 2rem;
    width: 100%;
    max-width: 420px;
    margin: auto;
    display: flex;
    flex-direction: column;
    gap: 0;
    box-shadow: 0 24px 64px rgba(0,0,0,0.28);
    border: 1px solid var(--border);
}

/* Each Gradio textbox block stacked, uniform bottom margin */
#auth-card .gradio-textbox {
    width: 100% !important;
    margin-bottom: 14px !important;
}

/* Label sits directly above input, normal weight/case for readability */
#auth-card .gradio-textbox > label > span {
    display: block !important;
    margin-bottom: 5px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* All auth inputs: full width, fixed height, consistent look */
#auth-card input[type="email"],
#auth-card input[type="password"],
#auth-card input[type="text"] {
    width: 100% !important;
    height: 42px !important;
    padding: 0 0.875rem !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    background: var(--input-bg) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}

#auth-card input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    outline: none !important;
}

.auth-app-title {
    text-align: center;
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
}

/* Tab row: grid so both tabs always fill 100% width with no empty space */
.auth-tab-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    width: 100%;
    background: var(--bg-surface-3);
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1.75rem;
    gap: 2px;
}

.auth-tab {
    width: 100%;
    text-align: center;
    padding: 0.58rem 0;
    border: none;
    border-radius: 7px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s ease;
    font-family: 'Inter', sans-serif;
}

.auth-tab.inactive { background: transparent; color: var(--text-muted); }
.auth-tab.inactive:hover { color: var(--text-primary); }
.auth-tab.active   { background: #2563eb; color: #ffffff; box-shadow: 0 2px 8px rgba(37,99,235,0.32); }

.auth-switch-text {
    text-align: center;
    font-size: 0.83rem;
    color: var(--text-muted);
    margin-top: 1.1rem;
}

.auth-switch-text a {
    color: #2563eb;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
}

.auth-switch-text a:hover { text-decoration: underline; }

#auth-card button.primary-btn {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.28) !important;
    margin-top: 4px !important;
}

#auth-card button.primary-btn:hover {
    box-shadow: 0 5px 16px rgba(37,99,235,0.4) !important;
}

.auth-status-ok  { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; border-radius:8px; padding:0.65rem 1rem; font-size:0.84rem; font-weight:600; margin-top:0.75rem; }
.auth-status-err { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; border-radius:8px; padding:0.65rem 1rem; font-size:0.84rem; font-weight:600; margin-top:0.75rem; }

/* ══════════════════════════════════════════
   BOLD TEXT – always visible in both themes
══════════════════════════════════════════ */
strong { color: var(--text-primary); }
.card strong { color: var(--text-primary); }
p strong { color: var(--text-primary); }
/* Exception: strong inside intentionally colored containers (welcome banner, profile banner) keeps white */
.welcome-banner strong,
.profile-banner strong,
.wb-badge strong { color: #ffffff; }

/* ══════════════════════════════════════════
   DRUG RECOMMENDATION – sidebar badge
══════════════════════════════════════════ */
.sb-new-badge {
    display: inline-block;
    background: linear-gradient(135deg, #059669, #34d399);
    color: white;
    font-size: 0.55rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.15rem 0.38rem;
    border-radius: 4px;
    margin-left: 0.4rem;
    vertical-align: middle;
    line-height: 1.4;
}

/* ══════════════════════════════════════════
   DRUG RECOMMENDATION – page scroll area
══════════════════════════════════════════ */
.drug-results-scroll {
    max-height: 72vh;
    overflow-y: auto;
    padding-right: 4px;
}

.drug-results-scroll::-webkit-scrollbar { width: 4px; }
.drug-results-scroll::-webkit-scrollbar-track { background: var(--bg-surface-3); border-radius: 4px; }
.drug-results-scroll::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 4px; }
"""

# ─── HTML BUILDERS ────────────────────────────────────────────────────────────

def format_chats_for_gradio(user_id):
    chats = get_user_chats(user_id)
    messages = []
    for chat in chats:
        u = chat.get("user_msg", "")
        b = chat.get("bot_msg",  "")
        if u: messages.append({"role": "user",      "content": u})
        if b: messages.append({"role": "assistant", "content": b})
    return messages

def build_chat_history_html(user_id):
    chats = get_user_chats(user_id)
    if not chats:
        return """
        <div class="ch-empty">
            <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5"
                 stroke-linecap="round" stroke-linejoin="round" style="margin:0 auto 1rem;display:block;">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <p>No consultations yet.<br>Complete a consultation to see your history here.</p>
        </div>"""
    now  = datetime.now().strftime("%b %d, %H:%M")
    html = '<div class="ch-scroll">'
    for i, chat in enumerate(reversed(chats), 1):
        u = chat.get("user_msg", "—")
        b = chat.get("bot_msg",  "—")
        html += f"""
        <div class="ch-item">
            <div class="ch-item-header">
                <div>
                    <span class="ch-item-num">#{i}</span>
                    <span class="ch-item-label">Consultation</span>
                </div>
                <span class="ch-item-time">{now}</span>
            </div>
            <div class="ch-item-body">
                <div class="ch-user">
                    <div class="ch-role-label">Patient</div>
                    <div class="ch-bubble">{u}</div>
                </div>
                <div class="ch-doctor">
                    <div class="ch-role-label">Doctor AI</div>
                    <div class="ch-bubble">{b}</div>
                </div>
            </div>
        </div>"""
    html += "</div>"
    return html

def build_sidebar_user_html(email):
    i = email[0].upper() if email else "U"
    d = email if len(email) <= 24 else email[:22] + "…"
    return f"""
    <div class="sb-user">
        <div class="sb-avatar">{i}</div>
        <div>
            <div class="sb-user-name">{d}</div>
            <div class="sb-user-role">Patient Account</div>
        </div>
    </div>"""

def build_profile_html(email, user_id):
    i = email[0].upper() if email else "U"
    return f"""
    <div class="profile-banner">
        <div class="profile-avatar-lg">{i}</div>
        <div class="profile-banner-info">
            <h3>{email}</h3>
            <p>Patient &nbsp;&middot;&nbsp; Active</p>
        </div>
    </div>
    <div class="card">
        <div class="card-head">Account Details</div>
        <div class="pf-row">
            <span class="pf-label">Email</span>
            <span class="pf-value">{email}</span>
        </div>
        <div class="pf-row">
            <span class="pf-label">User ID</span>
            <span class="pf-value" style="font-family:monospace;font-size:0.8rem;">{user_id}</span>
        </div>
        <div class="pf-row">
            <span class="pf-label">Role</span>
            <span class="pf-value">Patient</span>
        </div>
        <div class="pf-row">
            <span class="pf-label">Status</span>
            <span class="pf-value" style="color:#16a34a;font-weight:600;">Active</span>
        </div>
    </div>"""

def build_welcome_html(email):
    first = email.split("@")[0].capitalize()
    return f"""
    <div class="welcome-banner">
        <div class="wb-text">
            <h2>Welcome back, {first}</h2>
            <p>Your AI-powered medical assistant is ready. Use the sidebar to navigate.</p>
        </div>
        <div class="wb-badge"><span>Status</span><strong>Online</strong></div>
    </div>
    <div class="quick-grid">
        <div class="qc" style="border-left:3px solid #0891b2;">
            <div class="qc-tag">Start</div><h4>New Consultation</h4>
            <p>Upload a medical image and describe your symptoms for instant AI analysis.</p>
        </div>
        <div class="qc" style="border-left:3px solid #059669;">
            <div class="qc-tag" style="color:#059669;">New</div><h4>Drug Recommendation</h4>
            <p>Get OTC medicine suggestions based on your symptoms or diagnosed condition.</p>
        </div>
        <div class="qc" style="border-left:3px solid #7c3aed;">
            <div class="qc-tag" style="color:#7c3aed;">History</div><h4>Past Consultations</h4>
            <p>Review all previous AI doctor interactions and responses.</p>
        </div>
        <div class="qc" style="border-left:3px solid #d97706;">
            <div class="qc-tag" style="color:#d97706;">Account</div><h4>My Profile</h4>
            <p>View and manage your account information and settings.</p>
        </div>
    </div>
    <div class="card">
        <div class="card-head">
            <div class="card-head-icon">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2.5"
                     stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
            </div>
            About This Platform
        </div>
        <p style="color:var(--text-secondary);font-size:0.875rem;line-height:1.8;margin:0;">
            MediAssist AI uses multimodal large language models to analyze medical images and patient-reported symptoms.
            The new <strong>Drug Recommendation</strong> feature suggests OTC medicines based on your condition.
            Navigate to <strong>Consultation</strong> to upload an image, record your voice, or type your concern.
            <br><br>
            <span style="color:var(--accent);font-weight:600;">⚠ Disclaimer:</span>
            <span style="color:var(--text-muted);"> For educational purposes only. Always consult a qualified healthcare professional.</span>
        </p>
    </div>"""

# ─── CORE FUNCTIONS ───────────────────────────────────────────────────────────

def signup(email, password):
    result = register_user(email, password)
    if "User registered" in result:
        return gr.update(value='<div class="auth-status-ok">✓ Account created! Switch to Login to sign in.</div>')
    return gr.update(value=f'<div class="auth-status-err">✗ {result}</div>')

def login(email, password):
    global current_user
    r = login_user(email, password)
    if r["status"] == "success":
        uid = r["user_id"]
        current_user["uid"]   = uid
        current_user["email"] = email
        # show_page("home") returns 7 gr.update() values for all_pages
        page_updates = show_page("home")
        return (
            gr.update(value=""),
            gr.update(visible=True),
            format_chats_for_gradio(uid),
            gr.update(visible=False),
            gr.update(visible=True),
            build_welcome_html(email),
            build_sidebar_user_html(email),
            build_chat_history_html(uid),
            build_profile_html(email, uid),
        ) + page_updates
    return (
        gr.update(value='<div class="auth-status-err">✗ Invalid email or password. Please try again.</div>'),
        gr.update(visible=False), [],
        gr.update(visible=True), gr.update(visible=False),
        "", "", "", "",
    ) + tuple(gr.update() for _ in PAGE_KEYS)

# Drug recommendation handler
def get_drug_recommendation(disease_input, severity):

    if not disease_input or not disease_input.strip():
        return '<div style="color:var(--text-muted);text-align:center;padding:2rem;">Enter a condition or symptoms above and click Get Drug Recommendation.</div>'

    # Generate UI result
    result_html = recommend_drugs(disease_input, severity)

    # 🔹 Extract drug list for database storage
    drugs = get_drug_list(disease_input)

    # Save prescription to MongoDB if user is logged in
    if current_user["uid"] and result_html:
        try:
            doc = {
                "user_id":       current_user["uid"],
                "email":         current_user["email"],
                "condition":     disease_input.strip(),
                "severity":      severity,
                "session_title": f"{disease_input.strip().title()} – {datetime.now().strftime('%b %d, %Y %H:%M')}",

                # 🔹 Save structured data instead of HTML
                "drugs":         drugs,

                "created_at":    datetime.now()
            }

            result = prescriptions_collection.insert_one(doc)
            print(f"[mongo] Prescription saved: {result.inserted_id}")

        except Exception as e:
            print(f"[mongo] Prescription save FAILED: {e}")

    return result_html

def signout():
    global current_user
    current_user["uid"]   = None
    current_user["email"] = None

    tab_reset = """
    <script>
    (function() {
        var l = document.getElementById('tab-login-btn');
        var s = document.getElementById('tab-signup-btn');
        if (l) l.className = 'auth-tab active';
        if (s) s.className = 'auth-tab inactive';
    })();
    </script>
    """
    return (
        gr.update(visible=True),                   # auth_screen  ✅ show
        gr.update(visible=False),                  # app_screen   ✅ hide
        "",                                        # login_status
        gr.update(visible=True),                   # login_form
        gr.update(visible=False),                  # signup_form
        gr.update(visible=True, value=tab_reset),  # tab_reset_html
        # ✅ ALSO reset every page inside app_screen to False
        gr.update(visible=False),  # page_home
        gr.update(visible=False),  # page_consultation
        gr.update(visible=False),  # page_history
        gr.update(visible=False),  # page_profile
        gr.update(visible=False),  # page_dashboard
        gr.update(visible=False),  # page_simulation
        gr.update(visible=False),  # page_drugs
    )

# Auto-fill drug page from consultation diagnosis
def process_inputs_and_refresh(image_filepath, audio_filepath, user_msg=""):
    """Runs consultation and returns updated chat history in the same call."""
    results = process_inputs(image_filepath, audio_filepath, user_msg)
    updated_history = build_chat_history_html(current_user["uid"]) if current_user["uid"] else ""
    # Auto drug recommendation from diagnosis
    diagnosis_text = results[1] if results[1] else ""
    auto_drug_html = recommend_drugs(diagnosis_text) if diagnosis_text and "no image" not in diagnosis_text.lower() else ""
    return results + (updated_history, diagnosis_text, auto_drug_html)

def process_inputs(image_filepath, audio_filepath, user_msg=""):
    if not current_user["uid"]:
        return "Please log in first.", "", None, "", None

    def _edge(msg): return msg.strip()
    processed_input, edge_time = measure_time(_edge, user_msg)

    if audio_filepath:
        stt = transcribe_audio_with_groq(
            GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
            audio_file_path=audio_filepath,
            stt_model="whisper-large-v3"
        )
    else:
        stt = processed_input or "No input provided."

    _, fog_time = measure_time(get_user_chats, current_user["uid"])

    if image_filepath:
        doctor_response, cloud_time = measure_time(
            analyze_image_with_query,
            query=f"{system_prompt} {stt}",
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            encoded_image=encode_image(image_filepath)
        )
    else:
        doctor_response = f"{stt} (no image analysis performed)."
        cloud_time = 0

    audio_path = None
    if doctor_response:
        text_to_speech_with_gtts(input_text=doctor_response, output_filepath="final.mp3")
        audio_path = "final.mp3"

    save_user_chat(current_user["uid"], stt, doctor_response)

    total = edge_time + fog_time + cloud_time
    sim_text = (
        f"  Processing Path : Edge  ->  Fog  ->  Cloud\n"
        f"  {'─'*38}\n"
        f"  Edge  Latency   : {edge_time:>8.2f} ms\n"
        f"  Fog   Latency   : {fog_time:>8.2f} ms\n"
        f"  Cloud Latency   : {cloud_time:>8.2f} ms\n"
        f"  {'─'*38}\n"
        f"  Total Time      : {total:>8.2f} ms\n"
    )
    graph_path = generate_latency_graph(edge_time, fog_time, cloud_time)
    return stt, doctor_response, audio_path, sim_text, graph_path

# ─── NAVIGATION ───────────────────────────────────────────────────────────────

PAGE_KEYS = ["home", "consultation", "history", "profile", "dashboard", "simulation", "drugs"]

# AFTER
def show_page(name):
    if not current_user["uid"]:
        return tuple(gr.update() for _ in PAGE_KEYS)
    return tuple(gr.update(visible=(k == name)) for k in PAGE_KEYS)

def refresh_history():
    if current_user["uid"]:
        return build_chat_history_html(current_user["uid"])
    return ""

# ─── UI ───────────────────────────────────────────────────────────────────────

with gr.Blocks(
    css=custom_css,
    theme=gr.themes.Base(
        font=gr.themes.GoogleFont("Inter"),
        primary_hue="cyan",
        secondary_hue="sky",
        neutral_hue="slate",
    )
) as demo:

    # Floating theme toggle
    gr.HTML("""
    <button id="theme-toggle-btn" title="Switch to Dark Mode" onclick="(function(){
        const dark = document.body.classList.toggle('dark-theme');
        const btn  = document.getElementById('theme-toggle-btn');
        btn.textContent = dark ? '\u2600' : '\u263e';
        btn.title = dark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    })()">&#9790;</button>
    """)

    # ═══════════════════════════════════════
    # AUTH SCREEN  – tab toggle card
    # ═══════════════════════════════════════
    with gr.Column(elem_id="auth-screen", visible=True) as auth_screen:
        with gr.Column(elem_id="auth-card"):

            gr.HTML('<div class="auth-app-title">MediAssist AI</div>')

            gr.HTML("""
            <div class="auth-tab-row">
                <button class="auth-tab inactive" id="tab-login-btn"
                    onclick="
                        document.getElementById('tab-login-btn').className='auth-tab active';
                        document.getElementById('tab-signup-btn').className='auth-tab inactive';
                        document.getElementById('__to_login').click();">Login</button>
                <button class="auth-tab active" id="tab-signup-btn"
                    onclick="
                        document.getElementById('tab-signup-btn').className='auth-tab active';
                        document.getElementById('tab-login-btn').className='auth-tab inactive';
                        document.getElementById('__to_signup').click();">Signup</button>
            </div>
            """)

            to_signup_btn = gr.Button("x", elem_id="__to_signup", visible=False)
            to_login_btn  = gr.Button("x", elem_id="__to_login",  visible=False)

            # Hidden component used by signout to JS-reset tab highlight to Login
            tab_reset_html = gr.HTML("", visible=False)

            with gr.Column(visible=False) as login_form:
                email_login    = gr.Textbox(label="Email", placeholder="you@example.com", type="email")
                password_login = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                login_btn      = gr.Button("Login", elem_classes="primary-btn", size="lg")
                login_status_login = gr.HTML("")
                gr.HTML('<div class="auth-switch-text">Don\'t have an account? <a onclick="document.getElementById(\'__to_signup\').click();document.getElementById(\'tab-signup-btn\').className=\'auth-tab active\';document.getElementById(\'tab-login-btn\').className=\'auth-tab inactive\';">Signup</a></div>')

            with gr.Column(visible=True) as signup_form:
                email_signup    = gr.Textbox(label="Email", placeholder="you@example.com", type="email")
                password_signup = gr.Textbox(label="Password", placeholder="Choose a strong password", type="password")
                signup_btn      = gr.Button("Create Account", elem_classes="primary-btn", size="lg")
                login_status_signup = gr.HTML("")
                gr.HTML('<div class="auth-switch-text">Already have an account? <a onclick="document.getElementById(\'__to_login\').click();document.getElementById(\'tab-login-btn\').className=\'auth-tab active\';document.getElementById(\'tab-signup-btn\').className=\'auth-tab inactive\';">Login</a></div>')

            login_status = gr.Textbox(label="", interactive=False, show_label=False, container=False, visible=False)
            chatbox      = gr.Chatbot(type="messages", label="", visible=False, height=1, show_label=False)

    # ═══════════════════════════════════════
    # APP SCREEN
    # ═══════════════════════════════════════
    with gr.Row(elem_id="app-layout", visible=False) as app_screen:

        # ─ SIDEBAR ─────────────────────────
        with gr.Column(elem_id="sidebar", min_width=252, scale=0):
            gr.HTML("""
            <div class="sb-brand">
                <div class="sb-brand-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24"
                         fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5c0 1.1.9 2 2 2h2
                                 a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/>
                    </svg>
                </div>
                <div class="sb-brand-text">
                    <h2>MediAssist AI</h2>
                    <p>Healthcare Platform</p>
                </div>
            </div>""")

            sidebar_user_display = gr.HTML("")

            gr.HTML('<div class="sb-section-label">Navigation</div>')

            with gr.Column(elem_classes="sb-nav"):
                nav_home         = gr.Button("Home")
                nav_consultation = gr.Button("Consultation")
                nav_drugs        = gr.Button("Drug Recommendation  ✦")
                nav_history      = gr.Button("Chat History")
                nav_profile      = gr.Button("Profile")
                nav_dashboard    = gr.Button("Dashboard")
                nav_simulation   = gr.Button("Simulation")

            with gr.Column(elem_classes="sb-nav-bottom"):
                nav_signout = gr.Button("Sign Out")

        # ─ MAIN CONTENT ────────────────────
        with gr.Column(elem_id="main-content", scale=1):

            # ── HOME ──────────────────────────────────────────────────────
            with gr.Column(visible=True) as page_home:
                gr.HTML('<div class="pg-head"><div class="pg-head-title">Home</div><div class="pg-head-sub">Overview and quick access</div></div>')
                with gr.Column(elem_classes="pg-body"):
                    home_welcome = gr.HTML("")

            # ── CONSULTATION ──────────────────────────────────────────────
            with gr.Column(visible=False) as page_consultation:
                gr.HTML('<div class="pg-head"><div class="pg-head-title">Doctor Consultation</div><div class="pg-head-sub">Upload an image, record your voice, or describe your symptoms</div></div>')
                with gr.Column(elem_classes="pg-body"):

                    with gr.Row(equal_height=True):
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML("""<div class="card-head">
                                <div class="card-head-icon">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                                        <circle cx="8.5" cy="8.5" r="1.5"/>
                                        <polyline points="21 15 16 10 5 21"/>
                                    </svg>
                                </div>
                                Medical Image
                            </div>""")
                            image_in = gr.Image(type="filepath", label="", show_label=False, height=240)

                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML("""<div class="card-head">
                                <div class="card-head-icon">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                                        <line x1="12" y1="19" x2="12" y2="23"/>
                                        <line x1="8"  y1="23" x2="16" y2="23"/>
                                    </svg>
                                </div>
                                Voice Input
                            </div>""")
                            audio_in = gr.Audio(sources=["microphone"], type="filepath", label="", show_label=False)

                    with gr.Column(elem_classes="card"):
                        gr.HTML("""<div class="card-head">
                            <div class="card-head-icon">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                </svg>
                            </div>
                            Symptom Description
                        </div>""")
                        with gr.Row():
                            user_msg = gr.Textbox(
                                label="", show_label=False,
                                placeholder="Describe your symptoms in detail, e.g. 'I have a rash on my left arm that has been itching for three days...'",
                                lines=2, scale=5
                            )
                            submit = gr.Button("Analyze", elem_classes="primary-btn", scale=1, size="lg")

                    gr.HTML('<div style="height:1px;background:var(--border);margin:0.5rem 0 1.25rem;"></div>')
                    gr.HTML('<p class="card-head" style="border:none;padding:0;margin-bottom:1rem;">Results</p>')

                    with gr.Row():
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML('<div class="card-head">Patient Input (Transcribed)</div>')
                            stt_out = gr.Textbox(label="", lines=6, interactive=False, show_label=False, elem_classes="output-box")

                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML('<div class="card-head">Doctor Analysis</div>')
                            doctor_out = gr.Textbox(label="", lines=6, interactive=False, show_label=False, elem_classes="output-box")

                    with gr.Column(elem_classes="card"):
                        gr.HTML('<div class="card-head">Audio Response</div>')
                        doctor_audio = gr.Audio(label="", interactive=False, show_label=False)

            # ── CHAT HISTORY ──────────────────────────────────────────────
            with gr.Column(visible=False) as page_history:
                gr.HTML('<div class="pg-head"><div class="pg-head-title">Consultation History</div><div class="pg-head-sub">All your past AI doctor interactions</div></div>')
                with gr.Column(elem_classes="pg-body"):
                    with gr.Column(elem_classes="card"):
                        gr.HTML('<div class="card-head">Session Records</div>')
                        chat_history_html = gr.HTML("")

            # ── PROFILE ───────────────────────────────────────────────────
            with gr.Column(visible=False) as page_profile:
                gr.HTML('<div class="pg-head"><div class="pg-head-title">My Profile</div><div class="pg-head-sub">Your account information</div></div>')
                with gr.Column(elem_classes="pg-body"):
                    profile_html = gr.HTML("")

            # ── DASHBOARD ─────────────────────────────────────────────────
            with gr.Column(visible=False) as page_dashboard:
                db_components = build_dashboard_ui()

            # ── SIMULATION ────────────────────────────────────────────────
            with gr.Column(visible=False) as page_simulation:
                gr.HTML('<div class="pg-head"><div class="pg-head-title">Edge–Fog–Cloud Simulation</div><div class="pg-head-sub">Latency metrics from the last consultation pipeline run</div></div>')
                with gr.Column(elem_classes="pg-body"):
                    with gr.Row():
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML('<div class="card-head">System Performance Log</div>')
                            simulation_output = gr.Textbox(label="", lines=11, interactive=False,
                                                           show_label=False, elem_classes="sim-terminal")
                        with gr.Column(scale=1, elem_classes="card"):
                            gr.HTML('<div class="card-head">Latency Graph</div>')
                            latency_graph = gr.Image(label="", show_label=False)

            # ── DRUG RECOMMENDATION ───────────────────────────────────────
            with gr.Column(visible=False) as page_drugs:
                gr.HTML("""
                <div class="pg-head">
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        <div style="width:32px;height:32px;background:linear-gradient(135deg,#059669,#34d399);
                                    border-radius:8px;display:flex;align-items:center;justify-content:center;
                                    flex-shrink:0;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/>
                            </svg>
                        </div>
                        <div>
                            <div class="pg-head-title">Drug Recommendation</div>
                            <div class="pg-head-sub">AI-powered OTC medicine suggestions based on your condition or symptoms</div>
                        </div>
                    </div>
                </div>""")
                with gr.Column(elem_classes="pg-body"):

                    # Info banner
                    gr.HTML("""
                    <div style="background:linear-gradient(120deg,#059669 0%,#0d9488 100%);border-radius:14px;
                                padding:1.25rem 1.5rem;margin-bottom:1.25rem;display:flex;align-items:center;
                                justify-content:space-between;gap:1rem;box-shadow:0 5px 20px rgba(5,150,105,0.2);">
                        <div>
                            <div style="color:white;font-size:1.05rem;font-weight:800;margin-bottom:0.25rem;">
                                OTC Drug Recommendation System
                            </div>
                            <div style="color:rgba(255,255,255,0.78);font-size:0.84rem;">
                                Enter a disease name or describe your symptoms. Only over-the-counter medications are recommended.
                            </div>
                        </div>
                        <div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.22);
                                    border-radius:9px;padding:0.6rem 1rem;text-align:center;flex-shrink:0;">
                            <span style="display:block;color:rgba(255,255,255,0.7);font-size:0.65rem;font-weight:700;
                                         text-transform:uppercase;letter-spacing:0.08em;">Database</span>
                            <strong style="color:white;font-size:1rem;font-weight:800;">15 Conditions</strong>
                        </div>
                    </div>""")

                    # Input card
                    with gr.Column(elem_classes="card"):
                        gr.HTML("""<div class="card-head">
                            <div class="card-head-icon">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669"
                                     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                                </svg>
                            </div>
                            Symptom / Disease Input
                        </div>""")
                        with gr.Row():
                            drug_input = gr.Textbox(
                                label="", show_label=False,
                                placeholder="e.g. fever, common cold, acne, headache, muscle pain, allergy...",
                                lines=2, scale=4
                            )
                            drug_severity = gr.Dropdown(
                                choices=["Mild", "Moderate", "Severe"],
                                value="Mild",
                                label="Severity",
                                scale=1
                            )
                        drug_btn = gr.Button("Get Drug Recommendation", elem_classes="primary-btn", size="lg")

                    # Auto-fill from consultation notice
                    gr.HTML("""
                    <div style="background:var(--accent-light);border:1px solid var(--border);border-radius:9px;
                                padding:0.75rem 1rem;margin-bottom:1rem;display:flex;align-items:center;gap:0.6rem;
                                font-size:0.82rem;color:var(--text-secondary);">
                        <span>Complete a <strong>Consultation</strong> first — the diagnosis will auto-populate here for instant drug recommendations.</span>
                    </div>""")

                    # Results area
                    with gr.Column(elem_classes="card"):
                        gr.HTML("""<div class="card-head">
                            <div class="card-head-icon">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669"
                                     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/>
                                </svg>
                            </div>
                            Recommended Medicines
                        </div>""")
                        with gr.Column(elem_classes="drug-results-scroll"):
                            drug_output = gr.HTML(
                                '<div style="color:var(--text-muted);text-align:center;padding:3rem 1rem;">'
                                '<div style="font-size:0.875rem;">Enter a condition above and click <strong>Get Drug Recommendation</strong></div>'
                                '</div>'
                            )

    # ═══════════════════════════════════════
    # EVENT HANDLERS
    # ═══════════════════════════════════════

    to_signup_btn.click(fn=lambda: (gr.update(visible=False), gr.update(visible=True)),  outputs=[login_form, signup_form])
    to_login_btn.click( fn=lambda: (gr.update(visible=True),  gr.update(visible=False)), outputs=[login_form, signup_form])

    login_btn.click(
        login,
        inputs=[email_login, password_login],
        outputs=[login_status_login, chatbox, chatbox,
                 auth_screen, app_screen,
                 home_welcome, sidebar_user_display,
                 chat_history_html, profile_html,
                 page_home, page_consultation, page_history,
                 page_profile, page_dashboard, page_simulation, page_drugs]
    )

    signup_btn.click(signup, inputs=[email_signup, password_signup], outputs=[login_status_signup])

    all_pages = [page_home, page_consultation, page_history, page_profile, page_dashboard, page_simulation, page_drugs]

    # Consultation submit — updates results, chat history, AND auto-fills drug page
    submit.click(
        process_inputs_and_refresh,
        inputs=[image_in, audio_in, user_msg],
        outputs=[stt_out, doctor_out, doctor_audio, simulation_output, latency_graph,
                 chat_history_html, drug_input, drug_output]
    )

    # Drug recommendation button
    drug_btn.click(
        get_drug_recommendation,
        inputs=[drug_input, drug_severity],
        outputs=[drug_output]
    )

    # Navigation
    nav_home.click(         fn=lambda: show_page("home"),         outputs=all_pages)
    nav_consultation.click( fn=lambda: show_page("consultation"), outputs=all_pages)
    nav_history.click(      fn=lambda: show_page("history"),      outputs=all_pages)
    nav_profile.click(      fn=lambda: show_page("profile"),      outputs=all_pages)
    nav_dashboard.click(    fn=lambda: show_page("dashboard"),    outputs=all_pages)
    nav_dashboard.click(
        fn=lambda: refresh_dashboard(current_user["uid"]),
        outputs=[db_components["summary"], db_components["diagnoses"],
                db_components["drug_history"], db_components["condition_chart"],
                db_components["drug_chart"], db_components["insights"]]
    )
    nav_simulation.click(   fn=lambda: show_page("simulation"),   outputs=all_pages)
    nav_drugs.click(        fn=lambda: show_page("drugs"),        outputs=all_pages)

    nav_history.click(fn=refresh_history, outputs=[chat_history_html])

    nav_signout.click(
        signout,
        outputs=[
            auth_screen, app_screen,
            login_status, login_form, signup_form, tab_reset_html,
            # ✅ add all pages so they get reset to hidden
            page_home, page_consultation, page_history,
            page_profile, page_dashboard, page_simulation, page_drugs
        ]
    )

if __name__ == "__main__":
    demo.launch(debug=True, share=False)