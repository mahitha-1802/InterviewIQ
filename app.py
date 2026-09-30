import json
import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import (
    init_db,
    query_db,
    execute_db,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    encrypt_key,
    decrypt_key
)
from services.gemini_service import GeminiService

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route("/")
def index():
    return render_template("landing.html", hide_sidebar=True)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All form parameters are required.")
            return redirect(url_for("register"))

        if get_user_by_username(username):
            flash("Username is already registered.")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("Email address is already registered.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        execute_db(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )

        user = get_user_by_username(username)
        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("register.html", hide_sidebar=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials entered.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("login.html", hide_sidebar=True)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    interviews = query_db(
        "SELECT * FROM interviews WHERE user_id = ? AND status = 'completed' ORDER BY id DESC",
        (current_user.id,)
    )
    total_interviews = len(interviews)

    avg_score = 0
    duration_sum = 0
    if total_interviews > 0:
        scores = [row["overall_score"] for row in interviews if row["overall_score"] is not None]
        avg_score = int(sum(scores) / len(scores)) if scores else 0
        duration_sum = int(sum([row["duration_seconds"] for row in interviews]) / 60)

    total_questions = len(query_db("SELECT id FROM answers WHERE user_id = ?", (current_user.id,)))

    chart_labels = []
    chart_values = []
    chronological_interviews = list(reversed(interviews[:10]))
    for idx, interview in enumerate(chronological_interviews):
        chart_labels.append(f"S{idx+1} ({interview['category']})")
        chart_values.append(interview["overall_score"] or 0)

    return render_template(
        "dashboard.html",
        total_interviews=total_interviews,
        avg_score=avg_score,
        total_questions=total_questions,
        duration_sum=duration_sum,
        recent_interviews=interviews[:5],
        chart_data={"labels": chart_labels, "values": chart_values}
    )


@app.route("/setup")
@login_required
def setup():
    return render_template("setup.html")


@app.route("/interview/<int:interview_id>")
@login_required
def interview(interview_id):
    interview_data = query_db(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id),
        one=True
    )
    if not interview_data:
        return redirect(url_for("dashboard"))

    return render_template("interview.html", interview=interview_data)


@app.route("/feedback/<int:interview_id>")
@login_required
def feedback(interview_id):
    interview_data = query_db(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id),
        one=True
    )
    if not interview_data:
        return redirect(url_for("dashboard"))

    if interview_data["status"] != "completed" or interview_data["overall_score"] is None:
        finalize_interview_report(interview_id)
        interview_data = query_db(
            "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
            (interview_id, current_user.id),
            one=True
        )

    strengths = []
    weaknesses = []
    topics = []
    path = []

    try:
        if interview_data["strengths"]:
            strengths = json.loads(interview_data["strengths"])
    except Exception:
        strengths = [interview_data["strengths"]]

    try:
        if interview_data["weaknesses"]:
            weaknesses = json.loads(interview_data["weaknesses"])
    except Exception:
        weaknesses = [interview_data["weaknesses"]]

    try:
        if interview_data["topics_to_improve"]:
            topics = json.loads(interview_data["topics_to_improve"])
    except Exception:
        topics = [interview_data["topics_to_improve"]]

    try:
        if interview_data["learning_path"]:
            path = json.loads(interview_data["learning_path"])
    except Exception:
        path = [interview_data["learning_path"]]

    return render_template(
        "feedback.html",
        interview=interview_data,
        strengths_list=strengths,
        weaknesses_list=weaknesses,
        topics_list=topics,
        path_list=path
    )


