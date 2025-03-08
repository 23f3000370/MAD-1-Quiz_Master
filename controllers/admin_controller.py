from flask import Blueprint, render_template, request, redirect, url_for, session
from models.setup_db import get_db_connection

auth_bp = Blueprint('auth', __name__)

# Home Route
@auth_bp.route('/')
def home():
    return render_template('index.html')

# Signup Route
@auth_bp.route('/signup', methods=['GET', 'POST'])
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
        except:
            return "Username already exists!"
        finally:
            conn.close()
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM USERS WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('user.user_dashboard'))
        return "Invalid username or password"
    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
