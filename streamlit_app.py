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
            print(emp_dict)
            
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