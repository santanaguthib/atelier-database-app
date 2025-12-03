"""
TDE (Transparent Data Encryption) Module - View encryption status
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_tde_menu(db):
    """Display TDE submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("TRANSPARENT DATA ENCRYPTION (TDE) - Data-at-Rest Protection")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View Database Encryption Status")
        print("2. View Master Key Information")
        print("3. View Certificate Information")
        print("4. View Encryption Progress")
        print("5. View All Encrypted Databases")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_encryption_status(db)
        elif choice == '2':
            view_master_key_info(db)
        elif choice == '3':
            view_certificate_info(db)
        elif choice == '4':
            view_encryption_progress(db)
        elif choice == '5':
            view_all_encrypted_databases(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_encryption_status(db):
    """View TDE encryption status for Atelier database"""
    query = """
    SELECT 
        DB_NAME(dek.database_id) AS DatabaseName,
        dek.encryption_state AS EncryptionState,
        CASE dek.encryption_state
            WHEN 0 THEN 'No database encryption key present, no encryption'
            WHEN 1 THEN 'Unencrypted'
            WHEN 2 THEN 'Encryption in progress'
            WHEN 3 THEN 'Encrypted'
            WHEN 4 THEN 'Key change in progress'
            WHEN 5 THEN 'Decryption in progress'
            WHEN 6 THEN 'Protection change in progress'
        END AS EncryptionStateDesc,
        dek.create_date AS KeyCreatedDate,
        dek.regenerate_date AS KeyRegeneratedDate,
        dek.modify_date AS KeyModifiedDate,
        dek.percent_complete AS PercentComplete,
        c.name AS CertificateName,
        dek.encryption_scan_state AS ScanState,
        CASE dek.encryption_scan_state
            WHEN 0 THEN 'No scan initiated'
            WHEN 1 THEN 'Scan in progress'
            WHEN 2 THEN 'Scan complete'
        END AS ScanStateDesc
    FROM sys.dm_database_encryption_keys dek
    LEFT JOIN master.sys.certificates c ON dek.encryptor_thumbprint = c.thumbprint
    WHERE DB_NAME(dek.database_id) = 'Atelier'
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "TDE Encryption Status - Atelier Database")
    
    if results:
        encryption_state = results[0][1]
        if encryption_state == 3:
            print(f"\n{Fore.GREEN}✓ Database is FULLY ENCRYPTED{Style.RESET_ALL}")
        elif encryption_state == 2:
            percent = results[0][6]
            print(f"\n{Fore.YELLOW}⚠ Encryption in progress: {percent}%{Style.RESET_ALL}")
        elif encryption_state == 0 or encryption_state == 1:
            print(f"\n{Fore.RED}✗ Database is NOT ENCRYPTED{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}✗ No encryption key found. TDE is not configured.{Style.RESET_ALL}")


def view_master_key_info(db):
    """View Database Master Key information"""
    query = """
    SELECT 
        name AS KeyName,
        principal_id AS PrincipalID,
        key_guid AS KeyGUID,
        create_date AS CreatedDate,
        modify_date AS ModifiedDate
    FROM master.sys.symmetric_keys
    WHERE name = '##MS_DatabaseMasterKey##'
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Database Master Key Information")
    
    if not results:
        print(f"\n{Fore.YELLOW}Note: Database Master Key not found in master database.{Style.RESET_ALL}")


def view_certificate_info(db):
    """View TDE certificate information"""
    query = """
    SELECT 
        name AS CertificateName,
        certificate_id AS CertificateID,
        subject AS Subject,
        start_date AS ValidFrom,
        expiry_date AS ValidTo,
        DATEDIFF(DAY, GETDATE(), expiry_date) AS DaysUntilExpiry,
        CASE 
            WHEN expiry_date < GETDATE() THEN 'EXPIRED'
            WHEN DATEDIFF(DAY, GETDATE(), expiry_date) < 30 THEN 'EXPIRING SOON'
            ELSE 'VALID'
        END AS Status,
        thumbprint AS Thumbprint,
        pvt_key_last_backup_date AS LastBackupDate
    FROM master.sys.certificates
    WHERE name LIKE '%TDE%' OR name LIKE '%Atelier%'
    ORDER BY name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "TDE Certificate Information")
    
    if results:
        for row in results:
            days_until_expiry = row[5]
            status = row[6]
            last_backup = row[8]
            
            if status == 'EXPIRED':
                print(f"\n{Fore.RED}⚠ CRITICAL: Certificate has EXPIRED!{Style.RESET_ALL}")
            elif status == 'EXPIRING SOON':
                print(f"\n{Fore.YELLOW}⚠ WARNING: Certificate expires in {days_until_expiry} days!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✓ Certificate is valid ({days_until_expiry} days remaining){Style.RESET_ALL}")
            
            if last_backup:
                print(f"{Fore.GREEN}✓ Certificate backed up on: {last_backup}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}⚠ WARNING: Certificate has NOT been backed up!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  Backup is CRITICAL for disaster recovery!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}No TDE certificates found.{Style.RESET_ALL}")


def view_encryption_progress(db):
    """View detailed encryption progress and statistics"""
    query = """
    SELECT 
        DB_NAME(database_id) AS DatabaseName,
        encryption_state AS State,
        percent_complete AS PercentComplete,
        key_algorithm AS Algorithm,
        key_length AS KeyLength,
        create_date AS Started,
        DATEDIFF(MINUTE, create_date, GETDATE()) AS MinutesElapsed,
        CASE 
            WHEN encryption_state = 2 THEN 
                CAST(DATEDIFF(MINUTE, create_date, GETDATE()) * (100.0 / NULLIF(percent_complete, 0)) AS INT)
            ELSE NULL
        END AS EstimatedTotalMinutes
    FROM sys.dm_database_encryption_keys
    WHERE DB_NAME(database_id) = 'Atelier'
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Encryption Progress Details")
    
    if results and results[0][1] == 2:  # State = 2 means encryption in progress
        percent = results[0][2]
        elapsed = results[0][6]
        estimated = results[0][7]
        
        print(f"\n{Fore.CYAN}Encryption Progress Analysis:{Style.RESET_ALL}")
        print(f"Progress: {Fore.YELLOW}{percent}%{Style.RESET_ALL}")
        print(f"Time Elapsed: {elapsed} minutes")
        if estimated:
            remaining = estimated - elapsed
            print(f"Estimated Time Remaining: ~{remaining} minutes")


def view_all_encrypted_databases(db):
    """View all databases with TDE encryption on this server"""
    query = """
    SELECT 
        DB_NAME(dek.database_id) AS DatabaseName,
        CASE dek.encryption_state
            WHEN 0 THEN 'No encryption'
            WHEN 1 THEN 'Unencrypted'
            WHEN 2 THEN 'Encryption in progress'
            WHEN 3 THEN 'Encrypted'
            WHEN 4 THEN 'Key change'
            WHEN 5 THEN 'Decryption in progress'
        END AS Status,
        c.name AS CertificateName,
        dek.create_date AS EncryptionStarted,
        d.recovery_model_desc AS RecoveryModel,
        CAST(SUM(mf.size) * 8.0 / 1024 AS DECIMAL(10,2)) AS DatabaseSizeMB
    FROM sys.dm_database_encryption_keys dek
    INNER JOIN sys.databases d ON dek.database_id = d.database_id
    LEFT JOIN master.sys.certificates c ON dek.encryptor_thumbprint = c.thumbprint
    LEFT JOIN sys.master_files mf ON dek.database_id = mf.database_id
    GROUP BY dek.database_id, dek.encryption_state, c.name, dek.create_date, d.recovery_model_desc
    ORDER BY DB_NAME(dek.database_id)
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "All Encrypted Databases on Server")
    
    if results:
        encrypted_count = sum(1 for row in results if row[1] == 'Encrypted')
        total_count = len(results)
        print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"Encrypted databases: {Fore.GREEN}{encrypted_count}{Style.RESET_ALL} out of {total_count}")
    else:
        print(f"\n{Fore.YELLOW}No encrypted databases found on this server.{Style.RESET_ALL}")
