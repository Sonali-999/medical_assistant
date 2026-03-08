import gradio as gr
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
load_dotenv()
from auth import register_user, login_user
from chat_db import save_user_chat, get_user_chats
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_audio_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts
from chat_db import save_user_chat, get_user_chats


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

# Custom CSS - Medical Theme
custom_css = """
/* Global Styles */
.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    
}

body {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%) !important;
}

/* Header Styles */
#header-banner {
    background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
    padding: 2rem;
    text-align: center;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(8, 145, 178, 0.2);
}

#header-banner h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

#header-banner p {
    color: #e0f2fe;
    font-size: 1.1rem;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* Tab Navigation */
.tab-nav {
    background: white !important;
    border-radius: 50px !important;
    padding: 0.5rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    display: inline-flex !important;
    margin: 1rem auto !important;
}

.tab-nav button {
    background: white !important;
    color: #64748b !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    border-radius: 40px !important;
    transition: all 0.3s ease !important;
    margin: 0 0.25rem !important;
}

.tab-nav button:hover {
    background: #f1f5f9 !important;
    color: #0891b2 !important;
}

.tab-nav button.selected {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3) !important;
}

/* Card Styles */
.card-container {
    background: white !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08) !important;
    border: 1px solid #e2e8f0 !important;
    margin: 1rem 0 !important;
}

/* Auth Section Styles */
#auth-header {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
    padding: 2rem;
    text-align: center;
    border-radius: 16px 16px 0 0;
    margin: -2rem -2rem 2rem -2rem;
}

#auth-header h2 {
    color: white;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

#auth-header p {
    color: #e0f2fe;
    margin-top: 0.5rem;
}

/* Form Elements */
label {
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.5rem !important;
    display: block !important;
    color:black;
}

input[type="text"],
input[type="email"], 
input[type="password"],
textarea {
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.875rem 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    background: white !important;
    color: black;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
textarea:focus {
    border-color: #0891b2 !important;
    box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1) !important;
    outline: none !important;
    color: #0891b2 !important;
}

/* Buttons */
button.primary {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3) !important;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(8, 145, 178, 0.4) !important;
}

button.secondary {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.875rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}

button.secondary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}

/* Chat History */
.chatbot {
    border: 2px solid #e2e8f0 !important;
    border-radius: 16px !important;
    background: #f8fafc !important;
    min-height: 400px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    color:black;
}

.message.user {
    background: #dbeafe !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    color: black !important;
}

.message.bot {
    background: #d1fae5 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    color: black !important;
}

/* Status Messages */
.status-success {
    background: #d1fae5 !important;
    color: #065f46 !important;
    border: 2px solid #10b981 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    font-weight: 600 !important;
    text-align: center !important;
}

.status-error {
    background: #fee2e2 !important;
    color: #991b1b !important;
    border: 2px solid #ef4444 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    font-weight: 600 !important;
    text-align: center !important;
}

/* Image Upload */
.image-upload-area {
    border: 3px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    text-align: center !important;
    background: #f8fafc !important;
    transition: all 0.3s ease !important;
    min-height: 300px !important;
}

.image-upload-area:hover {
    border-color: #0891b2 !important;
    background: #f0f9ff !important;
}

/* Audio Section */
.audio-section {
    border: 2px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    background: white !important;
    text-align: center !important;
    min-height: 300px !important;
}

/* Response Cards */
.response-card {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    color: #0891b2 !important;
}

.response-card.doctor {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
    border-color: #0891b2 !important;
    color: #0891b2 !important;
}

/* Section Headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
}

.section-header h3 {
    color: #1e293b;
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
}

/* Footer */
.footer {
    background: white;
    border-top: 2px solid #e2e8f0;
    padding: 1.5rem;
    text-align: center;
    margin-top: 3rem;
    border-radius: 16px;
}

.footer p {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0.25rem 0;
}

/* Utility Classes */
.icon-badge {
    background: white;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.divider {
    width: 2px;
    background: #e2e8f0;
    margin: 0 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    #header-banner h1 {
        font-size: 1.75rem;
    }
    
    .card-container {
        padding: 1.5rem !important;
    }
}
/* Force Markdown headers to be black */
.gradio-markdown h1,
.gradio-markdown h2,
.gradio-markdown h3,
.gradio-markdown h4,
.gradio-markdown h5,
.gradio-markdown h6 {
    color: black !important;
}



/* Styled Chat History */
.chat-entry {
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    margin: 1rem 0;
    background: #f8fafc;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    overflow: hidden;
}

.chat-header {
    background: #dbeafe;
    padding: 0.5rem 1rem;
    font-weight: 600;
    color: #1e293b;
    font-size: 0.85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
}

.chat-body .user-msg {
    background: #e0f2fe;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    color:black;
}

.chat-body .bot-msg {
    background: #d1fae5;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    color: black;
}

"""





# Helper functions
from datetime import datetime

