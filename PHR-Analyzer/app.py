import streamlit as st
import os
from parser import extract_text_from_pdf, clean_report_text
from analyzer import analyze_report

st.set_page_config(page_title="Patient Health Report Analyzer", layout="wide")

st.title("🧾 Patient Health Report Analyzer")
st.markdown("Upload a patient's health report in PDF format and get AI-generated insights.")

# Upload Section
uploaded_file = st.file_uploader("📤 Upload PDF Report", type=["pdf"])

if uploaded_file:
    # Save uploaded file
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    file_path = os.path.join("reports", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Text Extraction
    st.subheader("📄 Extracted Report Text")
    report_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_report_text(report_text)
    st.text_area("Text Extracted from PDF:", cleaned_text, height=300)

    # Analyze Button
    if st.button("🔍 Analyze Report"):
        with st.spinner("Analyzing with Mistral..."):
            result = analyze_report(cleaned_text)
        st.subheader("📊 AI Analysis Result")
        st.markdown(result.replace("**", "**").replace("\n", "  \n"))
