from flask import Flask, render_template, request, redirect, url_for,session,flash
import sqlite3 
from setup_db import initialize_database

def get_db_connection():
    conn = sqlite3.connect('quiz_master.db')
    conn.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign keys
    return conn

app = Flask(__name__)
app.secret_key = "your_secret_key"

initialize_database()

# Home Route (Welcome Page)
@app.route('/')
def home():
    return render_template('index.html')

# User Registration Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO USERS (username, password, full_name, qualification, dob) VALUES (?, ?, ?, ?, ?)",
                           (username, password, full_name, qualification, dob))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM USERS WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('user_dashboard'))
        return "Invalid username or password"
    return render_template('login.html')

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM ADMIN WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return "Invalid admin credentials"
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('login'))

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all subjects
    cursor.execute("SELECT * FROM SUBJECTS")
    subjects = cursor.fetchall()

    # Fetch all chapters with the number of questions
    cursor.execute("SELECT id, chapter_name, subject_id, no_of_question FROM CHAPTERS")
    chapters = cursor.fetchall()

    # Close connection
    conn.close()

    # Organizing chapters under subjects
    subject_dict = {sub[0]: {"id": sub[0], "name": sub[1], "chapters": []} for sub in subjects}
    
    for chap in chapters:
        subject_id = chap[2]
        if subject_id in subject_dict:
            subject_dict[subject_id]["chapters"].append({
                "id": chap[0], 
                "name": chap[1], 
                "no_of_question": chap[3]  # Include number of questions
            })

    return render_template('admin_dashboard.html', subjects=subject_dict.values())


# Delete Subject Route
@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

# Add Subject Route
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        # ✅ Validate input
        if not name:
            flash("Subject name is required!", "danger")
            return redirect(url_for('add_subject'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # ✅ Check if subject already exists
            cursor.execute("SELECT id FROM SUBJECTS WHERE subject_name = ?", (name,))
            if cursor.fetchone():
                flash("Error: Subject already exists!", "danger")
            else:
                cursor.execute("INSERT INTO SUBJECTS (subject_name) VALUES (?)", (name,))
                conn.commit()
                flash("Subject added successfully!", "success")

        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")

        finally:
            conn.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_subject.html')

    








@app.route('/add_chapter', methods=["GET", "POST"])
def add_chapter():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        chapter_name = request.form.get("chapter_name", "").strip()
        no_of_questions = request.form.get("no_of_questions", "").strip()
        subject_id = request.form.get("subject_id", "").strip()

        # ✅ Input validation
        if not chapter_name:
            flash("Chapter name is required!", "danger")
        elif not no_of_questions.isdigit():
            flash("Number of questions must be a number!", "danger")
        elif not subject_id.isdigit():
            flash("Invalid Subject ID!", "danger")
        else:
            subject_id = int(subject_id)
            no_of_questions = int(no_of_questions)

            # ✅ Check if subject_id exists before inserting
            cursor.execute("SELECT id FROM SUBJECTS WHERE id = ?", (subject_id,))
            if cursor.fetchone():
                cursor.execute("""
                    INSERT INTO CHAPTERS (chapter_name, no_of_question, subject_id) 
                    VALUES (?, ?, ?)""", 
                    (chapter_name, no_of_questions, subject_id))
                conn.commit()
                flash("Chapter added successfully!", "success")
            else:
                flash("Error: Subject ID does not exist!", "danger")

        conn.close()
        return redirect(url_for("admin_dashboard"))

    return render_template('add_chapter.html')


# Delete Chapter Route
@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))


@app.route('/view_quiz')
def view_quiz():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all quizzes
    cursor.execute("SELECT id, quiz_name FROM QUIZES")
    quizzes = cursor.fetchall()  # List of (quiz_id, quiz_name)

    # Fetch all questions with quiz_id
    cursor.execute("SELECT id, quiz_id, question_title FROM QUESTIONS")
    questions = cursor.fetchall()  # List of (question_id, quiz_id, question_title)

    conn.close()

    # Organizing questions under quizzes
    quiz_dict = {quiz[0]: {"id": quiz[0], "name": quiz[1], "questions": []} for quiz in quizzes}
    
    for question_id, quiz_id, question_title in questions:
        if quiz_id in quiz_dict:
            quiz_dict[quiz_id]["questions"].append({
                "id": question_id,  # ✅ Now includes question ID
                "question_title": question_title  # ✅ Question title as expected
            })

    return render_template('view_quiz.html', quizes=quiz_dict.values())