def format_chats_for_gradio(user_id):
    chats = get_user_chats(user_id)
    messages = []

    for chat in chats:
        user_msg = chat.get("user_msg", "")
        bot_msg = chat.get("bot_msg", "")

        if user_msg:
            messages.append({"role": "user", "content": user_msg})

        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})

    return messages


def signup(email, password):
    result = register_user(email, password)
    if "User registered" in result:
        return f" {result}"
    else:
        return f" {result}"

def login(email, password):
    global current_user
    login_result = login_user(email, password)

    if login_result["status"] == "success":
        user_id = login_result["user_id"]
        current_user["uid"] = user_id
        current_user["email"] = email
        chats = format_chats_for_gradio(user_id)

        return (
            f" Welcome {email}",
            gr.update(visible=True),   # chatbox visible
            chats,                     # chat history
            gr.update(visible=True),   # dashboard tab visible
            gr.update(visible=True)    # consultation tab visible
        )

    else:
        return (
            " Invalid email or password",
            gr.update(visible=False),
            [],
            gr.update(visible=False),
            gr.update(visible=False)
        )

def load_dashboard():
    if not current_user["uid"]:
        return 0,0,0,None
    total, img, voice = get_dashboard_stats(current_user["uid"])
    chart = create_medical_chart(current_user["uid"])
    return total, img, voice, chart

def process_inputs(image_filepath, audio_filepath, user_msg=""):
    if not current_user["uid"]:
        return " Please log in first.", "", None

    speech_to_text_output = ""
    doctor_response = ""
    voice_of_doctor_path = None

    if audio_filepath:
        speech_to_text_output = transcribe_audio_with_groq(
            GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
            audio_file_path=audio_filepath,
            stt_model="whisper-large-v3"
        )
    else:
        speech_to_text_output = user_msg or "No input provided."

    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=f"{system_prompt} {speech_to_text_output}",
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            encoded_image=encode_image(image_filepath)
        )
    else:
        doctor_response = f"{speech_to_text_output} (no image analysis performed)."

    if doctor_response:
        text_to_speech_with_gtts(
            input_text=doctor_response,
            output_filepath="final.mp3"
        )
        voice_of_doctor_path = "final.mp3"

    save_user_chat(current_user["uid"], speech_to_text_output, doctor_response)

    return speech_to_text_output, doctor_response, voice_of_doctor_path

def get_dashboard_stats(user_id):
    chats = get_user_chats(user_id)

    total_consults = len(chats)

    images_used = sum(1 for c in chats if "image" in str(c))

    voice_used = sum(1 for c in chats if "audio" in str(c))

    return total_consults, images_used, voice_used


def create_medical_chart(user_id):

    chats = get_user_chats(user_id)

    data = {
        "Type": ["Text", "Image", "Voice"],
        "Usage": [
            sum(1 for c in chats if c.get("user_msg")),
            sum(1 for c in chats if "image" in str(c)),
            sum(1 for c in chats if "audio" in str(c))
        ]
    }

    df = pd.DataFrame(data)

    fig = px.pie(df, names="Type", values="Usage",
                 title="Consultation Input Types")

    return fig

