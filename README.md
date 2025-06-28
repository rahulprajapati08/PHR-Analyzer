# 🧾 Patient Health Report Analyzer (v2.0)

> **Prototype rebuilt with Mistral LLM, LangChain, and a modern UI.**

This is an enhanced and efficient version of the **Patient Health Report Analyzer** project I initially created as a prototype. The earlier version focused on basic PDF parsing and keyword matching. In this release, I've rebuilt it using cutting-edge technologies like:

- 🧠 **Mistral LLM (via Ollama)** – for local, privacy-preserving AI inference
- 🔗 **LangChain** – for prompt management and chaining logic
- 📄 **PDF Parsing** – clean extraction of health report text using `pdfplumber`
- 💻 **Streamlit UI** – for an intuitive and interactive frontend

---

## 🧠 Features

- Upload and analyze health/lab PDF reports
- Extracts and summarizes:
  - 🔍 Key medical observations
  - ⚠️ Critical abnormalities or conditions
  - 📋 Suggested follow-ups or tests
  - ❓ Missing or ambiguous information
- All AI processing done locally via Mistral (no cloud model dependency)

---


## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/rahulprajapati08/PHR-Analyzer.git
   cd Next-Word-Predictor-using-GRU
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Install Ollama if not already installed, then run:
   ```bash
   ollama run mistral
4. Launch the App:
   ```bash
   streamlit run app.py

---

## 🖼️ Screenshots
![Screenshot 2025-06-28 214745](https://github.com/user-attachments/assets/43b769d3-a85e-4145-8446-842972ffac26)
![Screenshot 2025-06-28 215425](https://github.com/user-attachments/assets/4f4fb852-8960-4ffe-b368-6429cbb4c301)

---

## 📌 Notes
- This project is fully local and private — no external LLM APIs are used.
- You can deploy the Streamlit app online and expose your backend using ngrok or localtunnel.

---

## 🛠️ Future Improvements
- Add PDF export of summary
- Build patient history dashboard
- Integrate OCR for scanned reports


