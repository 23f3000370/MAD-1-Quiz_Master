import sqlite3

DB_PATH = "quiz_master.db"  # ✅ Change this if needed

def get_db_connection():
    """Returns a database connection with foreign keys enabled."""
    try:
        conn = sqlite3.connect(DB_PATH) 
        conn.execute("PRAGMA foreign_keys = ON;")  # ✅ Ensures foreign keys are enforced
        return conn
    except sqlite3.Error as e:
        print(f"❌ Database connection failed: {e}")
        return None  # Prevents returning a broken connection


def initialize_database():
    """Creates necessary tables if they don't exist."""
    conn = get_db_connection()
    if conn is None:
        print("❌ Cannot initialize database, connection failed!")
        return

    cursor = conn.cursor()

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
    duration INTEGER NOT NULL,
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
    cursor.execute("INSERT OR IGNORE INTO ADMIN (id, username, password) VALUES (1, 'ayush2004@gmail.com', '23f3000370')")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SCORES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        total_scored INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- ✅ Automatically stores quiz attempt time
        FOREIGN KEY (quiz_id) REFERENCES QUIZES(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES USERS(id) ON DELETE CASCADE
    )''')


    


    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
