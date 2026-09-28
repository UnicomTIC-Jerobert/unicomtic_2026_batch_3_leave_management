This is an **excellent architectural observation!** You have just identified one of the most common pitfalls in software design: **State Overwriting vs. Event Tracking (Audit Trails)**. 

In enterprise systems, we rarely `UPDATE` statuses because we lose the history (who did it, when, and what the previous state was). Instead, we `INSERT` records into a tracking table. 

Let's normalize the database by introducing a **`leave_history`** table.
*   **`leaves`**: Stores the core request (who, start, end).
*   **`leave_history`**: Stores the timeline of actions (Applied, Approved, Rejected), who did it, and the timestamp.

Here is how we implement this tracking system using procedural programming, including a **custom HTML/CSS Timeline** in Streamlit!

---

### Step 1: Updated Database Logic (`database.py`)
We will change our schema and queries. Notice how `add_leave` now does *two* inserts (one for the leave, one for the initial "Applied" history).

```python
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
```

---

### Step 2: Updated Console App (`console_app.py`)
Now we can view the timeline directly in the terminal.

```python
import database

def main():
    database.init_db()
    
    while True:
        print("\n--- Leave Tracking System ---")
        print("1. Add Employee")
        print("2. Apply for Leave")
        print("3. View All Leaves")
        print("4. Approve/Reject Leave (Add Tracker Event)")
        print("5. View Leave Timeline")
        print("6. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            name = input("Enter Name: ")
            dept = input("Enter Department: ")
            database.add_employee(name, dept)
            
        elif choice == '2':
            emp_id = input("Enter Employee ID: ")
            emp_name = input("Enter Employee Name (for tracker): ")
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            database.add_leave(emp_id, start, end, emp_name)
            print("Leave applied and tracked!")
            
        elif choice == '3':
            leaves = database.get_all_leaves_with_current_status()
            for l in leaves:
                print(f"Leave ID: {l[0]} | {l[1]} ({l[2]}) | {l[3]} to {l[4]} | CURRENT STATUS: {l[5]}")
                
        elif choice == '4':
            leave_id = input("Enter Leave ID: ")
            action = input("Enter action (Approved/Rejected/Need Info): ")
            action_by = input("Who is doing this action? (e.g., Manager Bob): ")
            database.process_leave_action(leave_id, action, action_by)
            print("Action tracked successfully!")
            
        elif choice == '5':
            leave_id = input("Enter Leave ID to track: ")
            timeline = database.get_leave_timeline(leave_id)
            print("\n--- ⏳ LEAVE TIMELINE ---")
            for event in timeline:
                print(f"[{event[2]}] {event[0]} by {event[1]}")
                
        elif choice == '6':
            break

if __name__ == "__main__":
    main()
```

---

### Step 3: Streamlit UI with Timeline Visual (`streamlit_app.py`)
We will use custom HTML/CSS injected into Streamlit to recreate the vertical timeline component you asked about!

*(If you get errors about the database, delete your old `leave_management.db` file so it can recreate the new schema).*