@app.route("/history")
@login_required
def history():
    search_query = request.args.get("search", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()

    query = "SELECT * FROM interviews WHERE user_id = ?"
    params = [current_user.id]

    if search_query:
        query += " AND category LIKE ?"
        params.append(f"%{search_query}%")

    if difficulty_filter:
        query += " AND difficulty = ?"
        params.append(difficulty_filter)

    query += " ORDER BY id DESC"
    interviews = query_db(query, tuple(params))

    return render_template(
        "history.html",
        interviews=interviews,
        search_query=search_query,
        difficulty_filter=difficulty_filter
    )


@app.route("/history/delete/<int:interview_id>", methods=["POST"])
@login_required
def delete_interview(interview_id):
    execute_db(
        "DELETE FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id)
    )
    flash("Interview report successfully removed.")
    return redirect(url_for("history"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()

            if not username or not email:
                flash("Form fields cannot be empty.")
                return redirect(url_for("profile"))

            existing_user = get_user_by_username(username)
            if existing_user and existing_user.id != current_user.id:
                flash("Username is already taken.")
                return redirect(url_for("profile"))

            existing_email = get_user_by_email(email)
            if existing_email and existing_email.id != current_user.id:
                flash("Email is already registered.")
                return redirect(url_for("profile"))

            execute_db(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                (username, email, current_user.id)
            )
            flash("Profile updated successfully.")
            return redirect(url_for("profile"))

        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")

            user = get_user_by_id(current_user.id)
            if not check_password_hash(user.password_hash, current_pw):
                flash("Incorrect current password.")
                return redirect(url_for("profile"))

            execute_db(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(new_pw), current_user.id)
            )
            flash("Password updated successfully.")
            return redirect(url_for("profile"))

    return render_template("profile.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = get_user_by_id(current_user.id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_api_key":
            if request.form.get("clear_key"):
                execute_db("UPDATE users SET api_key = NULL WHERE id = ?", (current_user.id,))
                flash("Gemini API Key cleared.")
            else:
                key = request.form.get("api_key", "").strip()
                if key:
                    encrypted = encrypt_key(key)
                    execute_db("UPDATE users SET api_key = ? WHERE id = ?", (encrypted, current_user.id))
                    flash("Gemini API Key successfully updated.")
                else:
                    flash("API Key input was empty.")
            return redirect(url_for("settings"))

    return render_template("settings.html", has_api_key=(user.api_key is not None))


def finalize_interview_report(interview_id, duration_seconds=0):
    interview_data = query_db(
        "SELECT * FROM interviews WHERE id = ?",
        (interview_id,),
        one=True
    )
    if not interview_data or interview_data["status"] == "completed":
        return

    qa_rows = query_db(
        """SELECT q.question_text, a.answer_text, a.overall_score, a.feedback_text 
           FROM questions q 
           JOIN answers a ON a.question_id = q.id 
           WHERE q.interview_id = ? ORDER BY q.question_order ASC""",
        (interview_id,)
    )

    if not qa_rows:
        execute_db(
            "UPDATE interviews SET status = 'completed', duration_seconds = ? WHERE id = ?",
            (duration_seconds or interview_data["duration_seconds"], interview_id)
        )
        return

    qa_history = []
    for row in qa_rows:
        qa_history.append({
            "question": row["question_text"],
            "answer": row["answer_text"],
            "overall_score": row["overall_score"],
            "feedback": row["feedback_text"]
        })

    user = get_user_by_id(interview_data["user_id"])
    user_api_key = decrypt_key(user.api_key) if user.api_key else None
    ai_service = GeminiService(api_key=user_api_key)

    report = ai_service.compile_final_report(
        interview_data["category"],
        interview_data["experience_level"],
        interview_data["difficulty"],
        qa_history
    )

    execute_db(
        """UPDATE interviews SET 
           overall_score = ?, technical_score = ?, communication_score = ?, 
           problem_solving_score = ?, confidence_score = ?, grammar_score = ?, 
           professionalism_score = ?, strengths = ?, weaknesses = ?, 
           topics_to_improve = ?, learning_path = ?, hiring_recommendation = ?, 
           summary = ?, duration_seconds = ?, status = 'completed' 
           WHERE id = ?""",
        (
            report["overall_score"],
            report["technical_score"],
            report["communication_score"],
            report["problem_solving_score"],
            report["confidence_score"],
            report["grammar_score"],
            report["professionalism_score"],
            json.dumps(report["strengths"]),
            json.dumps(report["weaknesses"]),
            json.dumps(report["topics_to_improve"]),
            json.dumps(report["learning_path"]),
            report["hiring_recommendation"],
            report["summary"],
            duration_seconds or interview_data["duration_seconds"],
            interview_id
        )
    )


@app.route("/api/start_interview", methods=["POST"])
@login_required
def api_start_interview():
    category       = request.form.get("category", "Python").strip()
    experience_level = request.form.get("experience_level", "Fresher")
    difficulty     = request.form.get("difficulty", "Medium")
    num_questions  = int(request.form.get("num_questions", 5))
    interview_type = request.form.get("interview_type", "Voice")

    if category.lower() == "custom":
        custom_topic = request.form.get("custom_topic", "").strip()
        category = custom_topic if custom_topic else "Python"

    interview_id = execute_db(
        """INSERT INTO interviews 
           (user_id, category, experience_level, difficulty, num_questions, interview_type, status) 
           VALUES (?, ?, ?, ?, ?, ?, 'started')""",
        (current_user.id, category, experience_level, difficulty, num_questions, interview_type)
    )

    return redirect(url_for("interview", interview_id=interview_id))


@app.route("/api/get_question")
@login_required
def api_get_question():
    interview_id = request.args.get("interview_id", type=int)
    interview_data = query_db(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id),
        one=True
    )
    if not interview_data:
        return jsonify({"error": "Invalid interview session"}), 404

    existing_questions = query_db(
        "SELECT * FROM questions WHERE interview_id = ? ORDER BY question_order ASC",
        (interview_id,)
    )
    total_generated = len(existing_questions)

    if total_generated >= interview_data["num_questions"]:
        return jsonify({"status": "completed"})

    unanswered = None
    if total_generated > 0:
        last_q = existing_questions[-1]
        answered_check = query_db(
            "SELECT id FROM answers WHERE question_id = ?",
            (last_q["id"],),
            one=True
        )
        if not answered_check:
            unanswered = last_q

    if unanswered:
        return jsonify({
            "question_id": unanswered["id"],
            "question_order": unanswered["question_order"],
            "question_text": unanswered["question_text"],
            "status": "active"
        })

    history = [q["question_text"] for q in existing_questions]

    current_difficulty = interview_data["difficulty"]
    if total_generated > 0:
        last_answers = query_db(
            """SELECT a.overall_score FROM answers a 
               JOIN questions q ON a.question_id = q.id 
               WHERE q.interview_id = ? ORDER BY a.id DESC LIMIT 1""",
            (interview_id,),
            one=True
        )
        if last_answers:
            score = last_answers["overall_score"]
            diffs = ["Easy", "Medium", "Hard", "Expert"]
            curr_idx = diffs.index(current_difficulty) if current_difficulty in diffs else 1
            if score >= 80 and curr_idx < 3:
                current_difficulty = diffs[curr_idx + 1]
            elif score < 55 and curr_idx > 0:
                current_difficulty = diffs[curr_idx - 1]

    user = get_user_by_id(current_user.id)
    user_api_key = decrypt_key(user.api_key) if user.api_key else None
    ai_service = GeminiService(api_key=user_api_key)

    q_text, q_diff = ai_service.generate_question(
        interview_data["category"],
        interview_data["experience_level"],
        current_difficulty,
        history
    )

    new_q_id = execute_db(
        """INSERT INTO questions (interview_id, question_text, difficulty_level, question_order) 
           VALUES (?, ?, ?, ?)""",
        (interview_id, q_text, q_diff, total_generated + 1)
    )

    return jsonify({
        "question_id": new_q_id,
        "question_order": total_generated + 1,
        "question_text": q_text,
        "status": "active"
    })


@app.route("/api/submit_answer", methods=["POST"])
@login_required
def api_submit_answer():
    data = request.get_json()
    interview_id = data.get("interview_id")
    question_id = data.get("question_id")
    answer_text = data.get("answer_text", "").strip()

    interview_data = query_db(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id),
        one=True
    )
    if not interview_data:
        return jsonify({"error": "Invalid interview session"}), 404

    question_data = query_db(
        "SELECT * FROM questions WHERE id = ? AND interview_id = ?",
        (question_id, interview_id),
        one=True
    )
    if not question_data:
        return jsonify({"error": "Invalid question parameter"}), 404

    user = get_user_by_id(current_user.id)
    user_api_key = decrypt_key(user.api_key) if user.api_key else None
    ai_service = GeminiService(api_key=user_api_key)

    eval_result = ai_service.evaluate_answer(question_data["question_text"], answer_text)

    execute_db(
        """INSERT INTO answers 
           (question_id, user_id, answer_text, technical_score, communication_score, 
            completeness_score, confidence_score, grammar_score, professionalism_score, 
            overall_score, feedback_text, suggestion_text) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            question_id,
            current_user.id,
            answer_text,
            eval_result["technical_score"],
            eval_result["communication_score"],
            eval_result["completeness_score"],
            eval_result["confidence_score"],
            eval_result["grammar_score"],
            eval_result["professionalism_score"],
            eval_result["overall_score"],
            eval_result["feedback_text"],
            eval_result["suggestion_text"]
        )
    )

    total_answered = len(query_db(
        """SELECT a.id FROM answers a 
           JOIN questions q ON a.question_id = q.id 
           WHERE q.interview_id = ?""",
        (interview_id,)
    ))

    if total_answered >= interview_data["num_questions"]:
        finalize_interview_report(interview_id)
        return jsonify({"status": "completed"})

    return jsonify({"status": "saved"})


@app.route("/api/end_interview", methods=["POST"])
@login_required
def api_end_interview():
    data = request.get_json()
    interview_id = data.get("interview_id")
    duration_seconds = data.get("duration_seconds", 0)

    finalize_interview_report(interview_id, duration_seconds)
    return jsonify({"status": "completed"})


@app.route("/api/custom_question", methods=["POST"])
@login_required
def api_custom_question():
    """Generate an interview question for a user-supplied topic using a provided Gemini API key."""
    data = request.get_json()
    topic      = (data.get("topic")      or "").strip()
    api_key    = (data.get("api_key")    or "").strip()
    experience = (data.get("experience") or "Fresher").strip()
    difficulty = (data.get("difficulty") or "Medium").strip()
    history    = data.get("history", [])

    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    ai_service = GeminiService(api_key=api_key)
    if not ai_service.has_active_client():
        return jsonify({"error": "Invalid or inactive Gemini API key"}), 401

    question_text, question_difficulty = ai_service.generate_question(
        category=topic,
        experience=experience,
        difficulty=difficulty,
        history=history
    )
    return jsonify({
        "question":   question_text,
        "difficulty": question_difficulty,
        "topic":      topic
    })


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", hide_sidebar=True), 404

init_db()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
