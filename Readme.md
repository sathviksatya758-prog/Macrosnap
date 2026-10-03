\# 🥗 MacroSnap



MacroSnap is an AI-powered nutrition assistant built with Streamlit and Google Gemini.



It allows users to enter a meal as text or upload a photo of their food. Gemini analyzes the meal and provides an estimated calorie and macronutrient breakdown. At the end of the conversation, MacroSnap can generate a complete nutrition summary and send it to the user's email.



\## ✨ Features



\- 💬 AI nutrition chat using Google Gemini

\- 📸 Meal photo analysis using Gemini Vision

\- 🔥 Estimated calorie calculation

\- 💪 Protein, carbohydrate, and fat estimates

\- 🧠 Conversation memory during the session

\- 📋 Automatic daily nutrition summary

\- 📧 Send the nutrition summary to email

\- 🎨 Simple Streamlit interface



\## 🛠️ Technologies Used



\- Python

\- Streamlit

\- Google Gemini API

\- Gmail SMTP

\- Python `smtplib`

\- Python `email` library



\## 📁 Project Structure



```text

Macrosnap/

├── app.py

├── prompts.py

├── requirements.txt

├── README.md

├── .gitignore

└── .streamlit/

&#x20;   ├── secrets.toml

&#x20;   └── secrets.toml.example

