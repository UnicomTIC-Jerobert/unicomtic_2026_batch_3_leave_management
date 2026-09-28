import sqlite3

DB_NAME = "leave_management.db"

def get_connection():
    """Helper function to get a database connection."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize the database with tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)
    
    # Create Leaves Table (with a Foreign Key)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- CRUD OPERATIONS ---


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

def add_leave(employee_id, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leaves (employee_id, start_date, end_date) VALUES (?, ?, ?)", 
                   (employee_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_all_leaves_with_details():
    """This is where we use a JOIN query to combine employee and leave data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # INNER JOIN to get employee name and department alongside their leave request
    query = '''
        SELECT leaves.id, employees.name, employees.department, 
               leaves.start_date, leaves.end_date, leaves.status
        FROM leaves
        JOIN employees ON leaves.employee_id = employees.id
    '''
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records
    
    

def update_leave_status(leave_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leaves SET status = ? WHERE id = ?", (new_status, leave_id))
    conn.commit()
    conn.close()