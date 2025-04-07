# 🧠 JeevaAI — AI-Powered Voice Assistant

**JeevaAI** is a voice-enabled desktop assistant that integrates speech recognition, AI chat, real-time weather updates, app launching, and email capabilities — all in one simple and interactive interface. Powered by Python and Streamlit, JeevaAI offers an intelligent, hands-free experience for everyday tasks.

---

## 🚀 Features

- 🎙️ **Voice Recognition** – Speak commands naturally using your microphone.
- 🤖 **AI Chat (OpenAI GPT)** – Get smart responses with ChatGPT integration.
- 🌦️ **Weather Reports** – Real-time temperature, humidity, and conditions by city.
- 📩 **Email Sending** – Compose and send emails using your Gmail account.
- 🖥️ **App Launcher** – Open installed applications like Chrome, Notepad, etc.
- 🔊 **Text-to-Speech** – Audible replies via text-to-speech (pyttsx3).
- 🧪 **Streamlit Interface** – Responsive, clean, and user-friendly interface.
- 🔐 **Secure Credentials** – API keys and login info stored in `.env` for security.

---

## 🧰 Tech Stack

- **Python**
- **Streamlit** – UI/UX
- **OpenAI API** – Smart conversation (ChatGPT)
- **SpeechRecognition + PyAudio** – For voice input
- **pyttsx3** – For text-to-speech response
- **OpenWeatherMap API** – Weather data
- **SMTP (Gmail)** – Email service
- **dotenv** – Secure environment variable handling

---

## 📁 Project Structure

| File/Folder         | Description                                         |
|---------------------|-----------------------------------------------------|
| `app_new.py`        | Main application script (Streamlit)                 |
| `.env`              | Stores private keys and credentials securely        |
| `requirements.txt`  | Python package dependencies                         |

---

## ⚙️ Core Functions

| Function               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `take_command()`       | Listens to user's voice and converts it to text                            |
| `speak(text)`          | Speaks back text responses using TTS                                       |
| `chat_with_gpt()`      | Communicates with OpenAI GPT to answer user queries                        |
| `get_weather(city)`    | Fetches live weather data (temperature, humidity, etc.)                    |
| `send_email()`         | Sends email through Gmail using SMTP and SSL                               |
| `open_app()`           | Launches desktop applications like Notepad or Chrome                       |

---

## 🎙️ Example Voice Commands

- “What’s the weather in Delhi?”
- “Open Notepad.”
- “Send an email to Rahul.”
- “Who is the president of the USA?”
- “Tell me a fun fact.”

---
