# 🎤 Voice AI Assistant

A voice-driven AI assistant that transcribes voice commands using OpenAI's Whisper and responds with context-aware answers powered by Groq's LLaMA-3 and real-time web search using Serper.

## 🧠 Features

- 🎙️ Record voice commands directly from the browser
- 📝 Transcribe audio using Whisper
- 🤖 Generate intelligent responses using Groq's LLaMA-3 (70B)
- 🌐 Automatically trigger real-time web search using Google Serper API
- 🧵 Streamlined frontend (Streamlit) and backend (FastAPI)

---

## 🚀 Tech Stack

| Layer       | Technology |
|-------------|------------|
| Frontend    | Streamlit, HTML/CSS |
| Backend     | FastAPI, Whisper, LangChain, Groq, Google Serper |
| LLM         | LLaMA-3 (Groq) |
| APIs Used   | Google Serper API |
| Audio Model | OpenAI Whisper |

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/voice-ai-assistant.git
cd voice-ai-assistant
```

### 2. Environment Setup

Create a `.env` file in the backend directory and include the following:

```env
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key
WHISPER_MODEL=base  # or small, medium, large
```

Install dependencies:

```bash
pip install -r requirements.txt
```


> Note: For audio recording in Streamlit, ensure you have `audio-recorder-streamlit` installed.

### 3. Run Backend

```bash
uvicorn main:app --reload
```

### 4. Run Frontend

```bash
streamlit run streamlitapp.py
```

---

## 🌐 API Endpoints

- `POST /chat/voice`: Upload audio file and get transcript + AI response
- `POST /chat/text`: Send plain text (for testing without audio)


---

## 🧪 Example Use

1. Click the microphone icon
2. Speak your command clearly (e.g., "What’s the weather in Paris today?")
3. Wait a few seconds for the response
4. The assistant transcribes your query and replies
5. You’ll also see whether a web search was triggered


---


## 👨‍💻 Author

Developed by Sudais Alam


