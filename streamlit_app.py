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