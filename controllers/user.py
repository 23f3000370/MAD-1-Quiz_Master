from flask import Blueprint, render_template, request, redirect, url_for, session
from models.setup_db import get_db_connection
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT QUIZES.id, QUIZES.quiz_name, QUIZES.date, QUIZES.duration, CHAPTERS.chapter_name
        FROM QUIZES
        JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
    ''')
    quizzes = cursor.fetchall()

    
    cursor.execute('''
        SELECT scores.id, QUIZES.quiz_name, scores.total_scored 
        FROM scores
        JOIN QUIZES ON scores.quiz_id = QUIZES.id
        WHERE scores.user_id = ?
    ''', (session['user_id'],))
    scores = cursor.fetchall()

    conn.close()
    return render_template('user/user_dashboard.html', quizzes=quizzes, scores=scores)


@user_bp.route('/quiz_attempt/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_attempt(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Fetch quiz duration
    cursor.execute("SELECT duration FROM QUIZES WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    duration = int(quiz[0]) if quiz and isinstance(quiz[0], int) else 10  # Default to 10 min if missing

    # ✅ Fetch questions for the quiz
    cursor.execute("SELECT * FROM QUESTIONS WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()

    feedback = []
    score = 0

    if request.method == 'POST':
        for question in questions:
            question_id = question[0]
            correct_answer = question[7]  # Correct answer from DB
            selected_answer = request.form.get(f'question_{question_id}')  # User-selected answer

            feedback.append({
                "question": question[2],
                "selected": selected_answer,
                "correct": correct_answer,
                "is_correct": selected_answer == correct_answer
            })

            if selected_answer == correct_answer:
                score += 1  # Increment score if answer is correct

        # ✅ Convert UTC time to IST before storing in the database
        ist_now = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d - %H:%M")

        # ✅ Insert the quiz attempt record with IST timestamp
        cursor.execute("""
            INSERT INTO SCORES (quiz_id, user_id, total_scored, timestamp) 
            VALUES (?, ?, ?, ?)
        """, (quiz_id, session['user_id'], score, ist_now))

        conn.commit()
        conn.close()

        return render_template('user/quiz_result.html', feedback=feedback, score=score, total=len(questions))

    conn.close()
    return render_template('user/quiz_attempt.html', questions=questions, quiz_id=quiz_id, duration=duration)


@user_bp.route('/scores')
def user_scores():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SCORES.id, QUIZES.quiz_name, SCORES.total_scored, SCORES.timestamp
        FROM SCORES
        JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
        WHERE SCORES.user_id = ?
        ORDER BY SCORES.timestamp DESC
    ''', (session['user_id'],))
    scores = cursor.fetchall()

    conn.close()
    return render_template('user/user_scores.html', scores=scores)


    
@user_bp.route('/user_summary')
def user_summary():
    print("Session Data:", session)  

    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))  

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
        SELECT SUBJECTS.subject_name, COUNT(SCORES.quiz_id) 
        FROM SCORES
        JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
        JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
        JOIN SUBJECTS ON CHAPTERS.subject_id = SUBJECTS.id
        WHERE SCORES.user_id = ?
        GROUP BY SUBJECTS.subject_name
    ''', (session['user_id'],))
    user_subject_attempts = cursor.fetchall()

    
    cursor.execute('''
        SELECT strftime('%Y-%m', SCORES.timestamp) AS month, COUNT(*)
        FROM SCORES
        WHERE SCORES.user_id = ?
        GROUP BY month
    ''', (session['user_id'],))
    user_month_attempts = cursor.fetchall()

    conn.close()
    return render_template(
        'user/user_summary.html',
        user_subject_attempts=user_subject_attempts,
        user_month_attempts=user_month_attempts
    )
