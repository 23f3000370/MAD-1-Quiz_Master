from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.setup_db import get_db_connection

admin_bp = Blueprint('admin', __name__)

# ✅ Admin Dashboard Route
@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))  # ✅ Fixed route

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all subjects
    cursor.execute("SELECT * FROM SUBJECTS")
    subjects = cursor.fetchall()

    # Fetch all chapters with the number of questions
    cursor.execute("SELECT id, chapter_name, subject_id, no_of_question FROM CHAPTERS")
    chapters = cursor.fetchall()
    conn.close()

    # Organizing chapters under subjects
    subject_dict = {sub[0]: {"id": sub[0], "name": sub[1], "chapters": []} for sub in subjects}
    
    for chap in chapters:
        subject_id = chap[2]
        if subject_id in subject_dict:
            subject_dict[subject_id]["chapters"].append({
                "id": chap[0], 
                "name": chap[1], 
                "no_of_question": chap[3]
            })

    return render_template('admin_dashboard.html', subjects=subject_dict.values())

# ✅ Delete Subject Route
@admin_bp.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SUBJECTS WHERE id = ?", (subject_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin.admin_dashboard'))

# ✅ Add Subject Route
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

    return render_template('add_subject.html')

# ✅ Add Chapter Route
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

    return render_template('add_chapter.html')

# ✅ View Quiz Route
@admin_bp.route('/view_quiz')
def view_quiz():
    if 'admin' not in session:
        return redirect(url_for('auth.admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all quizzes
    cursor.execute("SELECT id, quiz_name FROM QUIZES")
    quizzes = cursor.fetchall()

    # Fetch all questions with quiz_id
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

    return render_template('view_quiz.html', quizes=quiz_dict.values())

# ✅ Search Admin Route
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

    return render_template('admin_search_results.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions)
