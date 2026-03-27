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
    .stApp { background-color: #f5f7f2; }
    .main-header {
        background: linear-gradient(135deg, #1a3a2a 0%, #2d6a4f 100%);
        padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1rem;
    }
    .main-header h1 { color: white; font-size: 1.8rem; margin: 0; }
    .main-header p { color: #a8d5b5; margin: 0.3rem 0 0; font-size: 0.95rem; }
    [data-testid="stSidebar"] { background-color: #1a3a2a; }
    [data-testid="stSidebar"] * { color: #e8f5e9 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #2d6a4f; color: white !important;
        border: none; border-radius: 8px; width: 100%;
        margin-bottom: 4px; padding: 8px 12px; font-size: 13px;
    }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """You are AgriAI, a highly specialized AI research assistant for:
- PhD research in AI/ML for agricultural plant disease detection
- Assistant Professor duties: teaching, course design, student guidance
- Deep learning model development (CNN, ViT, YOLO, ResNet, EfficientNet)
- Academic paper writing, literature reviews, and grant proposals
- Rice, wheat, tomato, and other crop disease identification
Your user is an Assistant Professor with 5 years of experience pursuing a PhD in AI/ML
applied to agriculture, focusing on plant disease detection, based in India.
Always respond with technically accurate research-grade content and practical PyTorch code."""

QUICK_PROMPTS = {
    "🔬 Research": [
        "Write a literature review on CNN-based rice disease detection (2020-2024)",
        "What are the current research gaps in AI-based plant disease detection?",
        "Compare CNN vs Vision Transformer for leaf disease classification",
    ],
    "💻 Code": [
        "Write PyTorch code for ResNet50 transfer learning on rice disease dataset",
        "Generate YOLOv8 pipeline for real-time rice disease detection",
        "Write code for Grad-CAM visualization on plant disease CNN",
    ],
    "📝 Paper Writing": [
        "Write an abstract for early rice disease detection using deep learning",
        "Write the introduction section for my plant disease detection paper",
        "Suggest top journals to submit my agri-AI research paper",
    ],
    "🎓 Teaching": [
        "Create lecture notes on CNNs for undergraduate AI students",
        "Design a semester project on plant disease detection for MSc students",
        "Generate 15 MCQ questions on deep learning for image classification",
    ],
    "🗃️ Datasets": [
        "List all publicly available rice disease image datasets with download links",
        "How to collect rice disease images in field conditions in India?",
        "Techniques to handle small and imbalanced plant disease datasets",
    ],
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "ready" not in st.session_state:
    st.session_state.ready = False

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
    st.markdown("## 🌾 Quick Prompts")
    st.markdown("---")
    for category, prompts in QUICK_PROMPTS.items():
        with st.expander(category, expanded=False):
            for p in prompts:
                short = p[:45] + "..." if len(p) > 45 else p
                if st.button(short, key=f"btn_{p[:30]}"):
                    st.session_state["inject_prompt"] = p
    st.markdown("---")
    st.markdown(f"**Queries:** {st.session_state.total_queries}")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.ready = False
        st.session_state.total_queries = 0
        st.rerun()

st.markdown("""
<div class='main-header'>
    <h1>🌾 AgriAI Research Assistant</h1>
    <p>AI-powered companion for plant disease detection research, code, papers and teaching</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.ready:
    st.warning("🔑 Enter your free Gemini API key below to start:")
    col1, col2 = st.columns([3, 1])
    with col1:
        manual_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            label_visibility="collapsed"
        )
    with col2:
        connect_btn = st.button("Connect 🔗", use_container_width=True)
    if manual_key and connect_btn:
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
            st.error(f"❌ Invalid key: {e}")
    st.caption("Get your FREE key at → aistudio.google.com/app/apikey")
    st.stop()

if not st.session_state.messages:
    st.success("✅ AgriAI is ready! Ask anything about plant disease detection, deep learning, papers or teaching.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🌾" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

injected = st.session_state.pop("inject_prompt", None)
user_input = st.chat_input("Ask about rice disease detection, deep learning, paper writing...")
prompt = injected or user_input

if prompt:
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
                    st.error("⚠️ Rate limit hit. Wait 1 minute and try again.")
                elif "invalid" in err.lower():
                    st.error("❌ Invalid API key. Please check your Gemini key.")
                else:
                    st.error(f"❌ Error: {err}")
