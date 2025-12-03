"""
Backup Module - View backup jobs and history
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_backup_menu(db):
    """Display backup management submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("BACKUP - Automated Backup Management")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View SQL Agent Jobs Status")
        print("2. View Backup History")
        print("3. View Last Backup Information")
        print("4. View Job Schedules")
        print("5. View Job Execution History")
        print("6. Manual Backup Execution")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_sql_agent_jobs(db)
        elif choice == '2':
            view_backup_history(db)
        elif choice == '3':
            view_last_backup_info(db)
        elif choice == '4':
            view_job_schedules(db)
        elif choice == '5':
            view_job_execution_history(db)
        elif choice == '6':
            manual_backup_execution(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_sql_agent_jobs(db):
    """View all SQL Server Agent jobs related to Atelier backups"""
    query = """
    SELECT 
        j.job_id,
        j.name AS JobName,
        j.enabled AS IsEnabled,
        j.description AS Description,
        CASE 
            WHEN ja.run_requested_date IS NOT NULL THEN 'Running'
            WHEN j.enabled = 1 THEN 'Enabled'
            ELSE 'Disabled'
        END AS Status,
        j.date_created AS CreatedDate,
        j.date_modified AS ModifiedDate
    FROM msdb.dbo.sysjobs j
    LEFT JOIN msdb.dbo.sysjobactivity ja ON j.job_id = ja.job_id
        AND ja.session_id = (SELECT MAX(session_id) FROM msdb.dbo.sysjobactivity)
    WHERE j.name LIKE '%Atelier%'
    ORDER BY j.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "SQL Server Agent Jobs - Atelier Backups")


def view_backup_history(db):
    """View backup history for Atelier database"""
    query = """
    SELECT TOP 30
        bs.database_name AS DatabaseName,
        CASE bs.type
            WHEN 'D' THEN 'Full Database'
            WHEN 'I' THEN 'Differential'
            WHEN 'L' THEN 'Transaction Log'
            WHEN 'F' THEN 'File/Filegroup'
        END AS BackupType,
        bs.backup_start_date AS StartTime,
        bs.backup_finish_date AS FinishTime,
        DATEDIFF(SECOND, bs.backup_start_date, bs.backup_finish_date) AS DurationSeconds,
        CAST(bs.backup_size / 1024.0 / 1024.0 AS DECIMAL(10,2)) AS BackupSizeMB,
        CAST(bs.compressed_backup_size / 1024.0 / 1024.0 AS DECIMAL(10,2)) AS CompressedSizeMB,
        bmf.physical_device_name AS BackupFile,
        bs.user_name AS ExecutedBy
    FROM msdb.dbo.backupset bs
    INNER JOIN msdb.dbo.backupmediafamily bmf ON bs.media_set_id = bmf.media_set_id
    WHERE bs.database_name = 'Atelier'
    ORDER BY bs.backup_start_date DESC
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Backup History (Last 30 backups)")


def view_last_backup_info(db):
    """View information about the last backup of each type"""
    query = """
    SELECT 
        database_name AS DatabaseName,
        MAX(CASE WHEN type = 'D' THEN backup_finish_date END) AS LastFullBackup,
        MAX(CASE WHEN type = 'I' THEN backup_finish_date END) AS LastDifferentialBackup,
        MAX(CASE WHEN type = 'L' THEN backup_finish_date END) AS LastLogBackup,
        DATEDIFF(HOUR, MAX(CASE WHEN type = 'D' THEN backup_finish_date END), GETDATE()) AS HoursSinceFullBackup,
        DATEDIFF(HOUR, MAX(CASE WHEN type = 'L' THEN backup_finish_date END), GETDATE()) AS HoursSinceLogBackup
    FROM msdb.dbo.backupset
    WHERE database_name = 'Atelier'
    GROUP BY database_name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Last Backup Information by Type")
    
    if results:
        print(f"\n{Fore.CYAN}Backup Strategy Analysis:{Style.RESET_ALL}")
        for row in results:
            hours_full = row[4] if row[4] else 999
            hours_log = row[5] if row[5] else 999
            
            if hours_full > 168:  # More than 7 days
                print(f"{Fore.RED}⚠ WARNING: Full backup is outdated (>{hours_full} hours ago){Style.RESET_ALL}")
            elif hours_full > 24:
                print(f"{Fore.YELLOW}⚠ NOTICE: Full backup is {hours_full} hours old{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Full backup is recent ({hours_full} hours ago){Style.RESET_ALL}")
            
            if hours_log > 2:
                print(f"{Fore.YELLOW}⚠ NOTICE: Log backup is {hours_log} hours old{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Log backup is recent ({hours_log} hours ago){Style.RESET_ALL}")


def view_job_schedules(db):
    """View schedules for backup jobs"""
    query = """
    SELECT 
        j.name AS JobName,
        s.name AS ScheduleName,
        CASE s.freq_type
            WHEN 1 THEN 'Once'
            WHEN 4 THEN 'Daily'
            WHEN 8 THEN 'Weekly'
            WHEN 16 THEN 'Monthly'
            WHEN 32 THEN 'Monthly, relative to freq_interval'
            WHEN 64 THEN 'Execute when SQL Server Agent starts'
            WHEN 128 THEN 'Execute when computer is idle'
        END AS Frequency,
        CASE s.freq_subday_type
            WHEN 1 THEN 'At the specified time'
            WHEN 2 THEN 'Seconds'
            WHEN 4 THEN 'Minutes'
            WHEN 8 THEN 'Hours'
        END AS SubdayFrequency,
        s.freq_subday_interval AS SubdayInterval,
        STUFF(STUFF(RIGHT('000000' + CAST(s.active_start_time AS VARCHAR(6)), 6), 5, 0, ':'), 3, 0, ':') AS StartTime,
        s.enabled AS IsEnabled
    FROM msdb.dbo.sysjobs j
    INNER JOIN msdb.dbo.sysjobschedules js ON j.job_id = js.job_id
    INNER JOIN msdb.dbo.sysschedules s ON js.schedule_id = s.schedule_id
    WHERE j.name LIKE '%Atelier%'
    ORDER BY j.name, s.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Backup Job Schedules")


def view_job_execution_history(db):
    """View job execution history with success/failure status"""
    query = """
    SELECT TOP 30
        j.name AS JobName,
        h.step_id AS StepID,
        h.step_name AS StepName,
        CASE h.run_status
            WHEN 0 THEN 'Failed'
            WHEN 1 THEN 'Succeeded'
            WHEN 2 THEN 'Retry'
            WHEN 3 THEN 'Canceled'
            WHEN 4 THEN 'In Progress'
        END AS Status,
        STUFF(STUFF(RIGHT('00000000' + CAST(h.run_date AS VARCHAR(8)), 8), 7, 0, '-'), 5, 0, '-') AS RunDate,
        STUFF(STUFF(RIGHT('000000' + CAST(h.run_time AS VARCHAR(6)), 6), 5, 0, ':'), 3, 0, ':') AS RunTime,
        h.run_duration AS DurationSeconds,
        LEFT(h.message, 200) AS Message
    FROM msdb.dbo.sysjobs j
    INNER JOIN msdb.dbo.sysjobhistory h ON j.job_id = h.job_id
    WHERE j.name LIKE '%Atelier%'
        AND h.step_id = 0  -- 0 = overall job status
    ORDER BY h.run_date DESC, h.run_time DESC
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Job Execution History (Last 30 runs)")


def manual_backup_execution(db):
    """Execute a backup job manually"""
    # Check user permissions in msdb
    print(f"\n{Fore.CYAN}Checking permissions...{Style.RESET_ALL}")
    perm_check = """
    SELECT 
        USER_NAME() AS CurrentUser,
        IS_MEMBER('SQLAgentUserRole') AS IsSQLAgentUser,
        IS_MEMBER('SQLAgentReaderRole') AS IsSQLAgentReader,
        IS_MEMBER('SQLAgentOperatorRole') AS IsSQLAgentOperator,
        IS_SRVROLEMEMBER('sysadmin') AS IsSysAdmin
    """
    try:
        cols, perm_results = db.execute_query(perm_check)
        if perm_results:
            user = perm_results[0][0]
            is_sysadmin = perm_results[0][4]
            is_operator = perm_results[0][3]
            
            print(f"  Current user: {user}")
            print(f"  SysAdmin: {'Yes' if is_sysadmin else 'No'}")
            print(f"  SQLAgentOperatorRole: {'Yes' if is_operator else 'No'}")
            
            if not is_sysadmin and not is_operator:
                print(f"\n{Fore.YELLOW}Warning: User lacks permissions to start jobs!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Need either sysadmin or SQLAgentOperatorRole in msdb.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not check permissions: {e}{Style.RESET_ALL}")
    
    # Check if SQL Agent is running
    print(f"\n{Fore.CYAN}Checking SQL Server Agent status...{Style.RESET_ALL}")
    agent_check = """
    SELECT 
        CASE 
            WHEN dss.status = 4 THEN 'Running'
            WHEN dss.status = 1 THEN 'Stopped'
            ELSE 'Unknown'
        END AS AgentStatus
    FROM sys.dm_server_services dss
    WHERE dss.servicename LIKE 'SQL Server Agent%'
    """
    try:
        cols, agent_results = db.execute_query(agent_check)
        if agent_results and agent_results[0][0] != 'Running':
            print(f"{Fore.RED}SQL Server Agent is not running!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Jobs cannot be executed when Agent is stopped.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Start SQL Server Agent service to enable job execution.{Style.RESET_ALL}")
            return
        else:
            print(f"{Fore.GREEN}✓ SQL Server Agent is running{Style.RESET_ALL}")
    except:
        print(f"{Fore.YELLOW}Could not check Agent status (requires VIEW SERVER STATE permission){Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Available Backup Jobs:{Style.RESET_ALL}")
    
    # List available jobs
    query = """
    SELECT name, enabled, description
    FROM msdb.dbo.sysjobs
    WHERE name LIKE '%Atelier%'
    ORDER BY name
    """
    columns, results = db.execute_query(query)
    
    if not results:
        print(f"{Fore.RED}No Atelier backup jobs found!{Style.RESET_ALL}")
        return
    
    for i, row in enumerate(results, 1):
        status = "✓ Enabled" if row[1] else "✗ Disabled"
        print(f"{i}. {row[0]} - {status}")
    
    try:
        choice = int(input(f"\n{Fore.YELLOW}Select job to execute (0 to cancel): {Style.RESET_ALL}"))
        if choice == 0 or choice > len(results):
            return
        
        job_name = results[choice - 1][0].strip()  # Remove any whitespace
        
        # Verify job exists with detailed info
        verify_query = f"""
        SELECT 
            CONVERT(VARCHAR(36), job_id) AS job_id_str,
            name,
            enabled,
            owner_sid,
            SUSER_SNAME(owner_sid) AS owner_name
        FROM msdb.dbo.sysjobs 
        WHERE name = N'{job_name}'
        """
        cols, verify_results = db.execute_query(verify_query)
        
        if not verify_results:
            print(f"{Fore.RED}Error: Job '{job_name}' not found in msdb.dbo.sysjobs!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}The job may need to be created. Check your backup configuration scripts.{Style.RESET_ALL}")
            return
        
        job_id_str = verify_results[0][0]
        owner_name = verify_results[0][4] if len(verify_results[0]) > 4 else 'Unknown'
        
        print(f"{Fore.CYAN}Job details:{Style.RESET_ALL}")
        print(f"  Job ID: {job_id_str}")
        print(f"  Owner: {owner_name}")
        print()
        
        actual_name = verify_results[0][1]
        is_enabled = verify_results[0][2]
        
        confirm = input(f"Execute job '{actual_name}'? (y/n): ")
        if confirm.lower() != 'y':
            return
        
        if not is_enabled:
            print(f"{Fore.YELLOW}Warning: Job is disabled. Enabling it temporarily...{Style.RESET_ALL}")
            enable_query = f"EXEC msdb.dbo.sp_update_job @job_name = N'{actual_name}', @enabled = 1"
            db.execute_query(enable_query, fetch=False, autocommit=True)
        
        # Execute job - try different methods
        print(f"{Fore.CYAN}Starting job...{Style.RESET_ALL}")
        
        # Method 1: Direct call without USE statement (fully qualified name)
        try:
            exec_query = f"EXEC msdb.dbo.sp_start_job @job_name = N'{actual_name}'"
            db.execute_query(exec_query, fetch=False, autocommit=True)
            print(f"{Fore.GREEN}✓ Job '{actual_name}' started successfully!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Note: Job is running in background. Check execution history for results.{Style.RESET_ALL}")
        except Exception as job_error:
            error_msg = str(job_error)
            print(f"{Fore.YELLOW}Method 1 failed: {error_msg[:100]}{Style.RESET_ALL}")
            
            # Check if it's a permission issue or agent not running
            if "14262" in error_msg:
                print(f"\n{Fore.RED}Job not found by SQL Agent (Error 14262)!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Common causes:{Style.RESET_ALL}")
                print(f"  1. Job exists in sysjobs but not registered with SQL Agent")
                print(f"  2. Job owner mismatch - owner must have SQLAgentOperatorRole")
                print(f"  3. Job was created but sp_add_jobserver was not executed")
                print(f"\n{Fore.YELLOW}To fix, recreate the job using Step 1.sql script{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Or add job to server:{Style.RESET_ALL}")
                print(f"  EXEC msdb.dbo.sp_add_jobserver @job_name=N'{actual_name}', @server_name=N'(local)'")
            elif "229" in error_msg or "permission" in error_msg.lower():
                print(f"\n{Fore.RED}Permission denied!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}User needs SQLAgentOperatorRole or sysadmin role.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Current user: {db.role}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}Trying alternative method...{Style.RESET_ALL}")
                
                # Method 2: Try with explicit job_id conversion (no USE statement)
                try:
                    exec_query2 = f"""
                    DECLARE @jobid UNIQUEIDENTIFIER;
                    SET @jobid = CAST('{job_id_str}' AS UNIQUEIDENTIFIER);
                    EXEC msdb.dbo.sp_start_job @job_id = @jobid;
                    """
                    db.execute_query(exec_query2, fetch=False, autocommit=True)
                    print(f"{Fore.GREEN}✓ Job started using alternative method!{Style.RESET_ALL}")
                except Exception as alt_error:
                    print(f"{Fore.RED}Alternative method also failed: {str(alt_error)[:150]}{Style.RESET_ALL}")
                    print(f"\n{Fore.YELLOW}Manual execution command for SSMS:{Style.RESET_ALL}")
                    print(f"  EXEC msdb.dbo.sp_start_job N'{actual_name}';")
                    print(f"\n{Fore.CYAN}Job owner: {owner_name}{Style.RESET_ALL}")
        
    except (ValueError, IndexError):
        print(f"{Fore.RED}Invalid selection!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