@app.route('/add_quiz', methods=["GET", "POST"])
def add_quiz():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == "POST":
        quiz_name = request.form.get("quiz_name", "").strip()
        chapter_id = request.form.get("chapter_id", "").strip()
        date = request.form.get("date", "").strip()
        duration = request.form.get("duration", "").strip()

        # ✅ Input validation
        if not quiz_name:
            flash("Quiz name is required!", "danger")
            return redirect(url_for("add_quiz"))

        if not chapter_id.isdigit():
            flash("Invalid Chapter ID!", "danger")
            return redirect(url_for("add_quiz"))

        if not duration.isdigit():
            flash("Duration must be a valid number!", "danger")
            return redirect(url_for("add_quiz"))

        chapter_id = int(chapter_id)
        duration = int(duration)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # ✅ Check if chapter_id exists
            cursor.execute("SELECT id FROM CHAPTERS WHERE id = ?", (chapter_id,))
            if not cursor.fetchone():
                flash("Error: Chapter ID does not exist!", "danger")
                return redirect(url_for("add_quiz"))

            # ✅ Insert into QUIZES
            cursor.execute("""
                INSERT INTO QUIZES (quiz_name, chapter_id, date, duration) 
                VALUES (?, ?, ?, ?)""",
                (quiz_name, chapter_id, date, duration))
            conn.commit()
            flash("Quiz added successfully!", "success")

        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")

        finally:
            conn.close()

        return redirect(url_for("view_quiz"))

    return render_template("add_quiz.html")


# Delete Quiz Route
@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM QUIZES WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_quiz'))

