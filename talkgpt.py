from openai import OpenAI
import streamlit as st
import base64

st.set_page_config(page_title="TalkGPT")

# --- Sidebar ---
with st.sidebar:
    st.title("🧠 TalkGPT")
    model_choice = st.selectbox(
        "Choose OpenAI GPT Model:",
        options=[
            "gpt-3.5-turbo",     # Budget-friendly
            "gpt-4o-mini",       # Budget-friendly + vision
            "gpt-4.1-nano",      # Extremely lightweight
            "gpt-4o",            # Latest flagship (vision capable)
        ],
        help="Select a model. gpt-4o and gpt-4o-mini support image inputs."
    )

    # File uploader only if the model supports vision
    if model_choice in ["gpt-4o", "gpt-4o-mini"]:
        uploaded_files = st.file_uploader(
            "Upload files (PDF, PNG, JPG, DOCX)",
            type=["pdf", "png", "jpg", "jpeg", "docx"],
            accept_multiple_files=True
        )
        if uploaded_files:
            st.session_state.pending_files = uploaded_files
    else:
        st.session_state.pending_files = []

    # Clear Chat Button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []

# --- Session State ---
if "openai_model" not in st.session_state or st.session_state["openai_model"] != model_choice:
    st.session_state["openai_model"] = model_choice

if "messages" not in st.session_state:
    st.session_state.messages = []

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Add system prompt to instruct GPT to use LaTeX for math ---
system_prompt = {
    "role": "system",
    "content": "You are a helpful tutor. When discussing math, use LaTeX syntax and enclose equations with $$...$$ for block display."
}

# --- Utility Functions ---

def maybe_format_as_latex(text):
    """Wrap possible math expressions with $$ for LaTeX rendering."""
    if any(symbol in text for symbol in ["^", "√", "±", "sqrt", "frac", "\\(", "\\["]):
        if "$$" not in text:
            return f"$$ {text.strip()} $$"
    return text

def render_message(content):
    """Render message with Markdown and possible LaTeX."""
    if "$$" in content or "\\(" in content or "\\[" in content:
        st.markdown(content, unsafe_allow_html=False)
    else:
        st.markdown(maybe_format_as_latex(content), unsafe_allow_html=False)

# --- Display previous messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Prepare file content if any (only for vision models) ---
    files_payload = []

    if "pending_files" in st.session_state and st.session_state.pending_files:
        if st.session_state["openai_model"] in ["gpt-4o", "gpt-4o-mini"]:
            for file in st.session_state.pending_files:
                file_bytes = file.read()
                mime = file.type
                if mime.startswith("image/"):
                    b64_data = base64.b64encode(file_bytes).decode("utf-8")
                    files_payload.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{b64_data}"
                        }
                    })
                else:
                    files_payload.append({
                        "type": "text",
                        "text": f"(Uploaded file: {file.name})"
                    })
        st.session_state.pending_files = []  # Clear after use

    # --- Build full payload ---
    messages_payload = [system_prompt] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # If there are images/text files, add them to the current user message
    if files_payload:
        messages_payload.append({
            "role": "user",
            "content": [prompt] + files_payload
        })

    # --- Call OpenAI Chat Completion ---
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=messages_payload if files_payload else messages_payload,
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
