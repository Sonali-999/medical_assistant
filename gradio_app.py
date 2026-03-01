import gradio as gr

import os
#from auth import firebase_login, firebase_register, save_user_chat, get_user_chats
from auth import register_user, login_user, save_user_chat, get_user_chats

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_audio_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

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

# ---------------- Authentication UI ----------------
def format_chats_for_gradio(user_id):
    raw_chats = get_user_chats(user_id)
    # Convert tuples to lists
    return [[u, b] for u, b in raw_chats]
def signup(email, password):
    result = register_user(email, password)
    if "User registered" in result:
        return f"✅ {result}"
    else:
        return f"❌ {result}"

def login(email, password):
    global current_user
    login_result = login_user(email, password)
    if login_result["status"] == "success":
        user_id = login_result["user_id"]
        current_user["uid"] = user_id
        current_user["email"] = email
        chats = get_user_chats(user_id)
        return f"✅ Welcome {email}", gr.update(visible=True), chats
    else:
        return f"❌ Invalid email or password", gr.update(visible=False), []

# ---------------- Doctor Q&A Logic ----------------

def process_inputs(image_filepath, audio_filepath, user_msg=""):
    if not current_user["uid"]:
        return "⚠️ Please log in first.", "", None

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

    # Convert to voice
    if doctor_response:
        text_to_speech_with_gtts(
            input_text=doctor_response,
            output_filepath="final.mp3"
        )
        voice_of_doctor_path = "final.mp3"

    # Save chat in MySQL
    save_user_chat(current_user["uid"], speech_to_text_output, doctor_response)

    return speech_to_text_output, doctor_response, voice_of_doctor_path

# ---------------- Build Gradio UI ----------------

with gr.Blocks() as demo:
    gr.Markdown("## 🏥 AI Medical Assistant")

    with gr.Tab("Login / Signup"):
        email = gr.Textbox(label="Email")
        password = gr.Textbox(label="Password", type="password")

        login_btn = gr.Button("Login")
        signup_btn = gr.Button("Signup")

        login_status = gr.Textbox(label="Status", interactive=False)

        chatbox = gr.Chatbot(type="messages", label="Chat History", visible=False)


        login_btn.click(login, [email, password], [login_status, chatbox])

        signup_btn.click(signup, [email, password], [login_status])

    with gr.Tab("Doctor Chat", visible=True) as doctor_tab:

        with gr.Row():
            image_in = gr.Image(type="filepath", label="Upload Image")
            audio_in = gr.Audio(sources=["microphone"], type="filepath", label="Speak to Doctor")
        user_msg = gr.Textbox(label="Or type your question")

        stt_out = gr.Textbox(label="Speech to Text")
        doctor_out = gr.Textbox(label="Doctor's Response")
        doctor_audio = gr.Audio(label="Doctor's Voice Response")

        submit = gr.Button("Submit")
        submit.click(process_inputs, [image_in, audio_in, user_msg],
                     [stt_out, doctor_out, doctor_audio])

demo.launch(debug=True)