@app.route('/add_question', methods=["GET", "POST"])
def add_question():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == "POST":
        question_title = request.form.get("question_title", "").strip()
        question = request.form.get("question", "").strip()
        option1 = request.form.get("option1", "").strip()
        option2 = request.form.get("option2", "").strip()
        option3 = request.form.get("option3", "").strip()
        option4 = request.form.get("option4", "").strip()
        correct = request.form.get("answer", "").strip()
        quiz_id = request.form.get("quiz_id", "").strip()

        # ✅ Input Validation
        if not question_title or not question or not option1 or not option2 or not option3 or not option4:
            flash("All fields are required!", "danger")
            return redirect(url_for("add_question"))

        if not quiz_id.isdigit():
            flash("Invalid Quiz ID!", "danger")
            return redirect(url_for("add_question"))

        quiz_id = int(quiz_id)

        if correct not in [option1, option2, option3, option4]:
            flash("Correct answer must match one of the provided options!", "danger")
            return redirect(url_for("add_question"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # ✅ Check if quiz_id exists
            cursor.execute("SELECT id FROM QUIZES WHERE id = ?", (quiz_id,))
            if not cursor.fetchone():
                flash("Error: Quiz ID does not exist!", "danger")
                return redirect(url_for("add_question"))

            # ✅ Insert question into database
            cursor.execute("""
                INSERT INTO QUESTIONS (question_title, question, option1, option2, option3, option4, answer, quiz_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (question_title, question, option1, option2, option3, option4, correct, quiz_id))
            conn.commit()
            flash("Question added successfully!", "success")

        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")

        finally:
            conn.close()

        return redirect(url_for('view_quiz'))

    return render_template("add_question.html")


# Delete Question Route
@app.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_quiz'))


    
    
    
           
# User Dashboard Route
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch quizzes with chapter names
    cursor.execute('''
        SELECT QUIZES.id, QUIZES.quiz_name, QUIZES.date, QUIZES.duration, CHAPTERS.chapter_name
        FROM QUIZES
        JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
    ''')
    quizzes = cursor.fetchall()

    # Fetch user scores
    cursor.execute('''
        SELECT scores.id, QUIZES.quiz_name, scores.total_scored 
        FROM scores
        JOIN QUIZES ON scores.quiz_id = QUIZES.id
        WHERE scores.user_id = ?
    ''', (session['user_id'],))
    scores = cursor.fetchall()
    
    conn.close()
    
    return render_template('user_dashboard.html', quizzes=quizzes, scores=scores)


# Attempt Quiz Route
@app.route('/quiz_attempt/<int:quiz_id>', methods=['GET', 'POST'])
def quiz_attempt(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch quiz duration from the QUIZES table
    cursor.execute("SELECT duration FROM QUIZES WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    duration = int(quiz[0]) if quiz and isinstance(quiz[0], int) else 10  # Default duration (if not found)

    cursor.execute("SELECT * FROM QUESTIONS WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()
    
    feedback = []  # Store feedback for each question
    score = 0  # Track the score

    if request.method == 'POST':
        for question in questions:
            question_id = question[0]
            correct_answer = question[7]  # Correct answer from DB
            selected_answer = request.form.get(f'question_{question_id}')  # User's choice

            # Store feedback
            feedback.append({
                "question": question[2],  # Question text
                "selected": selected_answer,
                "correct": correct_answer,
                "is_correct": selected_answer == correct_answer
            })

            # Calculate score
            if selected_answer == correct_answer:
                score += 1
        
        # Store score in the database
        cursor.execute("INSERT INTO SCORES (quiz_id, user_id, total_scored) VALUES (?, ?, ?)",
                       (quiz_id, session['user_id'], score))
        conn.commit()
        conn.close()

        # Pass feedback to results page
        return render_template('quiz_result.html', feedback=feedback, score=score, total=len(questions))

    conn.close()
    return render_template('quiz_attempt.html', questions=questions, quiz_id=quiz_id, duration=duration)







    



@app.route('/user_scores')
def user_scores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user scores with timestamps
    cursor.execute('''
        SELECT SCORES.id, QUIZES.quiz_name, SCORES.total_scored, SCORES.timestamp
        FROM SCORES
        JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
        WHERE SCORES.user_id = ?
        ORDER BY SCORES.timestamp DESC
    ''', (session['user_id'],))
    scores = cursor.fetchall()
    
    conn.close()
    
    return render_template('user_scores.html', scores=scores)


@app.route('/summary')
def summary():
    print("Session Data:", session)  # Debugging session contents

    if session.get('admin'):  # If admin is logged in
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch subject-wise user attempts
        cursor.execute('''
            SELECT SUBJECTS.subject_name, COUNT(DISTINCT SCORES.user_id) 
            FROM SCORES
            JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
            JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
            JOIN SUBJECTS ON CHAPTERS.subject_id = SUBJECTS.id
            GROUP BY SUBJECTS.subject_name
        ''')
        subject_attempts = cursor.fetchall()

        # Fetch subject-wise top scores
        cursor.execute('''
            SELECT SUBJECTS.subject_name, MAX(SCORES.total_scored)
            FROM SCORES
            JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
            JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
            JOIN SUBJECTS ON CHAPTERS.subject_id = SUBJECTS.id
            GROUP BY SUBJECTS.subject_name
        ''')
        subject_top_scores = cursor.fetchall()

        conn.close()
        return render_template(
            'admin_summary.html',
            subject_attempts=subject_attempts,
            subject_top_scores=subject_top_scores
        )

    elif session.get('user_id'):  # If normal user is logged in
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch subject-wise quizzes attempted by the user
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

        # Fetch month-wise quizzes attempted by the user
        cursor.execute('''
            SELECT strftime('%Y-%m', SCORES.timestamp) AS month, COUNT(*)
            FROM SCORES
            WHERE SCORES.user_id = ?
            GROUP BY month
        ''', (session['user_id'],))
        user_month_attempts = cursor.fetchall()

        conn.close()
        return render_template(
            'user_summary.html',
            user_subject_attempts=user_subject_attempts,
            user_month_attempts=user_month_attempts
        )

    else:
        return redirect(url_for('login'))  # Redirect if not logged in


@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        chapter_name = request.form['chapter_name']
        no_of_question = request.form['no_of_question']

        cursor.execute("UPDATE CHAPTERS SET chapter_name=?, no_of_question=? WHERE id = ?", 
                       (chapter_name, no_of_question ,chapter_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))  

    cursor.execute("SELECT * FROM CHAPTERS WHERE id = ?", (chapter_id,))
    chapter = cursor.fetchone()
    conn.close()
    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_name = request.form['quiz_name']
        new_date = request.form['date_of_quiz']
        new_duration = request.form['duration']

        cursor.execute("UPDATE QUIZES SET quiz_name = ?, date = ?, duration = ? WHERE id = ?", 
                       (new_name, new_date, new_duration, quiz_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))  

    cursor.execute("SELECT * FROM QUIZES WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    conn.close()
    return render_template('edit_quiz.html', quiz=quiz)

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':  # Update subject
        subject_name = request.form['subject_name']
        cursor.execute('''
            UPDATE SUBJECTS SET subject_name = ? WHERE id = ?
        ''', (subject_name, subject_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    cursor.execute("SELECT id, subject_name FROM SUBJECTS WHERE id = ?", (subject_id,))
    subject = cursor.fetchone()
    conn.close()

    return render_template('edit_subject.html', subject=subject)

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        question_title = request.form['question_title']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        cursor.execute('''
            UPDATE QUESTIONS 
            SET question_title = ?, option1 = ?, option2 = ?, option3 = ?, option4 = ?, answer = ?
            WHERE id = ?
        ''', (question_title, option1, option2, option3, option4, answer, question_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_quiz'))

    cursor.execute("SELECT * FROM QUESTIONS WHERE id = ?", (question_id,))
    question = cursor.fetchone()
    conn.close()

    return render_template('edit_question.html', question=question)


@app.route('/search_admin', methods=['GET'])
def search_admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    query = request.args.get('query', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Search across multiple tables
    cursor.execute("SELECT * FROM SUBJECTS WHERE subject_name LIKE ?", ('%' + query + '%',))
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM CHAPTERS WHERE chapter_name LIKE ?", ('%' + query + '%',))
    chapters = cursor.fetchall()

    cursor.execute("SELECT * FROM QUIZES WHERE quiz_name LIKE ?", ('%' + query + '%',))
    quizzes = cursor.fetchall()

    cursor.execute("SELECT * FROM QUESTIONS WHERE question_title LIKE ?", ('%' + query + '%',))
    questions = cursor.fetchall()

    conn.close()

    return render_template('admin_search_results.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)






    





    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

