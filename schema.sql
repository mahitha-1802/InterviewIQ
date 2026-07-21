CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    num_questions INTEGER NOT NULL,
    interview_type TEXT NOT NULL,
    overall_score REAL,
    technical_score REAL,
    communication_score REAL,
    problem_solving_score REAL,
    confidence_score REAL,
    grammar_score REAL,
    professionalism_score REAL,
    strengths TEXT,
    weaknesses TEXT,
    topics_to_improve TEXT,
    learning_path TEXT,
    hiring_recommendation TEXT,
    summary TEXT,
    duration_seconds INTEGER DEFAULT 0,
    status TEXT DEFAULT 'started',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    difficulty_level TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    technical_score REAL,
    communication_score REAL,
    completeness_score REAL,
    confidence_score REAL,
    grammar_score REAL,
    professionalism_score REAL,
    overall_score REAL,
    feedback_text TEXT,
    suggestion_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