# Build Gradio UI
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="blue")) as demo:
    
    # Header
    with gr.Row():
        gr.HTML("""
            <div id="header-banner">
                <div style="display: inline-block; background: white; padding: 1rem; border-radius: 50%; margin-bottom: 1rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/>
                    </svg>
                </div>
                <h1>🏥 AI Medical Assistant</h1>
                <p>Your Digital Healthcare Companion</p>
            </div>
        """)
    
    # Tabs
    with gr.Tabs():
        
        # Authentication Tab
        with gr.Tab("Authentication") as auth_tab:
            with gr.Column(elem_classes="card-container"):
                gr.HTML("""
                    <div id="auth-header">
                        <div class="icon-badge">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                                <circle cx="12" cy="7" r="4"/>
                            </svg>
                        </div>
                        <h2>Welcome Back</h2>
                        <p>Sign in to access your medical assistant</p>
                    </div>
                """)
                
                with gr.Row():
                    # Login Sect
                    with gr.Column(scale=1):
                        gr.Markdown('<h3 style="color:black;"> Login to Your Account</h3>')
                        email_login = gr.Textbox(
                            label="Email Address",
                            placeholder="your.email@example.com",
                            type="email"
                        )
                        password_login = gr.Textbox(
                            label="Password",
                            placeholder="Enter your password",
                            type="password"
                        )
                        login_btn = gr.Button("Login", elem_classes="primary", size="lg")
                    
                    # Divider
                    with gr.Column(scale=0, min_width=50):
                        gr.HTML('<div class="divider" style="height: 300px;"></div>')
                    
                    # Signup Sect
                    with gr.Column(scale=1):
                        gr.Markdown('<h3 style="color:black;">Create New Account</h3>')
                        email_signup = gr.Textbox(
                            label=" Email Address",
                            placeholder="your.email@example.com",
                            type="email"
                        )
                        password_signup = gr.Textbox(
                            label=" Password",
                            placeholder="Create a password",
                            type="password"
                        )
                        signup_btn = gr.Button("Sign Up", elem_classes="secondary", size="lg")
                
                # status Message
                login_status = gr.Textbox(
                    label="",
                    interactive=False,
                    show_label=False,
                    container=False
                )
                
                # Chat History (Hidden by default)
                gr.Markdown('<h3 style="color:black;"> Your Consultation History</h3>', visible=True)
                chatbox = gr.Chatbot(
                    type="messages",
                    label="",
                    visible=False,
                    height=400,
                    show_label=False
                )
        with gr.Tab("Dashboard", visible=False) as dashboard_tab:
            with gr.Column(elem_classes="card-container"):                
                gr.Markdown("## Patient Dashboard")
                with gr.Row():
                    total_consults = gr.Number(label="Total Consultations")
                    image_cases = gr.Number(label="Image Cases")
                    voice_cases = gr.Number(label="Voice Consultations")
                gr.Markdown("### Medical Interaction Analytics")
                chart = gr.Plot()
                refresh_dashboard = gr.Button("Refresh Dashboard")

        # Doctor Chat tab
        with gr.Tab("Doctor Consultation", visible=False) as consult_tab:
            with gr.Column():
                
                # Chat History Section
                with gr.Column(elem_classes="card-container"):
                    gr.HTML("""
                        <div class="section-header">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                            </svg>
                            <h3>Consultation Interface</h3>
                        </div>
                    """)
                    
                    gr.Markdown("*Upload an image, record your voice, or type your medical concern below*")
                
                # Input Section - Image and Audio
                with gr.Row():
                    with gr.Column(scale=1, elem_classes="card-container"):
                        gr.HTML("""
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                    <circle cx="8.5" cy="8.5" r="1.5"/>
                                    <polyline points="21 15 16 10 5 21"/>
                                </svg>
                                <span style="font-weight: 700; color: #1e293b;">Upload Medical Image</span>
                            </div>
                        """)
                        image_in = gr.Image(
                            type="filepath",
                            label="",
                            show_label=False,
                            height=280,
                            elem_classes="image-upload-area"
                        )
                    
                    with gr.Column(scale=1, elem_classes="card-container"):
                        gr.HTML("""
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                                    <line x1="12" y1="19" x2="12" y2="23"/>
                                    <line x1="8" y1="23" x2="16" y2="23"/>
                                </svg>
                                <span style="font-weight: 700; color: #1e293b;">Record Your Symptoms</span>
                            </div>
                        """)
                        audio_in = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="",
                            show_label=False,
                            elem_classes="audio-section"
                        )
                
                # Text input sect
                with gr.Column(elem_classes="card-container"):
                    gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                            </svg>
                            <span style="font-weight: 700; color: #1e293b;">Type Your Question</span>
                        </div>
                    """)
                    
                    with gr.Row():
                        user_msg = gr.Textbox(
                            label="",
                            placeholder="Describe your symptoms or ask a medical question...",
                            lines=2,
                            scale=4,
                            show_label=False
                        )
                        submit = gr.Button("🔍 Submit", elem_classes="primary", scale=1, size="lg")
                
                # Response Section
                gr.HTML('<div style="margin: 2rem 0 1rem 0; border-top: 2px solid #e2e8f0;"></div>')
                gr.Markdown("### Consultation Results")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### Your Input (Transcribed)")
                        stt_out = gr.Textbox(
                            label="",
                            lines=5,
                            interactive=False,
                            show_label=False,
                            elem_classes="response-card"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### Doctor's Analysis")
                        doctor_out = gr.Textbox(
                            label="",
                            lines=5,
                            interactive=False,
                            show_label=False,
                            elem_classes="response-card doctor"
                        )
                
                # Audio Response
                with gr.Column(elem_classes="card-container"):
                    gr.HTML("""
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                            </svg>
                            <span style="font-weight: 700; color: #1e293b;">Listen to Doctor's Response</span>
                        </div>
                    """)
                    doctor_audio = gr.Audio(
                        label="",
                        interactive=False,
                        show_label=False
                    )
    
    # Footer
    gr.HTML("""
        <div class="footer">
            <p style="font-weight: 600; color: #0891b2; font-size: 1rem;">AI Medical Assistant</p>
            <p>This is an AI-powered medical assistant for educational purposes only.</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">Always consult with a qualified healthcare professional for medical advice.</p>
        </div>
    """)
    
    # Event Handlers
    login_btn.click(
        login,
        inputs=[email_login, password_login],
        outputs=[
            login_status,
            chatbox,
            chatbox,
            dashboard_tab,
            consult_tab
        ]
    )
    
    signup_btn.click(
        signup,
        inputs=[email_signup, password_signup],
        outputs=[login_status]
    )
    
    submit.click(
        process_inputs,
        inputs=[image_in, audio_in, user_msg],
        outputs=[stt_out, doctor_out, doctor_audio]
    )

    refresh_dashboard.click(
    load_dashboard,
    outputs=[total_consults, image_cases, voice_cases, chart]
    )
if __name__ == "__main__":
    demo.launch(debug=True, share=False)   