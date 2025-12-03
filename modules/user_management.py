"""
User Management Module - Registration and User Administration
"""

from colorama import Fore, Style
from datetime import datetime


def show_user_management_menu(db, current_user, is_admin):
    """Main menu for user management"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}USER MANAGEMENT - Registration & Administration{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        if is_admin:
            print("1. View Pending Registration Requests")
            print("2. Approve Registration Request")
            print("3. Reject Registration Request")
            print("4. View All Users")
            print("5. Disable User Account")
            print("6. Enable User Account")
            print("7. Delete User Account")
            print("8. View User Activity Log")
        else:
            print(f"{Fore.YELLOW}Admin privileges required for user management{Style.RESET_ALL}")
            print("1. View My Account Information")
        
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}").strip()
        
        if choice == '0':
            break
        elif is_admin:
            if choice == '1':
                view_pending_requests(db)
            elif choice == '2':
                approve_registration(db)
            elif choice == '3':
                reject_registration(db)
            elif choice == '4':
                view_all_users(db)
            elif choice == '5':
                disable_user(db)
            elif choice == '6':
                enable_user(db)
            elif choice == '7':
                delete_user(db)
            elif choice == '8':
                view_user_activity(db)
        else:
            if choice == '1':
                view_my_account(db, current_user)


def view_pending_requests(db):
    """View all pending registration requests"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Pending Registration Requests{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    query = """
    SELECT 
        RequestID,
        Username,
        FullName,
        Email,
        RequestedRole,
        RequestDate,
        Justification
    FROM UserRegistrationRequests
    WHERE Status = 'Pending'
    ORDER BY RequestDate ASC
    """
    
    columns, results = db.execute_query(query)
    
    if results:
        db.display_results(columns, results, "Pending Requests")
        print(f"\n{Fore.GREEN}Total pending requests: {len(results)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No pending registration requests.{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")


def approve_registration(db):
    """Approve a registration request and create SQL login + user"""
    print(f"\n{Fore.CYAN}Approve Registration Request{Style.RESET_ALL}\n")
    
    # Show pending requests
    query_requests = """
    SELECT 
        RequestID,
        Username,
        FullName,
        RequestedRole,
        Email
    FROM UserRegistrationRequests
    WHERE Status = 'Pending'
    ORDER BY RequestDate ASC
    """
    
    columns, results = db.execute_query(query_requests)
    
    if not results:
        print(f"{Fore.YELLOW}No pending requests to approve.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    db.display_results(columns, results, "Pending Requests")
    
    request_id = input(f"\n{Fore.CYAN}Enter RequestID to approve (0 to cancel): {Style.RESET_ALL}").strip()
    
    if request_id == '0':
        return
    
    # Get request details
    query_details = f"""
    SELECT Username, HashedPassword, RequestedRole, Email, FullName
    FROM UserRegistrationRequests
    WHERE RequestID = {request_id} AND Status = 'Pending'
    """
    
    cols, req_data = db.execute_query(query_details)
    
    if not req_data:
        print(f"{Fore.RED}Invalid RequestID or request already processed.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    username, hashed_pwd, role, email, fullname = req_data[0]
    
    print(f"\n{Fore.CYAN}Request Details:{Style.RESET_ALL}")
    print(f"Username: {username}")
    print(f"Full Name: {fullname}")
    print(f"Email: {email}")
    print(f"Requested Role: {role}")
    
    confirm = input(f"\n{Fore.YELLOW}Approve this request? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        print(f"{Fore.YELLOW}Approval cancelled.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    # Create SQL Server Login
    create_login_sql = f"""
    USE [master];
    IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = '{username}')
    BEGIN
        CREATE LOGIN [{username}] WITH PASSWORD = N'{hashed_pwd}', 
        DEFAULT_DATABASE=[Atelier], 
        CHECK_EXPIRATION=OFF, 
        CHECK_POLICY=OFF;
    END
    """
    
    # Mapping of user roles to database roles
    role_mapping = {
        'manager': 'AtelierManager',
        'tailor_user': 'AtelierTailor',
        'cashier': 'AtelierCashier'
    }
    
    db_role = role_mapping.get(role, 'AtelierTailor')  # Default to Tailor if unknown
    
    create_user_sql = f"""
    USE [Atelier];
    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '{username}')
    BEGIN
        CREATE USER [{username}] FOR LOGIN [{username}] WITH DEFAULT_SCHEMA=[dbo];
    END
    """
    
    # Execute SQL commands using separate connection for DDL operations
    print(f"\n{Fore.CYAN}Creating SQL Server login...{Style.RESET_ALL}")
    try:
        # Create new connection for DDL operations
        import pyodbc
        ddl_conn = pyodbc.connect(db.connection_string, autocommit=True)
        ddl_cursor = ddl_conn.cursor()
        
        # Create login
        ddl_cursor.execute(create_login_sql)
        print(f"{Fore.GREEN}✓ Login created{Style.RESET_ALL}")
        
        # Create user
        print(f"{Fore.CYAN}Creating database user...{Style.RESET_ALL}")
        ddl_cursor.execute(create_user_sql)
        print(f"{Fore.GREEN}✓ User created{Style.RESET_ALL}")
        
        # Assign to role
        print(f"{Fore.CYAN}Adding user to role [{db_role}]...{Style.RESET_ALL}")
        assign_role_sql = f"USE [Atelier]; ALTER ROLE [{db_role}] ADD MEMBER [{username}]"
        ddl_cursor.execute(assign_role_sql)
        print(f"{Fore.GREEN}✓ User added to role{Style.RESET_ALL}")
        
        ddl_cursor.close()
        ddl_conn.close()
        
    except Exception as e:
        print(f"{Fore.RED}Error creating user: {e}{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    # Update request status
    update_status = f"""
    UPDATE UserRegistrationRequests
    SET Status = 'Approved',
        ProcessedDate = GETDATE(),
        ProcessedBy = CURRENT_USER
    WHERE RequestID = {request_id}
    """
    
    db.execute_query(update_status, fetch=False, autocommit=True)
    
    print(f"\n{Fore.GREEN}✓ Registration approved successfully!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ SQL Server login created: {username}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Database user created and added to role: {db_role}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  User now has all permissions defined for {role} role{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")


def reject_registration(db):
    """Reject a registration request"""
    print(f"\n{Fore.CYAN}Reject Registration Request{Style.RESET_ALL}\n")
    
    # Show pending requests
    query_requests = """
    SELECT 
        RequestID,
        Username,
        FullName,
        RequestedRole
    FROM UserRegistrationRequests
    WHERE Status = 'Pending'
    ORDER BY RequestDate ASC
    """
    
    columns, results = db.execute_query(query_requests)
    
    if not results:
        print(f"{Fore.YELLOW}No pending requests to reject.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    db.display_results(columns, results, "Pending Requests")
    
    request_id = input(f"\n{Fore.CYAN}Enter RequestID to reject (0 to cancel): {Style.RESET_ALL}").strip()
    
    if request_id == '0':
        return
    
    reason = input(f"{Fore.CYAN}Rejection reason: {Style.RESET_ALL}").strip()
    
    confirm = input(f"\n{Fore.YELLOW}Reject this request? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        return
    
    update_status = f"""
    UPDATE UserRegistrationRequests
    SET Status = 'Rejected',
        ProcessedDate = GETDATE(),
        ProcessedBy = CURRENT_USER,
        RejectionReason = '{reason}'
    WHERE RequestID = {request_id} AND Status = 'Pending'
    """
    
    db.execute_query(update_status, fetch=False, autocommit=True)
    
    print(f"\n{Fore.GREEN}✓ Request rejected.{Style.RESET_ALL}")
    input("\nPress Enter to continue...")


def view_all_users(db):
    """View all database users"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}All Database Users{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    query = """
    SELECT 
        dp.name AS Username,
        dp.type_desc AS UserType,
        dp.create_date AS CreatedDate,
        CASE WHEN sp.is_disabled = 1 THEN 'Disabled' 
             WHEN sp.name IS NULL THEN 'No Login'
             ELSE 'Active' END AS Status,
        STRING_AGG(r.name, ', ') AS DatabaseRoles
    FROM sys.database_principals dp
    LEFT JOIN sys.server_principals sp ON dp.name = sp.name
    LEFT JOIN sys.database_role_members drm ON dp.principal_id = drm.member_principal_id
    LEFT JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
    WHERE dp.type IN ('S', 'U')
        AND dp.name NOT IN ('dbo', 'guest', 'INFORMATION_SCHEMA', 'sys')
        AND dp.name NOT LIKE 'db_%'
        AND dp.name NOT LIKE '##%##'
    GROUP BY dp.name, dp.type_desc, dp.create_date, sp.is_disabled, sp.name
    ORDER BY dp.create_date DESC
    """
    
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Database Users")
    
    input("\nPress Enter to continue...")


def disable_user(db):
    """Disable a user account"""
    print(f"\n{Fore.CYAN}Disable User Account{Style.RESET_ALL}\n")
    
    username = input(f"{Fore.CYAN}Enter username to disable: {Style.RESET_ALL}").strip()
    
    if username.lower() in ['atelier_admin', 'sa', 'dbo']:
        print(f"{Fore.RED}Cannot disable system administrator account!{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    confirm = input(f"\n{Fore.YELLOW}Disable user '{username}'? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        return
    
    try:
        import pyodbc
        ddl_conn = pyodbc.connect(db.connection_string, autocommit=True)
        ddl_cursor = ddl_conn.cursor()
        
        disable_sql = f"USE [master]; ALTER LOGIN [{username}] DISABLE"
        ddl_cursor.execute(disable_sql)
        
        ddl_cursor.close()
        ddl_conn.close()
        
        print(f"\n{Fore.GREEN}✓ User '{username}' disabled.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error disabling user: {e}{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")


def enable_user(db):
    """Enable a user account"""
    print(f"\n{Fore.CYAN}Enable User Account{Style.RESET_ALL}\n")
    
    username = input(f"{Fore.CYAN}Enter username to enable: {Style.RESET_ALL}").strip()
    
    confirm = input(f"\n{Fore.YELLOW}Enable user '{username}'? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'yes':
        return
    
    try:
        import pyodbc
        ddl_conn = pyodbc.connect(db.connection_string, autocommit=True)
        ddl_cursor = ddl_conn.cursor()
        
        enable_sql = f"USE [master]; ALTER LOGIN [{username}] ENABLE"
        ddl_cursor.execute(enable_sql)
        
        ddl_cursor.close()
        ddl_conn.close()
        
        print(f"\n{Fore.GREEN}✓ User '{username}' enabled.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error enabling user: {e}{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")


def delete_user(db):
    """Delete a user account permanently"""
    print(f"\n{Fore.RED}Delete User Account (PERMANENT){Style.RESET_ALL}\n")
    
    username = input(f"{Fore.CYAN}Enter username to delete: {Style.RESET_ALL}").strip()
    
    if username.lower() in ['atelier_admin', 'sa', 'dbo', 'manager']:
        print(f"{Fore.RED}Cannot delete protected account!{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n{Fore.RED}WARNING: This will permanently delete the user and all associated data!{Style.RESET_ALL}")
    confirm = input(f"{Fore.YELLOW}Type 'DELETE {username}' to confirm: {Style.RESET_ALL}").strip()
    
    if confirm != f'DELETE {username}':
        print(f"{Fore.YELLOW}Deletion cancelled.{Style.RESET_ALL}")
        input("\nPress Enter to continue...")
        return
    
    # Drop user using separate connection for DDL operations
    try:
        import pyodbc
        ddl_conn = pyodbc.connect(db.connection_string, autocommit=True)
        ddl_cursor = ddl_conn.cursor()
        
        # Drop user from database first
        drop_user_sql = f"USE [Atelier]; IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '{username}') DROP USER [{username}]"
        ddl_cursor.execute(drop_user_sql)
        
        # Drop login from server
        drop_login_sql = f"USE [master]; IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = '{username}') DROP LOGIN [{username}]"
        ddl_cursor.execute(drop_login_sql)
        
        ddl_cursor.close()
        ddl_conn.close()
        
        print(f"\n{Fore.GREEN}✓ User '{username}' deleted permanently.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ SQL Login removed{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Database User removed{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Error deleting user: {e}{Style.RESET_ALL}")
    
    input("\nPress Enter to continue...")


def view_user_activity(db):
    """View user activity from audit logs"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}User Activity Log{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    query = """
    SELECT 
        UserName,
        COUNT(*) AS TotalActions,
        MIN(OperationDate) AS FirstAction,
        MAX(OperationDate) AS LastAction
    FROM OrderLogs
    GROUP BY UserName
    ORDER BY COUNT(*) DESC
    """
    
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "User Activity Summary")
    
    input("\nPress Enter to continue...")


def view_my_account(db, username):
    """View current user's account information"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}My Account Information{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}Username:{Style.RESET_ALL} {username}")
    print(f"{Fore.GREEN}Current Database:{Style.RESET_ALL} Atelier")
    
    # Get role information
    role_query = """
    SELECT 
        dp.name AS RoleName
    FROM sys.database_role_members drm
    JOIN sys.database_principals dp ON drm.role_principal_id = dp.principal_id
    WHERE drm.member_principal_id = USER_ID()
    """
    
    cols, roles = db.execute_query(role_query)
    
    if roles:
        print(f"\n{Fore.GREEN}Assigned Roles:{Style.RESET_ALL}")
        for role in roles:
            print(f"  • {role[0]}")
    
    input("\nPress Enter to continue...")


