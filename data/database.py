import sqlite3
import os
import datetime
import sys
from typing import List, Optional

try:
    from core.models import Task, Note
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.models import Task, Note


DATABASE_NAME = "nexus_task_ai.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', DATABASE_NAME)
INIT_FLAG_FILE = os.path.join(os.path.dirname(__file__), '.db_initialized')

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            priority TEXT DEFAULT 'Media',
            due_date DATE,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            task_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_task(description: str, priority: str = "Media", due_date: Optional[datetime.date] = None) -> Optional[Task]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tasks (description, priority, due_date, completed)
            VALUES (?, ?, ?, ?)
        ''', (description, priority, due_date, False))
        conn.commit()
        new_id = cursor.lastrowid
        if new_id is not None:
            return get_task_by_id(new_id)
        return None
    except sqlite3.Error as e:
        print(f"Error adding task: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_all_tasks() -> List[Task]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, description, priority, due_date, completed FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        tasks = [
            Task(id=row['id'], description=row['description'], priority=row['priority'],
                 due_date=row['due_date'], completed=bool(row['completed']))
            for row in rows
        ]
        return tasks
    except sqlite3.Error as e:
        print(f"Error fetching tasks: {e}")
        return []
    finally:
        conn.close()

def get_task_by_id(task_id: int) -> Optional[Task]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, description, priority, due_date, completed FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            task = Task(id=row['id'], description=row['description'], priority=row['priority'],
                        due_date=row['due_date'], completed=bool(row['completed']))
            return task
        return None
    except sqlite3.Error as e:
        print(f"Error fetching task {task_id}: {e}")
        return None
    finally:
        conn.close()

def update_task_completion(task_id: int, completed: bool) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating task completion for ID {task_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_task(task_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting task ID {task_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_note(content: str, task_id: Optional[int] = None) -> Optional[Note]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        current_time = datetime.datetime.now()
        cursor.execute('''
            INSERT INTO notes (content, task_id, created_at)
            VALUES (?, ?, ?)
        ''', (content, task_id, current_time))
        conn.commit()
        new_id = cursor.lastrowid
        if new_id is not None:
            return get_note_by_id(new_id)
        return None
    except sqlite3.Error as e:
        print(f"Error adding note: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_note_by_id(note_id: int) -> Optional[Note]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content, task_id, created_at FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            note = Note(id=row['id'], content=row['content'], task_id=row['task_id'], created_at=row['created_at'])
            return note
        return None
    except sqlite3.Error as e:
        print(f"Error fetching note {note_id}: {e}")
        return None
    finally:
        conn.close()

def get_all_notes() -> List[Note]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content, task_id, created_at FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        notes = [
            Note(id=row['id'], content=row['content'], task_id=row['task_id'], created_at=row['created_at'])
            for row in rows
        ]
        return notes
    except sqlite3.Error as e:
        print(f"Error fetching all notes: {e}")
        return []
    finally:
        conn.close()

def get_notes_for_task(task_id: int) -> List[Note]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content, task_id, created_at FROM notes WHERE task_id = ? ORDER BY created_at DESC", (task_id,))
        rows = cursor.fetchall()
        notes = [
            Note(id=row['id'], content=row['content'], task_id=row['task_id'], created_at=row['created_at'])
            for row in rows
        ]
        return notes
    except sqlite3.Error as e:
        print(f"Error fetching notes for task {task_id}: {e}")
        return []
    finally:
        conn.close()

def update_note(note_id: int, content: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (content, note_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating note ID {note_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_note(note_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting note ID {note_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if not os.path.exists(INIT_FLAG_FILE):
    initialize_database()
    try:
        with open(INIT_FLAG_FILE, 'w') as f:
            f.write(datetime.datetime.now().isoformat())
    except IOError as e:
        print(f"Warning: Could not create initialization flag file: {e}")