```python
import streamlit as st
import pandas as pd
import database

database.init_db()

st.set_page_config(page_title="Leave Tracker", layout="wide")
st.title("🏖️ Leave Management & Tracking System")

tab1, tab2, tab3 = st.tabs(["Employees", "Apply Leave", "Leave Tracking Dashboard"])

with tab1:
    with st.form("emp_form"):
        name = st.text_input("Employee Name")
        dept = st.selectbox("Department", ["HR", "Engineering", "Sales", "Marketing"])
        if st.form_submit_button("Add Employee") and name:
            database.add_employee(name, dept)
            st.success(f"Added {name}!")

with tab2:
    employees = database.get_all_employees()
    if employees:
        with st.form("leave_form"):
            emp_dict = {f"{emp[1]} ({emp[2]})": (emp[0], emp[1]) for emp in employees}
            selected_emp = st.selectbox("Select Employee", list(emp_dict.keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if st.form_submit_button("Submit Leave Request"):
                emp_id, emp_name = emp_dict[selected_emp]
                database.add_leave(emp_id, str(start_date), str(end_date), emp_name)
                st.success("Leave request submitted and tracked!")

with tab3:
    st.header("Leave Dashboard")
    leaves = database.get_all_leaves_with_current_status()
    
    if leaves:
        df_leaves = pd.DataFrame(leaves, columns=["Leave ID", "Name", "Department", "Start", "End", "Current Status"])
        st.dataframe(df_leaves, hide_index=True)
        
        st.divider()
        
        col1, col2 = st.columns([1, 1])
        
        # LEFT COLUMN: Take Action
        with col1:
            st.subheader("Process a Leave")
            leave_id_to_update = st.number_input("Leave ID", min_value=1, step=1)
            action = st.selectbox("Action", ["Approved", "Rejected", "Need More Info"])
            action_by = st.text_input("Supervisor Name (Action By)", "System Admin")
            if st.button("Submit Action"):
                database.process_leave_action(leave_id_to_update, action, action_by)
                st.success("Action recorded!")
                st.rerun()

        # RIGHT COLUMN: The Timeline Component
        with col2:
            st.subheader("⏳ Leave Timeline")
            view_id = st.number_input("Enter Leave ID to view timeline", min_value=1, step=1)
            
            if st.button("Show Timeline"):
                timeline_data = database.get_leave_timeline(view_id)
                
                if not timeline_data:
                    st.warning("No tracking history found for this Leave ID.")
                else:
                    # CUSTOM CSS FOR VERTICAL TIMELINE
                    timeline_html = """
                    <style>
                    .timeline { border-left: 3px solid #ff4b4b; padding-left: 20px; margin-left: 10px; font-family: sans-serif;}
                    .timeline-item { margin-bottom: 25px; position: relative; }
                    .timeline-item::before { 
                        content: ''; position: absolute; left: -28px; top: 5px; 
                        width: 14px; height: 14px; background: white; 
                        border: 3px solid #ff4b4b; border-radius: 50%; 
                    }
                    .t-time { font-size: 0.85em; color: #888; margin-bottom: 3px;}
                    .t-action { font-size: 1.1em; font-weight: bold; color: #fff;}
                    .t-user { font-size: 0.9em; color: #ccc; }
                    </style>
                    <div class="timeline">
                    """
                    
                    for event in timeline_data:
                        action, action_by, timestamp = event
                        
                        # Color coding based on action
                        color = "#4CAF50" if action == "Approved" else "#F44336" if action == "Rejected" else "#2196F3" if action == "Applied" else "#FF9800"
                        
                        timeline_html += f"""
                        <div class="timeline-item">
                            <div class="t-time">{timestamp}</div>
                            <div class="t-action" style="color: {color};">{action}</div>
                            <div class="t-user">by {action_by}</div>
                        </div>
                        """
                    timeline_html += "</div>"
                    
                    # Render the HTML in Streamlit
                    st.markdown(timeline_html, unsafe_allow_html=True)
```

### Why this is a massive step forward:
1. **Event Sourcing**: Instead of mutating data (`UPDATE`), we are appending data (`INSERT`). This is how banks handle transactions and how modern logistics track shipments.
2. **Subqueries (`get_all_leaves_with_current_status`)**: Look at the SQL query in `database.py`. We are dynamically calculating the "Current Status" by finding the most recent record in the history table. This is much safer than maintaining a separate status column!
3. **UI/UX Component**: You successfully implemented a Vertical Timeline using HTML/CSS inside Python.

### Ready for the next leap?
Currently, our `database.py` has 6 separate functions. Every time we want to deal with an Employee, we have to call a standalone function. What if we could group data and behavior together? 

**"I want to do `employee = Employee("John", "HR")` and `employee.save()`!"**

When you have tested the timeline and are ready, let me know, and we will move to **Phase 2: Object-Oriented Programming (OOP) and Classes!**