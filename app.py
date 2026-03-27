
import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(
    page_title="AgriAI Research Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background: #f0f4f0; }
.hero {
    background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 60%, #1D9E75 100%);
    padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
}
.hero h1 { color: white; font-size: 2rem; margin: 0 0 0.3rem; }
.hero p { color: #a8d5b5; margin: 0; font-size: 1rem; }
.sec { font-size: 1rem; color: #1a3a2a; font-weight: 600;
    margin: 1.2rem 0 0.6rem; padding-left: 10px;
    border-left: 3px solid #1D9E75; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "You are AgriAI, a highly specialized AI research assistant for: "
    "PhD research in AI/ML for agricultural plant disease detection, "
    "Assistant Professor duties: teaching, course design, student guidance, "
    "Deep learning model development (CNN, ViT, YOLO, ResNet, EfficientNet), "
    "Academic paper writing, literature reviews, and grant proposals, "
    "Rice, wheat, tomato, and other crop disease identification. "
    "Your user is an Assistant Professor with 5 years of experience pursuing a PhD in AI/ML "
    "applied to agriculture, focusing on plant disease detection, based in India. "
    "Always respond with technically accurate research-grade content and practical PyTorch code."
)

MODULES = [
    {
        "icon": "🔬",
        "title": "Research",
        "desc": "Literature reviews and gap analysis",
        "prompts": [
            "Write a literature review on CNN-based rice disease detection (2020-2024)",
            "What are the current research gaps in AI-based plant disease detection?",
            "Compare CNN vs Vision Transformer for leaf disease classification",
            "How can federated learning help in plant disease detection across farms?",
        ]
    },
    {
        "icon": "💻",
        "title": "Code and Models",
        "desc": "PyTorch, YOLO, ViT code generation",
        "prompts": [
            "Write PyTorch code for ResNet50 transfer learning on rice disease dataset",
            "Generate complete YOLOv8 pipeline for real-time rice disease detection",
            "Write Grad-CAM visualization code for plant disease CNN model",
            "Write code to handle class imbalance using focal loss",
        ]
    },
    {
        "icon": "📝",
        "title": "Paper Writing",
        "desc": "Abstracts, introductions, methodology",
        "prompts": [
            "Write an abstract for early rice disease detection using deep learning",
            "Write the introduction section for my plant disease detection paper",
            "Write methodology section for CNN-Transformer hybrid model paper",
            "Suggest top journals for my agri-AI research paper",
        ]
    },
    {
        "icon": "🎓",
        "title": "Teaching",
        "desc": "Lecture notes, quizzes, syllabus",
        "prompts": [
            "Create lecture notes on CNNs for undergraduate AI/ML students",
            "Design a semester project on plant disease detection for MSc students",
            "Generate 15 MCQ questions on deep learning for image classification",
            "Design a full syllabus for AI in Agriculture elective course",
        ]
    },
    {
        "icon": "🗃️",
        "title": "Datasets",
        "desc": "Data collection and augmentation",
        "prompts": [
            "List all publicly available rice disease datasets with download links",
            "How to collect and annotate rice disease images in field in India?",
            "Techniques to handle small and imbalanced plant disease datasets",
            "How to adapt model trained on lab images to real field conditions?",
        ]
    },
    {
        "icon": "📊",
        "title": "Evaluation",
        "desc": "Metrics, benchmarking, Grad-CAM",
        "prompts": [
            "Write code for complete evaluation metrics for disease classification",
            "How to benchmark my rice disease model against state-of-the-art?",
            "Explain precision, recall, F1 and mAP for plant disease detection",
            "Write code to generate confusion matrix and ROC curves",
        ]
    },
]

for key, val in [
    ("messages", []),
    ("chat_session", None),
    ("total_queries", 0),
    ("ready", False),
    ("active_module", None),
    ("inject_prompt", None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if api_key and not st.session_state.ready:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT
        )
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.ready = True
    except:
        st.session_state.ready = False

with st.sidebar:
    st.markdown("## 🌾 AgriAI")
    if st.session_state.ready:
        st.success("Connected!")
    st.markdown("---")
    st.markdown(f"**Queries:** {st.session_state.total_queries}")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.ready = False
        st.session_state.total_queries = 0
        st.rerun()

st.markdown("""
<div class='hero'>
    <h1>🌾 AgriAI Research Assistant</h1>
    <p>AI-powered companion for plant disease detection — research, code, papers and teaching</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.ready:
    st.warning("🔑 Enter your free Gemini API key to start:")
    col1, col2 = st.columns([4, 1])
    with col1:
        manual_key = st.text_input(
            "key", type="password",
            placeholder="AIzaSy... get free key at aistudio.google.com/app/apikey",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("Connect", use_container_width=True):
            if manual_key:
                try:
                    genai.configure(api_key=manual_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-2.0-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    st.session_state.chat_session = model.start_chat(history=[])
                    st.session_state.ready = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Invalid key: {e}")
    st.caption("Get free key: aistudio.google.com/app/apikey")
    st.divider()

st.markdown("<div class='sec'>Select a Module</div>", unsafe_allow_html=True)

cols = st.columns(6)
for i, mod in enumerate(MODULES):
    with cols[i]:
        label = mod["icon"] + " " + mod["title"]
        if st.button(label, key="mod_" + str(i), use_container_width=True):
            st.session_state.active_module = i
            st.rerun()

if st.session_state.active_module is not None:
    mod = MODULES[st.session_state.active_module]
    title = mod["icon"] + " " + mod["title"] + " — Quick Prompts"
    st.markdown("<div class='sec'>" + title + "</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for j, prompt in enumerate(mod["prompts"]):
        with (col1 if j % 2 == 0 else col2):
            if st.button("▶  " + prompt, key="p_" + str(j), use_container_width=True):
                st.session_state.inject_prompt = prompt

st.divider()
st.markdown("<div class='sec'>💬 Chat</div>", unsafe_allow_html=True)

if not st.session_state.messages:
    if st.session_state.ready:
        st.success("✅ AgriAI is ready! Select a module above or type your question below.")
    else:
        st.info("👆 Connect your API key above, then select a module to start!")
else:
    for msg in st.session_state.messages:
        avatar = "🌾" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

injected = st.session_state.pop("inject_prompt", None)
user_input = st.chat_input("Ask about rice disease detection, deep learning, papers, teaching...")
prompt = injected or user_input

if prompt:
    if not st.session_state.ready:
        st.error("Please connect your Gemini API key first!")
        st.stop()
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🌾"):
        with st.spinner("AgriAI is thinking..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.total_queries += 1
                st.rerun()
            except Exception as e:
                err = str(e)
                if "429" in err or "quota" in err.lower():
                    st.error("Rate limit hit. Wait 1 minute and try again.")
                else:
                    st.error("Error: " + err)
