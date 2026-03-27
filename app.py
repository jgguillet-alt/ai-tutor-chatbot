import streamlit as st
from anthropic import Anthropic

# --- Page Config ---
st.set_page_config(
    page_title="Platform AI School - AI Tutor",
    page_icon="🎓",
    layout="centered",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .main-header p {
        color: #888;
        font-size: 1.05rem;
        margin-top: 0.2rem;
    }
    .topic-btn button {
        width: 100%;
        text-align: left;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f6ff 0%, #eef0fb 100%);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🎓 Platform AI School</h1>
    <p>Your friendly AI tutor — ask anything about AI!</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 👋 Welcome!")
    st.markdown(
        "I'm your **AI tutor** from Platform AI School. "
        "I explain AI concepts in simple terms with examples. "
        "No question is too basic!"
    )
    st.divider()
    st.markdown("### 💡 Try asking about...")

    topics = [
        "What is Artificial Intelligence?",
        "Explain Machine Learning like I'm 5",
        "What is a Neural Network?",
        "How does ChatGPT work?",
        "What is Deep Learning?",
        "Supervised vs Unsupervised Learning",
        "What can I build with AI?",
        "How do I start learning AI?",
    ]

    for topic in topics:
        if st.button(topic, key=topic, use_container_width=True):
            st.session_state.pending_topic = topic

    st.divider()
    st.caption("Powered by Claude AI & Platform AI School")

# --- System Prompt ---
SYSTEM_PROMPT = """You are a friendly, patient, and encouraging AI tutor for Platform AI School.
Your students are absolute beginners who are curious about AI but may have no technical background.

Guidelines:
- Explain concepts in simple, everyday language. Avoid jargon unless you define it first.
- Use real-world analogies and examples to make concepts click.
- Break complex topics into small, digestible steps.
- Be warm and encouraging — celebrate curiosity and questions.
- When appropriate, suggest what to learn next.
- Keep responses concise but thorough (aim for 2-4 paragraphs unless more detail is asked for).
- Use emoji sparingly to keep things friendly 🎯
- If asked something outside AI/ML/data science, gently redirect to AI topics.
- Format responses with markdown for readability (bold key terms, use bullet points).
"""

# --- Init State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = Anthropic()

# --- Handle sidebar topic click ---
if "pending_topic" in st.session_state:
    topic = st.session_state.pending_topic
    del st.session_state.pending_topic
    st.session_state.messages.append({"role": "user", "content": topic})
    st.rerun()

# --- Display Chat History ---
for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask me anything about AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

# --- Generate Response ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Thinking..."):
            response = st.session_state.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            reply = response.content[0].text
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
