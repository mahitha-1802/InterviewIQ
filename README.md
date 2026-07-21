# InterviewIQ

**Practice. Improve. Get Hired.**

InterviewIQ is an AI-powered virtual interview simulator designed to help candidates prepare for real job interviews. The platform generates adaptive questions using Google Gemini, evaluates responses across six performance dimensions, and delivers comprehensive hiring reports with actionable feedback.

---

## Features

- **AI-Generated Questions** — Powered by Google Gemini 2.0 Flash, dynamically generates interview questions tailored to the selected category, experience level, and difficulty.
- **Adaptive Difficulty** — Automatically adjusts question difficulty based on response quality. Scoring above 80 increases difficulty; scoring below 55 decreases it.
- **Voice & Text Modes** — Supports spoken interviews via browser Speech Recognition (STT) and Speech Synthesis (TTS), or standard text input.
- **6-Dimension Evaluation** — Each answer is scored on Technical Accuracy, Communication, Completeness, Confidence, Grammar, and Professionalism.
- **Comprehensive Reports** — Post-interview reports include radar charts, strengths, weaknesses, improvement topics, a learning path, and a hiring recommendation.
- **12 Interview Categories** — Python, Java, C#, SQL, JavaScript, Full Stack, Machine Learning, Data Science, Customer Service, Marketing, Sales, and Behavioral/HR.
- **Custom Topics** — Enter any subject (e.g., Kubernetes, GraphQL, System Design) and the AI generates questions specifically around that topic.
- **Offline Fallback** — Works without a Gemini API key using built-in question banks and mock evaluations.
- **Encrypted API Keys** — User-provided Gemini keys are encrypted with AES-128 (Fernet) before database storage.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python, Flask, Flask-Login, Werkzeug |
| **AI Engine** | Google Gemini 2.0 Flash (google-genai / google-generativeai) |
| **Database** | SQLite3 with foreign key constraints |
| **Security** | Fernet symmetric encryption (cryptography library) |
| **Frontend** | HTML5, Jinja2 templates, Vanilla CSS, Vanilla JavaScript |
| **Speech** | Web Speech API (browser-native STT and TTS) |
| **Charts** | Chart.js (line and radar visualizations) |

---

## Project Structure

```
interviewIQ/
├── app.py                      Main application (routes and API endpoints)
├── config.py                   Application configuration
├── database.py                 Database models, queries, and encryption
├── schema.sql                  SQLite table definitions
├── requirements.txt            Python dependencies
│
├── services/
│   └── gemini_service.py       Gemini AI integration and fallback question banks
│
├── templates/
│   ├── base.html               Base layout with sidebar navigation
│   ├── landing.html            Public landing page
│   ├── login.html              Login form
│   ├── register.html           Registration form
│   ├── dashboard.html          User dashboard with stats and charts
│   ├── setup.html              Interview configuration form
│   ├── interview.html          Live interview room (video + chat)
│   ├── feedback.html           Post-interview report and analytics
│   ├── history.html            Past interview list with filters
│   ├── profile.html            User profile management
│   ├── settings.html           API key management
│   └── 404.html                Error page
│
└── static/
    ├── css/
    │   └── style.css           Complete application stylesheet
    └── js/
        ├── main.js             Theme toggling and sidebar logic
        ├── interview.js        Interview session controller
        └── charts.js           Chart.js rendering functions
```

---

## Installation

### Prerequisites
- Python 3.9 or higher
- A modern browser (Chrome, Edge, or Safari) for speech API support

### Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Gemini API Key** *(optional)*

   The application runs in sandbox mode automatically if no API key is provided. To enable full AI capabilities:

   - **Environment variable:**
     ```bash
     # Windows PowerShell
     $env:GEMINI_API_KEY="your_api_key_here"

     # Linux / macOS
     export GEMINI_API_KEY="your_api_key_here"
     ```

   - **In-app settings:** Log in, navigate to Settings, and enter your API key. It will be encrypted and stored securely.

3. **Start the server**
   ```bash
   python app.py
   ```

4. **Open the application**

   Navigate to [http://localhost:5000](http://localhost:5000) in your browser.

---

## User Flow

1. **Register** — Create an account on the landing page.
2. **Configure** — Select interview category, experience level, difficulty, question count, and mode (Voice or Text).
3. **Practice** — Grant camera and microphone permissions, listen to AI-spoken questions, and respond by voice or text.
4. **Review** — Complete all questions or end the session early to view your performance report with scores, radar charts, strengths, weaknesses, and a personalized learning path.
