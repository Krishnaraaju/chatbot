import streamlit as st
import os
import time
from news_engine import fetch_outbreak_news
from rag_engine import get_ai_response, load_knowledge_base

# Page Config
st.set_page_config(page_title="Swasthya Sathi Demo", layout="wide")

# Load Environment Variables (or use st.secrets for Cloud)
# In a real scenario, we'd prefer st.secrets for Streamlit Cloud deployment
if "GEMINI_API_KEY" not in os.environ:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    else:
        st.warning("Please set GEMINI_API_KEY in .env or st.secrets")

# Title
st.title("🏥 Swasthya Sathi: Rural Health Companion")

# Layout
col1, col2 = st.columns([1, 1])

# --- LEFT COLUMN: ADMIN DASHBOARD ---
with col1:
    st.header("🛠️ Admin Dashboard")
    
    st.subheader("📢 Live News Ticker")
    if st.button("Refresh News"):
        with st.spinner("Fetching latest outbreak alerts..."):
            alert = fetch_outbreak_news()
            if alert:
                st.error(f"🚨 ALERT: {alert}")
                st.session_state['current_alert'] = alert
            else:
                st.success("✅ No critical outbreaks detected.")
                st.session_state['current_alert'] = None
    
    if 'current_alert' in st.session_state and st.session_state['current_alert']:
        st.info(f"Current Active Alert: {st.session_state['current_alert']}")

    st.divider()

    st.subheader("📂 Knowledge Base (Government PDFs)")
    data_dir = "gov_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    if files:
        st.write(f"Loaded {len(files)} documents:")
        for f in files:
            st.code(f"📄 {f}")
    else:
        st.warning("⚠️ No PDFs found in 'gov_data/'. Please add files.")

# --- RIGHT COLUMN: PHONE SIMULATOR ---
with col2:
    st.header("📱 WhatsApp Simulator")
    
    # Chat Container mimicking phone screen
    chat_container = st.container(height=500, border=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Type your health query..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Generate response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Swasthya Sathi is typing..."):
                    # Get alert context
                    current_alert = st.session_state.get('current_alert', None)
                    
                    # Call RAG Engine
                    response = get_ai_response(prompt, news_alert=current_alert)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.caption("Swasthya Sathi - Smart India Hackathon Project | Powered by Gemini 1.5 Flash")