def register_new_user():
    """Registration form for new users (called before login)"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}USER REGISTRATION - Atelier Database{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Your registration request will be reviewed by an administrator.{Style.RESET_ALL}\n")
    
    # Collect registration data
    username = input(f"{Fore.CYAN}Username (login): {Style.RESET_ALL}").strip()
    if not username:
        print(f"{Fore.RED}Username cannot be empty!{Style.RESET_ALL}")
        return False
    
    password = input(f"{Fore.CYAN}Password: {Style.RESET_ALL}").strip()
    if len(password) < 8:
        print(f"{Fore.RED}Password must be at least 8 characters!{Style.RESET_ALL}")
        return False
    
    password_confirm = input(f"{Fore.CYAN}Confirm password: {Style.RESET_ALL}").strip()
    if password != password_confirm:
        print(f"{Fore.RED}Passwords do not match!{Style.RESET_ALL}")
        return False
    
    fullname = input(f"{Fore.CYAN}Full Name: {Style.RESET_ALL}").strip()
    email = input(f"{Fore.CYAN}Email: {Style.RESET_ALL}").strip()
    
    print(f"\n{Fore.CYAN}Select desired role:{Style.RESET_ALL}")
    print("1. Manager - Read/Write access to all data")
    print("2. Tailor - Work with orders and production")
    print("3. Cashier - Process payments")
    
    role_choice = input(f"\n{Fore.CYAN}Choice (1-3): {Style.RESET_ALL}").strip()
    
    role_map = {
        '1': 'manager',
        '2': 'tailor_user',
        '3': 'cashier'
    }
    
    if role_choice not in role_map:
        print(f"{Fore.RED}Invalid role selection!{Style.RESET_ALL}")
        return False
    
    role = role_map[role_choice]
    
    justification = input(f"\n{Fore.CYAN}Why do you need access? (brief justification): {Style.RESET_ALL}").strip()
    
    # Connect as guest or use application connection to insert request
    from database import DatabaseConnection
    from config import Config
    
    # Use manager account to insert registration request (it has write permissions)
    temp_db = DatabaseConnection('manager', 'Manager@2025!Pass', 'manager')
    
    if not temp_db.connect():
        print(f"{Fore.RED}Failed to submit registration request. Please try again later.{Style.RESET_ALL}")
        return False
    
    # Insert registration request
    insert_query = f"""
    INSERT INTO UserRegistrationRequests 
    (Username, HashedPassword, FullName, Email, RequestedRole, Justification, RequestDate, Status)
    VALUES 
    ('{username}', '{password}', '{fullname}', '{email}', '{role}', '{justification}', GETDATE(), 'Pending')
    """
    
    try:
        temp_db.execute_query(insert_query, fetch=False, autocommit=True)
        temp_db.disconnect()
        
        print(f"\n{Fore.GREEN}✓ Registration request submitted successfully!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ An administrator will review your request.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ You will be able to login once approved.{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}Error submitting request: {e}{Style.RESET_ALL}")
        return False
