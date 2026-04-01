
import streamlit as st
import requests

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

OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

MODULES = [
    {"icon": "🔬", "title": "Research", "prompts": [
        "Write a literature review on CNN-based rice disease detection (2020-2024)",
        "What are the current research gaps in AI-based plant disease detection?",
        "Compare CNN vs Vision Transformer for leaf disease classification",
        "How can federated learning help in plant disease detection across farms?",
    ]},
    {"icon": "💻", "title": "Code and Models", "prompts": [
        "Write PyTorch code for ResNet50 transfer learning on rice disease dataset",
        "Generate complete YOLOv8 pipeline for real-time rice disease detection",
        "Write Grad-CAM visualization code for plant disease CNN model",
        "Write code to handle class imbalance using focal loss",
    ]},
    {"icon": "📝", "title": "Paper Writing", "prompts": [
        "Write an abstract for early rice disease detection using deep learning",
        "Write the introduction section for my plant disease detection paper",
        "Write methodology section for CNN-Transformer hybrid model paper",
        "Suggest top journals for my agri-AI research paper",
    ]},
    {"icon": "🎓", "title": "Teaching", "prompts": [
        "Create lecture notes on CNNs for undergraduate AI/ML students",
        "Design a semester project on plant disease detection for MSc students",
        "Generate 15 MCQ questions on deep learning for image classification",
        "Design a full syllabus for AI in Agriculture elective course",
    ]},
    {"icon": "🗃️", "title": "Datasets", "prompts": [
        "List all publicly available rice disease datasets with download links",
        "How to collect and annotate rice disease images in field in India?",
        "Techniques to handle small and imbalanced plant disease datasets",
        "How to adapt model trained on lab images to real field conditions?",
    ]},
    {"icon": "📊", "title": "Evaluation", "prompts": [
        "Write code for complete evaluation metrics for disease classification",
        "How to benchmark my rice disease model against state-of-the-art?",
        "Explain precision, recall, F1 and mAP for plant disease detection",
        "Write code to generate confusion matrix and ROC curves",
    ]},
]

for key, val in [
    ("messages", []),
    ("total_queries", 0),
    ("ready", False),
    ("active_module", None),
    ("inject_prompt", None),
    ("api_key", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = val


def call_openrouter(api_key, messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agriai-research-assistant.streamlit.app",
        "X-Title": "AgriAI Research Assistant",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    }
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


if not st.session_state.ready:
    st.session_state.api_key = OPENROUTER_API_KEY
    st.session_state.ready = True

with st.sidebar:
    st.markdown("## 🌾 AgriAI")
    st.success("✅ OpenRouter Connected!")
    st.caption(f"Model: `{OPENROUTER_MODEL}`")
    st.markdown("---")
    st.markdown(f"**Queries:** {st.session_state.total_queries}")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.rerun()

st.markdown("""
<div class='hero'>
    <h1>🌾 AgriAI Research Assistant</h1>
    <p>AI-powered companion for plant disease detection — research, code, papers and teaching</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='sec'>Select a Module</div>", unsafe_allow_html=True)
cols = st.columns(6)
for i, mod in enumerate(MODULES):
    with cols[i]:
        if st.button(mod["icon"] + " " + mod["title"], key="mod_" + str(i), use_container_width=True):
            st.session_state.active_module = i
            st.rerun()

if st.session_state.active_module is not None:
    mod = MODULES[st.session_state.active_module]
    st.markdown("<div class='sec'>" + mod["icon"] + " " + mod["title"] + " — Quick Prompts</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for j, prompt in enumerate(mod["prompts"]):
        with (col1 if j % 2 == 0 else col2):
            if st.button("▶  " + prompt, key="p_" + str(j), use_container_width=True):
                st.session_state.inject_prompt = prompt

st.divider()
st.markdown("<div class='sec'>💬 Chat</div>", unsafe_allow_html=True)

if not st.session_state.messages:
    st.success("✅ AgriAI is ready! Select a module above or type your question below.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🌾" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

injected = st.session_state.pop("inject_prompt", None)
prompt = injected or st.chat_input("Ask about rice disease detection, deep learning, papers, teaching...")

if prompt:
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🌾"):
        with st.spinner("AgriAI is thinking..."):
            try:
                reply = call_openrouter(st.session_state.api_key, st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.total_queries += 1
                st.rerun()
            except Exception as e:
                err = str(e)
                if "429" in err:
                    st.error("⚠️ Rate limit hit. Wait a moment and try again.")
                elif "401" in err:
                    st.error("❌ Invalid API key.")
                else:
                    st.error(f"Error: {err}")
