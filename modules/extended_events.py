"""
Extended Events Module - Monitor slow queries and failed logins
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_extended_events_menu(db):
    """Display Extended Events submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("EXTENDED EVENTS - Performance & Security Monitoring")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View Active Extended Event Sessions")
        print("2. View Slow Queries (> 1 second)")
        print("3. View Failed Login Attempts")
        print("4. View Session Statistics")
        print("5. Create Extended Event Session for Monitoring")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_active_sessions(db)
        elif choice == '2':
            view_slow_queries(db)
        elif choice == '3':
            view_failed_login_events(db)
        elif choice == '4':
            view_session_statistics(db)
        elif choice == '5':
            create_monitoring_session(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_active_sessions(db):
    """View all active Extended Event sessions"""
    query = """
    SELECT 
        ses.name AS SessionName,
        CASE 
            WHEN dxs.name IS NOT NULL 
            THEN 'RUNNING' 
            ELSE 'STOPPED' 
        END AS Status,
        ses.max_memory AS MaxMemoryKB,
        ses.event_retention_mode_desc AS RetentionMode,
        COUNT(DISTINCT sese.name) AS EventCount
    FROM sys.server_event_sessions ses
    LEFT JOIN sys.dm_xe_sessions dxs ON ses.name = dxs.name
    LEFT JOIN sys.server_event_session_events sese ON ses.event_session_id = sese.event_session_id
    GROUP BY ses.name, dxs.name, ses.max_memory, ses.event_retention_mode_desc
    ORDER BY ses.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Extended Event Sessions")


def view_slow_queries(db):
    """View queries that took longer than 2 seconds from Atelier_LongQueries XE session"""
    print(f"\n{Fore.CYAN}Reading slow queries from Extended Events (Atelier_LongQueries)...{Style.RESET_ALL}\n")
    
    query = """
    WITH EventData AS
    (
        SELECT CAST(event_data AS XML) AS EventXML
        FROM sys.fn_xe_file_target_read_file(
            'C:\\CP\\Audit\\Atelier\\Atelier_LongQueries*.xel', 
            NULL, NULL, NULL
        )
    )
    SELECT TOP 30
        EventXML.value('(event/@timestamp)[1]', 'DATETIME2') AS EventTime,
        EventXML.value('(event/action[@name="username"]/value)[1]', 'NVARCHAR(128)') AS Username,
        EventXML.value('(event/action[@name="database_name"]/value)[1]', 'NVARCHAR(128)') AS DatabaseName,
        CAST(EventXML.value('(event/data[@name="duration"]/value)[1]', 'BIGINT') / 1000000.0 AS DECIMAL(10,2)) AS DurationSeconds,
        CAST(EventXML.value('(event/data[@name="cpu_time"]/value)[1]', 'BIGINT') / 1000.0 AS DECIMAL(10,2)) AS CpuTimeMS,
        EventXML.value('(event/data[@name="logical_reads"]/value)[1]', 'BIGINT') AS LogicalReads,
        EventXML.value('(event/action[@name="client_app_name"]/value)[1]', 'NVARCHAR(128)') AS Application
    FROM EventData
    ORDER BY EventTime DESC
    """
    try:
        columns, results = db.execute_query(query)
        if results:
            db.display_results(columns, results, "Slow Queries (>= 2 seconds) from Atelier_LongQueries")
        else:
            print(f"{Fore.YELLOW}No slow queries recorded yet.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Extended Event session 'Atelier_LongQueries' is monitoring queries >= 2 seconds.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not read Extended Event files: {e}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Session may be newly created or files not generated yet.{Style.RESET_ALL}")


def view_failed_login_events(db):
    """View failed login attempts from Atelier_FailedLogins XE session"""
    print(f"\n{Fore.CYAN}Reading failed logins from Extended Events (Atelier_FailedLogins)...{Style.RESET_ALL}\n")
    
    query = """
    WITH FailedLogins AS
    (
        SELECT CAST(event_data AS XML) AS EventXML
        FROM sys.fn_xe_file_target_read_file(
            'C:\\CP\\Audit\\Atelier\\Atelier_FailedLogins*.xel', 
            NULL, NULL, NULL
        )
    )
    SELECT TOP 50
        EventXML.value('(event/@timestamp)[1]', 'DATETIME2') AS EventTime,
        EventXML.value('(event/action[@name="server_principal_name"]/value)[1]', 'NVARCHAR(128)') AS LoginName,
        EventXML.value('(event/action[@name="client_hostname"]/value)[1]', 'NVARCHAR(128)') AS ClientHost,
        EventXML.value('(event/action[@name="client_app_name"]/value)[1]', 'NVARCHAR(128)') AS Application,
        EventXML.value('(event/data[@name="error_number"]/value)[1]', 'INT') AS ErrorNumber,
        EventXML.value('(event/data[@name="message"]/value)[1]', 'NVARCHAR(MAX)') AS ErrorMessage
    FROM FailedLogins
    ORDER BY EventTime DESC
    """
    try:
        columns, results = db.execute_query(query)
        if results:
            db.display_results(columns, results, "Failed Login Attempts from Atelier_FailedLogins")
        else:
            print(f"{Fore.YELLOW}No failed login attempts recorded yet.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Extended Event session 'Atelier_FailedLogins' is monitoring failed logins.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not read Extended Event files: {e}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Session may be newly created or no failed logins occurred yet.{Style.RESET_ALL}")


def view_session_statistics(db):
    """View statistics about Extended Event sessions"""
    query = """
    SELECT 
        s.name AS SessionName,
        COUNT(se.name) AS EventCount,
        STRING_AGG(se.name, ', ') AS Events
    FROM sys.server_event_sessions s
    JOIN sys.server_event_session_events se ON s.event_session_id = se.event_session_id
    GROUP BY s.name
    ORDER BY s.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Extended Event Session Statistics")


def create_monitoring_session(db):
    """Create a new Extended Event session for monitoring"""
    print(f"\n{Fore.CYAN}Creating Extended Event Session for Monitoring...{Style.RESET_ALL}\n")
    
    # Check if session already exists
    check_query = """
    SELECT name FROM sys.server_event_sessions 
    WHERE name = 'AtelierMonitoring'
    """
    columns, results = db.execute_query(check_query)
    
    if results:
        print(f"{Fore.YELLOW}Session 'AtelierMonitoring' already exists.{Style.RESET_ALL}")
        drop_choice = input("Do you want to drop and recreate it? (y/n): ")
        if drop_choice.lower() == 'y':
            drop_query = """
            IF EXISTS (SELECT * FROM sys.server_event_sessions WHERE name = 'AtelierMonitoring')
            BEGIN
                DROP EVENT SESSION AtelierMonitoring ON SERVER;
            END
            """
            db.execute_query(drop_query, fetch=False, autocommit=True)
            print(f"{Fore.GREEN}Existing session dropped.{Style.RESET_ALL}")
        else:
            return
    
    # Create new session
    create_query = """
    CREATE EVENT SESSION [AtelierMonitoring] ON SERVER 
    ADD EVENT sqlserver.sql_batch_completed(
        ACTION(sqlserver.client_app_name, sqlserver.database_name, sqlserver.username)
        WHERE duration > 1000000  -- Queries longer than 1 second
    ),
    ADD EVENT sqlserver.error_reported(
        ACTION(sqlserver.client_app_name, sqlserver.client_hostname, sqlserver.server_principal_name)
        WHERE error_number = 18456  -- Failed login attempts
    ),
    ADD EVENT sqlserver.blocked_process_report(
        ACTION(sqlserver.client_app_name, sqlserver.database_name, sqlserver.username)
    )
    ADD TARGET package0.event_file(
        SET filename=N'C:\\CP\\Audit\\Atelier\\AtelierMonitoring.xel',
        max_file_size=(50),
        max_rollover_files=(5)
    )
    WITH (
        MAX_MEMORY=4096 KB,
        EVENT_RETENTION_MODE=ALLOW_SINGLE_EVENT_LOSS,
        MAX_DISPATCH_LATENCY=30 SECONDS,
        MAX_EVENT_SIZE=0 KB,
        MEMORY_PARTITION_MODE=NONE,
        TRACK_CAUSALITY=ON,
        STARTUP_STATE=ON
    );
    """
    
    try:
        db.execute_query(create_query, fetch=False, autocommit=True)
        print(f"{Fore.GREEN}✓ Extended Event session 'AtelierMonitoring' created successfully!{Style.RESET_ALL}")
        
        # Start the session
        start_query = "ALTER EVENT SESSION [AtelierMonitoring] ON SERVER STATE = START;"
        db.execute_query(start_query, fetch=False, autocommit=True)
        print(f"{Fore.GREEN}✓ Session started successfully!{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Session Configuration:{Style.RESET_ALL}")
        print("• Captures queries longer than 1 second")
        print("• Captures failed login attempts")
        print("• Captures blocked processes")
        print("• Output: C:\\CP\\Audit\\Atelier\\AtelierMonitoring.xel")
        
    except Exception as e:
        print(f"{Fore.RED}Error creating Extended Event session: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Note: This operation requires ALTER ANY EVENT SESSION permission.{Style.RESET_ALL}")
