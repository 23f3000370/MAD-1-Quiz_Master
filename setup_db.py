import sqlite3

def initialize_database():
    conn = sqlite3.connect('quiz_master.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables if they do not exist
    cursor.execute(''' CREATE TABLE IF NOT EXISTS SUBJECTS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL
    )''')

    cursor.execute(''' CREATE TABLE IF NOT EXISTS CHAPTERS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_name TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    no_of_question INTEGER NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES SUBJECTS(id) on DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute(''' CREATE TABLE IF NOT EXISTS QUIZES(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT NOT NULL,
    chapter_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    duration TEXT NOT NULL,
    FOREIGN KEY(chapter_id) REFERENCES CHAPTERS(id) on DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute(''' CREATE TABLE IF NOT EXISTS QUESTIONS(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_title TEXT NOT NULL,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    answer TEXT NOT NULL,
    quiz_id INTEGER NOT NULL,
    FOREIGN KEY(quiz_id) REFERENCES QUIZES(id) on DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS USERS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        qualification TEXT,
        dob TEXT
    )''')

    
    cursor.execute('''CREATE TABLE IF NOT EXISTS ADMIN (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    cursor.execute("INSERT OR IGNORE INTO ADMIN (id, username, password) VALUES (1, 'ayush', '23f3000370')")

    cursor.execute('''CREATE TABLE IF NOT EXISTS SCORES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        total_scored INTEGER,
        FOREIGN KEY(quiz_id) REFERENCES QUIZES(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES USERS(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
