import sqlite3

DB = "tasks.db"

def init():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            done INTEGER DEFAULT 0, due_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add(task, due_at=None):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO tasks (task, due_at) VALUES (?, ?)", (task, due_at))
    conn.commit()
    conn.close()

def list_tasks():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, task, done FROM tasks ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows

def complete(task_id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def delete(task_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

init()
print("Task sistemi hazır.")
