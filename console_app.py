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