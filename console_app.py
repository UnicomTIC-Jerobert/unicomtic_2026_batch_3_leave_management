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
            print(employees)
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