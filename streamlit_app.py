import streamlit as st

st.set_page_config(
    page_title="AI Career Platform",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI-Powered Career Intelligence")

st.write(
    "Welcome to the AI Career Platform. "
    "Analyze your resume and get personalized career guidance."
)

st.subheader("📄 Resume Analysis")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    st.success(f"Resume uploaded: {uploaded_file.name}")

    if st.button("🚀 Analyze Resume"):
        st.info("Resume analysis will be connected to the AI backend.")