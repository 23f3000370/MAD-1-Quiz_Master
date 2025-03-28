from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.setup_db import get_db_connection

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login')) 

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SUBJECTS")
    subjects = cursor.fetchall()

    
    cursor.execute("SELECT id, chapter_name, subject_id, no_of_question FROM CHAPTERS")
    chapters = cursor.fetchall()
    conn.close()

    
    subject_dict = {sub[0]: {"id": sub[0], "name": sub[1], "chapters": []} for sub in subjects}
    
    for chap in chapters:
        subject_id = chap[2]
        if subject_id in subject_dict:
            subject_dict[subject_id]["chapters"].append({
                "id": chap[0], 
                "name": chap[1], 
                "no_of_question": chap[3]
            })

    return render_template('admin/admin_dashboard.html', subjects=subject_dict.values())



@admin_bp.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            flash("Subject name is required!", "danger")
            return redirect(url_for('admin.add_subject'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
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

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_subject.html')


@admin_bp.route('/add_chapter', methods=["GET", "POST"])
def add_chapter():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        chapter_name = request.form.get("chapter_name", "").strip()
        no_of_questions = request.form.get("no_of_questions", "").strip()
        subject_id = request.form.get("subject_id", "").strip()

        if not chapter_name:
            flash("Chapter name is required!", "danger")
        elif not no_of_questions.isdigit():
            flash("Number of questions must be a number!", "danger")
        elif not subject_id.isdigit():
            flash("Invalid Subject ID!", "danger")
        else:
            subject_id = int(subject_id)
            no_of_questions = int(no_of_questions)

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
        return redirect(url_for("admin.admin_dashboard"))

    return render_template('admin/add_chapter.html')

@admin_bp.route('/add_quiz', methods=["GET", "POST"])
def add_quiz():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    if request.method == "POST":
        quiz_name = request.form.get("quiz_name", "").strip()
        chapter_id = request.form.get("chapter_id", "").strip()
        date = request.form.get("date", "").strip()
        duration = request.form.get("duration", "").strip()

      
        if not quiz_name:
            flash("Quiz name is required!", "danger")
            return redirect(url_for("admin.add_quiz"))

        if not chapter_id.isdigit():
            flash("Invalid Chapter ID!", "danger")
            return redirect(url_for("admin.add_quiz"))

        if not duration.isdigit():
            flash("Duration must be a valid number!", "danger")
            return redirect(url_for("admin.add_quiz"))

        chapter_id = int(chapter_id)
        duration = int(duration)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
           
            cursor.execute("SELECT id FROM CHAPTERS WHERE id = ?", (chapter_id,))
            if not cursor.fetchone():
                flash("Error: Chapter ID does not exist!", "danger")
                return redirect(url_for("admin.view_quiz"))

           
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

        return redirect(url_for("admin.view_quiz"))

    return render_template("admin/add_quiz.html")

@admin_bp.route('/add_question', methods=["GET", "POST"])
def add_question():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    if request.method == "POST":
        question_title = request.form.get("question_title", "").strip()
        question = request.form.get("question", "").strip()
        option1 = request.form.get("option1", "").strip()
        option2 = request.form.get("option2", "").strip()
        option3 = request.form.get("option3", "").strip()
        option4 = request.form.get("option4", "").strip()
        correct = request.form.get("answer", "").strip()
        quiz_id = request.form.get("quiz_id", "").strip()

        
        if not question_title or not question or not option1 or not option2 or not option3 or not option4:
            flash("All fields are required!", "danger")
            return redirect(url_for("admin.add_question"))

        if not quiz_id.isdigit():
            flash("Invalid Quiz ID!", "danger")
            return redirect(url_for("admin.view_quiz"))

        quiz_id = int(quiz_id)

        if correct not in [option1, option2, option3, option4]:
            flash("Correct answer must match one of the provided options!", "danger")
            return redirect(url_for("admin.add_question"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            
            cursor.execute("SELECT id FROM QUIZES WHERE id = ?", (quiz_id,))
            if not cursor.fetchone():
                flash("Error: Quiz ID does not exist!", "danger")
                return redirect(url_for("admin.add_question"))

            
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

        return redirect(url_for('admin.view_quiz'))

    return render_template("admin/add_question.html")


@admin_bp.route('/view_quiz')
def view_quiz():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT id, quiz_name FROM QUIZES")
    quizzes = cursor.fetchall()

    
    cursor.execute("SELECT id, quiz_id, question_title FROM QUESTIONS")
    questions = cursor.fetchall()
    conn.close()

    quiz_dict = {quiz[0]: {"id": quiz[0], "name": quiz[1], "questions": []} for quiz in quizzes}
    
    for question_id, quiz_id, question_title in questions:
        if quiz_id in quiz_dict:
            quiz_dict[quiz_id]["questions"].append({
                "id": question_id,
                "question_title": question_title
            })

    return render_template('admin/view_quiz.html', quizes=quiz_dict.values())


@admin_bp.route('/search_admin', methods=['GET'])
def search_admin():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    query = request.args.get('query', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM SUBJECTS WHERE subject_name LIKE ?", ('%' + query + '%',))
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM CHAPTERS WHERE chapter_name LIKE ?", ('%' + query + '%',))
    chapters = cursor.fetchall()

    cursor.execute("SELECT * FROM QUIZES WHERE quiz_name LIKE ?", ('%' + query + '%',))
    quizzes = cursor.fetchall()

    cursor.execute("SELECT * FROM QUESTIONS WHERE question_title LIKE ?", ('%' + query + '%',))
    questions = cursor.fetchall()

    conn.close()

    return render_template('admin/admin_search_results.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)


@admin_bp.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM QUIZES WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.view_quiz'))


@admin_bp.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.view_quiz'))

@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_dashboard'))  

    cursor.execute("SELECT * FROM CHAPTERS WHERE id = ?", (chapter_id,))
    chapter = cursor.fetchone()
    conn.close()
    return render_template('admin/edit_chapter.html', chapter=chapter)

@admin_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_dashboard'))  

    cursor.execute("SELECT * FROM QUIZES WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    conn.close()
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':  
        subject_name = request.form['subject_name']
        cursor.execute('''
            UPDATE SUBJECTS SET subject_name = ? WHERE id = ?
        ''', (subject_name, subject_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin.admin_dashboard'))

    cursor.execute("SELECT id, subject_name FROM SUBJECTS WHERE id = ?", (subject_id,))
    subject = cursor.fetchone()
    conn.close()

    return render_template('admin/edit_subject.html', subject=subject)

@admin_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

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
        return redirect(url_for('admin.view_quiz'))

    cursor.execute("SELECT * FROM QUESTIONS WHERE id = ?", (question_id,))
    question = cursor.fetchone()
    conn.close()

    return render_template('admin/edit_question.html', question=question)

@admin_bp.route('/admin_summary')
def admin_summary():
    print("Session Data:", session)  

    if session.get('admin') is not True:
        return redirect(url_for('login'))  

    conn = get_db_connection()
    cursor = conn.cursor()

  
    cursor.execute('''
        SELECT SUBJECTS.subject_name, COUNT(DISTINCT SCORES.user_id) 
        FROM SCORES
        JOIN QUIZES ON SCORES.quiz_id = QUIZES.id
        JOIN CHAPTERS ON QUIZES.chapter_id = CHAPTERS.id
        JOIN SUBJECTS ON CHAPTERS.subject_id = SUBJECTS.id
        GROUP BY SUBJECTS.subject_name
    ''')
    subject_attempts = cursor.fetchall()

 
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
        'admin/admin_summary.html',
        subject_attempts=subject_attempts,
        subject_top_scores=subject_top_scores
    )




