import sqlite3
from datetime import datetime

DB_NAME = "leave_management.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, department TEXT NOT NULL
    )''')
    
    # The Leaves table no longer needs a 'status' column!
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )''')
    
    # NEW: Leave History Table for Tracking
    cursor.execute('''CREATE TABLE IF NOT EXISTS leave_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        leave_id INTEGER NOT NULL,
        action TEXT NOT NULL,       -- e.g., 'Applied', 'Approved', 'Rejected'
        action_by TEXT NOT NULL,    -- Name or Role of the person acting
        timestamp TEXT NOT NULL,    -- When it happened
        FOREIGN KEY(leave_id) REFERENCES leaves(id)
    )''')
    
    conn.commit()
    conn.close()

# --- CRUD & TRACKING OPERATIONS ---

def add_employee(name, department):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, department) VALUES (?, ?)", (name, department))
    conn.commit()
    conn.close()

def get_all_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

def add_leave(employee_id, start_date, end_date, employee_name):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Insert the main leave record
    cursor.execute("INSERT INTO leaves (employee_id, start_date, end_date) VALUES (?, ?, ?)", 
                   (employee_id, start_date, end_date))
    
    # Get the ID of the leave we just inserted
    leave_id = cursor.lastrowid 
    
    # 2. Insert the initial tracking event
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO leave_history (leave_id, action, action_by, timestamp) 
                      VALUES (?, ?, ?, ?)''', 
                   (leave_id, 'Applied', employee_name, timestamp))
    
    conn.commit()
    conn.close()

def process_leave_action(leave_id, action, action_by):
    """Replaces update_leave_status. We INSERT a new history record instead."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO leave_history (leave_id, action, action_by, timestamp) 
                      VALUES (?, ?, ?, ?)''', 
                   (leave_id, action, action_by, timestamp))
    conn.commit()
    conn.close()

def get_all_leaves_with_current_status():
    """Advanced JOIN: Get leave info AND the LATEST status from history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # We use a subquery to fetch the most recent status for each leave
    query = '''
        SELECT l.id, e.name, e.department, l.start_date, l.end_date,
               (SELECT action FROM leave_history lh WHERE lh.leave_id = l.id ORDER BY timestamp DESC LIMIT 1) as current_status
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
    '''
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records

def get_leave_timeline(leave_id):
    """Fetch the history/timeline for a specific leave."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT action, action_by, timestamp FROM leave_history WHERE leave_id = ? ORDER BY timestamp ASC", (leave_id,))
    history = cursor.fetchall()
    conn.close()
    return history