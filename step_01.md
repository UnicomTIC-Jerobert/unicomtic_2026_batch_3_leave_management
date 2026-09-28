This is an **absolutely fantastic learning path**. Moving from Procedural $\rightarrow$ Object-Oriented (OOP) $\rightarrow$ Custom ORM is exactly how modern frameworks (like Django or SQLAlchemy) evolved. Experiencing the "pain points" of procedural code will make you truly appreciate and understand how an ORM works under the hood.

**Is it feasible?** Yes, 100%. Python and SQLite are the perfect tools for this because SQLite requires no external server setup, allowing you to focus entirely on the code architecture.

Let's dive into **Phase 1: Procedural Programming**. 

### The Project: Leave Management System
To practice **JOIN** queries, we need at least two tables with a relationship.
1. **`employees`** (id, name, department)
2. **`leaves`** (id, employee_id, start_date, end_date, status) - *Links to employees via `employee_id`*

---

### Step 1: The Procedural Core (`database.py`)
In procedural programming, we write functions that take inputs, interact with the database, and return outputs. Create a file named `database.py` and paste this code.

```python
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    
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
```

---

### Step 2: The Console UI (`console_app.py`)
Now let's use these procedural functions in a simple terminal application.

```python
import database

def main():
    database.init_db()
    
    while True:
        print("\n--- Leave Management System ---")
        print("1. Add Employee")
        print("2. View Employees")
        print("3. Apply for Leave")
        print("4. View All Leaves (JOIN Query)")
        print("5. Approve/Reject Leave")
        print("6. Exit")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            name = input("Enter Name: ")
            dept = input("Enter Department: ")
            database.add_employee(name, dept)
            print("Employee added!")
            
        elif choice == '2':
            employees = database.get_all_employees()
            for emp in employees:
                print(f"ID: {emp[0]}, Name: {emp[1]}, Dept: {emp[2]}")
                
        elif choice == '3':
            emp_id = input("Enter Employee ID: ")
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            database.add_leave(emp_id, start, end)
            print("Leave applied!")
            
        elif choice == '4':
            leaves = database.get_all_leaves_with_details()
            print("\n--- Leave Records ---")
            for l in leaves:
                # Unpacking the JOIN query results
                print(f"Leave ID: {l[0]} | Name: {l[1]} ({l[2]}) | {l[3]} to {l[4]} | Status: {l[5]}")
                
        elif choice == '5':
            leave_id = input("Enter Leave ID: ")
            status = input("Enter new status (Approved/Rejected): ")
            database.update_leave_status(leave_id, status)
            print("Status updated!")
            
        elif choice == '6':
            break

if __name__ == "__main__":
    main()
```

---

### Step 3: The Streamlit UI (`streamlit_app.py`)
Streamlit allows us to take the exact same procedural logic and put it on a web page. 
*(Make sure to install streamlit: `pip install streamlit pandas`)*

```python
import streamlit as st
import pandas as pd
import database

# Initialize DB when the app loads
database.init_db()

st.title("🏖️ Leave Management System")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Employees", "Apply Leave", "Leave Dashboard"])

with tab1:
    st.header("Add New Employee")
    with st.form("emp_form"):
        name = st.text_input("Employee Name")
        dept = st.selectbox("Department", ["HR", "Engineering", "Sales", "Marketing"])
        submit_emp = st.form_submit_button("Add Employee")
        
        if submit_emp and name:
            database.add_employee(name, dept)
            st.success(f"Added {name} to {dept}!")

    st.subheader("Employee List")
    employees = database.get_all_employees()
    if employees:
        # Convert to pandas dataframe for nice Streamlit rendering
        df_emp = pd.DataFrame(employees, columns=["ID", "Name", "Department"])
        st.dataframe(df_emp, hide_index=True)

with tab2:
    st.header("Apply for Leave")
    employees = database.get_all_employees()
    
    if not employees:
        st.warning("Please add an employee first.")
    else:
        with st.form("leave_form"):
            # Create a dictionary to map employee names to their IDs
            emp_dict = {f"{emp[1]} ({emp[2]})": emp[0] for emp in employees}
            
            selected_emp = st.selectbox("Select Employee", list(emp_dict.keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            submit_leave = st.form_submit_button("Submit Leave Request")
            
            if submit_leave:
                emp_id = emp_dict[selected_emp]
                database.add_leave(emp_id, str(start_date), str(end_date))
                st.success("Leave request submitted!")

with tab3:
    st.header("Leave Dashboard (JOIN Query)")
    
    leaves = database.get_all_leaves_with_details()
    if leaves:
        df_leaves = pd.DataFrame(leaves, columns=["Leave ID", "Name", "Department", "Start", "End", "Status"])
        st.dataframe(df_leaves, hide_index=True)
        
        st.subheader("Update Leave Status")
        col1, col2, col3 = st.columns(3)
        with col1:
            leave_id_to_update = st.number_input("Leave ID", min_value=1, step=1)
        with col2:
            new_status = st.selectbox("New Status", ["Approved", "Rejected", "Pending"])
        with col3:
            st.write("") # Spacing
            st.write("") # Spacing
            if st.button("Update"):
                database.update_leave_status(leave_id_to_update, new_status)
                st.success("Updated! Refreshing...")
                st.rerun() # Refresh the page to show updated data
    else:
        st.info("No leave records found.")
```

### How to Run This:
1. Save the 3 files in the same folder.
2. To test the console app: `python console_app.py`
3. To test the web app: `streamlit run streamlit_app.py`

### What to notice before we move to OOP:
Look closely at `database.py`. Notice how we have to write `conn = get_connection()` and `cursor = conn.cursor()` inside **every single function**? Notice how if we want to change the table name, we have to rewrite SQL everywhere? 

This repetition and hard-coding is the exact problem that **OOP** and eventually **ORMs** are designed to solve. 

Play around with this setup, add a few employees, apply for leaves, and see how the `JOIN` brings the data together. Let me know when you've tested this and are ready to refactor it into **Phase 2: Object-Oriented Programming (Classes & Objects)!**