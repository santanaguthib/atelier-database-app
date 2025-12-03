"""
Audit Module - View security audit events
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_audit_menu(db):
    """Display audit submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("AUDIT - Security Events Monitoring")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View Server Audit Status")
        print("2. View Audit Specifications")
        print("3. View Audit Logs (Recent Events)")
        print("4. View Failed Login Attempts")
        print("5. View Schema Changes")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_server_audit_status(db)
        elif choice == '2':
            view_audit_specifications(db)
        elif choice == '3':
            view_audit_logs(db)
        elif choice == '4':
            view_failed_logins(db)
        elif choice == '5':
            view_schema_changes(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_server_audit_status(db):
    """View server audit configuration and status"""
    query = """
    SELECT 
        audit_id,
        name AS AuditName,
        type_desc AS AuditType,
        is_state_enabled AS IsEnabled,
        queue_delay AS QueueDelay,
        create_date AS CreatedDate,
        modify_date AS ModifiedDate
    FROM sys.server_audits
    ORDER BY name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Server Audit Status")


def view_audit_specifications(db):
    """View database audit specifications"""
    query = """
    SELECT 
        das.name AS SpecificationName,
        das.is_state_enabled AS IsEnabled,
        sa.name AS AuditName,
        das.create_date AS CreatedDate,
        das.modify_date AS ModifiedDate
    FROM sys.database_audit_specifications das
    LEFT JOIN sys.server_audits sa ON das.audit_guid = sa.audit_guid
    ORDER BY das.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Database Audit Specifications")


def view_audit_logs(db):
    """View recent audit log entries"""
    print(f"\n{Fore.CYAN}Checking for audit log files...{Style.RESET_ALL}\n")
    
    # Check if audit is enabled
    check_query = """
    SELECT 
        sa.name AS AuditName,
        sa.is_state_enabled AS IsEnabled,
        sa.type_desc AS AuditType
    FROM sys.server_audits sa
    WHERE sa.is_state_enabled = 1
    """
    
    columns, audits = db.execute_query(check_query)
    
    if not audits:
        print(f"{Fore.YELLOW}Server Audit is not configured or not enabled.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}To enable audit, execute the audit creation scripts from your DB scripts.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Files will be created in: C:\\CP\\Audit\\Atelier\\{Style.RESET_ALL}\n")
        
        # Show alternative information
        print(f"{Fore.CYAN}Alternative: Recent database activities{Style.RESET_ALL}\n")
        alt_query = """
        SELECT TOP 20
            session_id AS SessionID,
            login_name AS LoginName,
            host_name AS HostName,
            program_name AS ProgramName,
            login_time AS LoginTime,
            status AS Status
        FROM sys.dm_exec_sessions
        WHERE is_user_process = 1
        ORDER BY login_time DESC
        """
        columns2, results2 = db.execute_query(alt_query)
        if results2:
            db.display_results(columns2, results2, "Recent User Sessions")
        return
    
    # Try to read audit files
    query = """
    SELECT TOP 50
        event_time AS EventTime,
        action_id AS ActionID,
        succeeded AS Succeeded,
        session_server_principal_name AS UserName,
        database_name AS DatabaseName,
        schema_name AS SchemaName,
        object_name AS ObjectName,
        statement AS Statement
    FROM sys.fn_get_audit_file('C:\\CP\\Audit\\Atelier\\*.sqlaudit', DEFAULT, DEFAULT)
    ORDER BY event_time DESC
    """
    try:
        columns, results = db.execute_query(query)
        if results:
            db.display_results(columns, results, "Recent Audit Events (Last 50)")
        else:
            print(f"{Fore.YELLOW}No audit events found. Audit may be newly created.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not read audit files. They may not exist yet.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Audit files location: C:\\CP\\Audit\\Atelier\\*.sqlaudit{Style.RESET_ALL}")


def view_failed_logins(db):
    """View failed login attempts from error log"""
    query = """
    EXEC xp_readerrorlog 0, 1, N'Login failed'
    """
    try:
        columns, results = db.execute_query(query)
        if columns and results:
            # Take only first 20 failed login attempts
            limited_results = results[:20] if len(results) > 20 else results
            db.display_results(columns, limited_results, "Failed Login Attempts (Last 20)")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not read error log. Admin privileges may be required.{Style.RESET_ALL}")


def view_schema_changes(db):
    """View schema modification events"""
    print(f"\n{Fore.CYAN}Checking for schema changes from audit logs...{Style.RESET_ALL}\n")
    
    # First, check if audit is configured
    check_query = """
    SELECT 
        name AS AuditName,
        is_state_enabled AS IsEnabled
    FROM sys.server_audits
    WHERE is_state_enabled = 1
    """
    
    columns, audits = db.execute_query(check_query)
    
    if not audits:
        print(f"{Fore.YELLOW}Server Audit is not configured or not enabled.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Alternative: Viewing schema changes from system catalog{Style.RESET_ALL}\n")
        
        # Show recent object modifications from system tables
        alt_query = """
        SELECT TOP 30
            OBJECT_NAME(object_id) AS ObjectName,
            type_desc AS ObjectType,
            create_date AS CreatedDate,
            modify_date AS ModifiedDate,
            CASE 
                WHEN DATEDIFF(DAY, modify_date, GETDATE()) = 0 THEN 'Today'
                WHEN DATEDIFF(DAY, modify_date, GETDATE()) = 1 THEN 'Yesterday'
                ELSE CAST(DATEDIFF(DAY, modify_date, GETDATE()) AS VARCHAR) + ' days ago'
            END AS ModifiedWhen
        FROM sys.objects
        WHERE type IN ('U', 'P', 'V', 'TR', 'FN', 'IF', 'TF')
            AND is_ms_shipped = 0
        ORDER BY modify_date DESC
        """
        columns2, results2 = db.execute_query(alt_query)
        if results2:
            db.display_results(columns2, results2, "Recent Object Modifications (from system catalog)")
        return
    
    # Try to read audit files
    query = """
    SELECT TOP 30
        event_time AS EventTime,
        session_server_principal_name AS UserName,
        database_name AS DatabaseName,
        object_name AS ObjectName,
        statement AS Statement
    FROM sys.fn_get_audit_file('C:\\CP\\Audit\\Atelier\\*.sqlaudit', DEFAULT, DEFAULT)
    WHERE action_id IN ('ALCR', 'ALDR', 'ALUP', 'CRCR', 'CRDR', 'CROP')
    ORDER BY event_time DESC
    """
    try:
        columns, results = db.execute_query(query)
        if results:
            db.display_results(columns, results, "Recent Schema Changes (from Audit)")
        else:
            print(f"{Fore.YELLOW}No schema change events found in audit logs.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not read audit files. Files may not exist yet.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Note: Audit files are created in C:\\CP\\Audit\\Atelier\\ when audit is active{Style.RESET_ALL}")
