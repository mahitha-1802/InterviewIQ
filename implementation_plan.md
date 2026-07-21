# Implementation Plan - InterviewIQ

InterviewIQ is a premium, AI-powered virtual interviewer application designed to simulate real-world technical and behavioral interviews using voice conversations and natural language. It features a modern Glassmorphism-inspired dark/light theme, interactive speech APIs, and detailed visual dashboards and reports.

## User Review Required

> [!IMPORTANT]
> **Gemini API Key**: The application will read the Gemini API Key from the environment variable `GEMINI_API_KEY`. Additionally, we will add an option in the **Settings** page allowing users to save their Gemini API Key in the database (encrypted), making it easier to run locally without configuring terminal environment variables.
>
> **Voice & Speech APIs**: The browser's native `SpeechSynthesis` and `webkitSpeechRecognition` (Web Speech API) are used. These work out-of-the-box in modern browsers (Chrome, Edge, Safari). No heavy cloud-based speech costs!

## Proposed Structure

The workspace will be organized as follows:
```
interviewIQ/
├── app.py                  # Flask Application entry point
├── config.py               # Configuration management
├── database.py             # Database models and helpers (SQLite)
├── schema.sql              # Database initialization schema
├── requirements.txt        # Backend dependencies
├── README.md               # Setup and execution instructions
├── services/
│   └── gemini_service.py   # Google Gemini API client & prompts
├── static/
│   ├── css/
│   │   └── style.css       # Core design system and variables
│   ├── js/
│   │   ├── main.js         # Navigation, sidebar, dark mode toggling
│   │   ├── charts.js       # Chart.js helper functions
│   │   └── interview.js    # Speech synthesis, voice recognition, audio visualizer
│   └── images/
│       └── avatar.svg      # AI Interviewer avatar asset
└── templates/
    ├── 404.html
    ├── base.html           # Main dashboard layout wrapper
    ├── dashboard.html      # User dashboard & metrics
    ├── feedback.html       # Detailed post-interview report
    ├── history.html        # Past interviews list with search/filter
    ├── interview.html      # Interactive interview arena (Zoom-like UI)
    ├── landing.html        # Premium marketing landing page
    ├── login.html          # Clean glassmorphism login
    ├── profile.html        # User Profile settings
    ├── register.html       # User Registration page
    ├── settings.html       # App configuration (Gemini Key, Dark Mode)
    └── setup.html          # Interview configuration form
```

---

## Component Specifications

### 1. Database Schema (`schema.sql`)
Using SQLite with foreign key constraints:
- `users`: ID, Username, Email, Password Hash, API Key (encrypted, optional), Created At
- `interviews`: ID, User ID, Category, Experience Level, Difficulty, Num Questions, Interview Type, Overall Score, Scores (Technical, Communication, Problem Solving, Confidence, Grammar, Professionalism), Strengths, Weaknesses, Topics to Improve, Recommended Path, Hiring Recommendation, Summary, Duration Seconds, Created At
- `questions`: ID, Interview ID, Question Text, Difficulty Level, Question Order, Created At
- `answers`: ID, Question ID, Answer Text, Technical Score, Communication Score, Completeness Score, Confidence Score, Grammar Score, Professionalism Score, Overall Score, Feedback Text, Suggestion Text, Created At

### 2. Backend Routes (`app.py`)
- `/` - Landing Page (No login required)
- `/register` - Registration GET/POST
- `/login` - Login GET/POST
- `/logout` - Logout (Login required)
- `/dashboard` - Dashboard with stats, recent activity, and charts
- `/setup` - Choose category, difficulty, level, and count
- `/interview/<interview_id>` - Voice/Text interview interface
- `/feedback/<interview_id>` - Final report display
- `/history` - View previous interviews (Search & Filter)
- `/profile` - View/Edit user credentials
- `/settings` - API Key management & app configurations
- `/api/start_interview` - POST: Initialize session
- `/api/get_question` - GET: Get current question
- `/api/submit_answer` - POST: Evaluate answer and prepare next question
- `/api/end_interview` - POST: Force-terminate and compile report

### 3. AI Service (`services/gemini_service.py`)
Utilizing Google Gemini API via structured prompts:
- **Question Generation**: Creates relevant interview questions based on category, experience, and current question difficulty.
- **Adaptive Difficulty Engine**: Adjusts difficulty (Easy, Medium, Hard, Expert) for subsequent questions depending on previous scores.
- **Real-time Feedback**: Evaluates each response against technical accuracy, communication, completeness, grammar, and professionalism.
- **Final Report Compiler**: Synthesizes all question evaluations into overall metrics, recommended learning paths, strengths/weaknesses, and hiring decisions.

### 4. Interactive Voice Flow (`static/js/interview.js`)
- **Speech Synthesis (TTS)**: Translates AI-generated question text to voice, selecting high-quality voice profiles.
- **Speech Recognition (STT)**: Activates after TTS completes, listening to the microphone, updating a visual soundwave animation, and transcribing live.
- **Meet-like UI**: Split-screen design with AI avatar on one side (with dynamic speaking/thinking animations) and candidate preview/wave-indicator on the other.

---

## Design System (`static/css/style.css`)
- **Aesthetic**: Modern SaaS feel with dynamic gradients, dark/light theme switching, and glassmorphism templates (backdrop blur, subtle border highlights, deep shadows).
- **Typography**: `Outfit` or `Inter` Google Fonts.
- **Animations**: Fluid transitions, glowing pulses for active microphone recording, and typing indicator logic.

## Verification Plan

### Automated Checks
- Test SQLite connection and migration setup on initial launch.
- Verify Gemini API client credentials via settings test connectivity endpoint.

### Manual Verification
- Complete full user lifecycle: Register -> Log in -> Setup Interview -> Complete 5-question voice interview -> Generate detailed feedback report -> View history list.
- Confirm dark mode persistent setting across multiple route visits.
- Test fallback behavior if Gemini API key is not supplied (meaningful instructions UI card instead of generic errors).
