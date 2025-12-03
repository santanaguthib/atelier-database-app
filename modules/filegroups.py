"""
Filegroups Module - View data distribution across filegroups
"""
from database import DatabaseConnection
from colorama import Fore, Style


def show_filegroups_menu(db):
    """Display filegroups submenu"""
    while True:
        print(f"\n{Fore.CYAN}{'='*80}")
        print("FILEGROUPS - Data Distribution & Storage Management")
        print(f"{'='*80}{Style.RESET_ALL}")
        print("1. View All Filegroups")
        print("2. View Files in Each Filegroup")
        print("3. View Table Distribution")
        print("4. View Index Distribution")
        print("5. View Filegroup Space Usage")
        print("6. View Data Distribution Summary")
        print("0. Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}")
        
        if choice == '1':
            view_all_filegroups(db)
        elif choice == '2':
            view_files_in_filegroups(db)
        elif choice == '3':
            view_table_distribution(db)
        elif choice == '4':
            view_index_distribution(db)
        elif choice == '5':
            view_space_usage(db)
        elif choice == '6':
            view_distribution_summary(db)
        elif choice == '0':
            break
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")


def view_all_filegroups(db):
    """View all filegroups in the database"""
    query = """
    SELECT 
        fg.data_space_id AS FileGroupID,
        fg.name AS FileGroupName,
        fg.type_desc AS Type,
        CASE fg.is_default
            WHEN 1 THEN 'YES'
            ELSE 'NO'
        END AS IsDefault,
        CASE fg.is_read_only
            WHEN 1 THEN 'YES'
            ELSE 'NO'
        END AS IsReadOnly,
        COUNT(DISTINCT t.object_id) AS TableCount
    FROM sys.filegroups fg
    LEFT JOIN sys.indexes i ON fg.data_space_id = i.data_space_id
    LEFT JOIN sys.tables t ON i.object_id = t.object_id AND i.index_id IN (0, 1)
    GROUP BY fg.data_space_id, fg.name, fg.type_desc, fg.is_default, fg.is_read_only
    ORDER BY fg.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Filegroups in Atelier Database")


def view_files_in_filegroups(db):
    """View physical files in each filegroup"""
    query = """
    SELECT 
        fg.name AS FileGroupName,
        df.name AS LogicalFileName,
        df.physical_name AS PhysicalFilePath,
        df.type_desc AS FileType,
        CAST(df.size * 8.0 / 1024 AS DECIMAL(10,2)) AS CurrentSizeMB,
        CASE df.max_size
            WHEN -1 THEN 'UNLIMITED'
            ELSE CAST(df.max_size * 8.0 / 1024 AS VARCHAR(20))
        END AS MaxSizeMB,
        CAST(df.growth * 8.0 / 1024 AS DECIMAL(10,2)) AS GrowthMB,
        CASE df.is_percent_growth
            WHEN 1 THEN 'Percent'
            ELSE 'MB'
        END AS GrowthType,
        df.state_desc AS State
    FROM sys.database_files df
    LEFT JOIN sys.filegroups fg ON df.data_space_id = fg.data_space_id
    ORDER BY fg.name, df.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Physical Files by Filegroup")


def view_table_distribution(db):
    """View how tables are distributed across filegroups"""
    query = """
    SELECT 
        OBJECT_NAME(i.object_id) AS TableName,
        i.name AS IndexName,
        i.type_desc AS IndexType,
        fg.name AS FileGroupName,
        SUM(p.[rows]) AS [RowCount],
        CAST(SUM(a.total_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS TotalSpaceMB,
        CAST(SUM(a.used_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS UsedSpaceMB,
        CAST((SUM(a.total_pages) - SUM(a.used_pages)) * 8.0 / 1024 AS DECIMAL(10,2)) AS UnusedSpaceMB
    FROM sys.indexes i
    INNER JOIN sys.filegroups fg ON i.data_space_id = fg.data_space_id
    INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
    WHERE OBJECT_NAME(i.object_id) IN (
        'Orders', 'OrderCosts', 'OrderComplications', 'OrderFabrics', 
        'CashRegister', 'OrderLogs'
    )
    AND i.index_id IN (0, 1)  -- Heap or Clustered Index only
    GROUP BY i.object_id, i.name, i.type_desc, fg.name
    ORDER BY fg.name, OBJECT_NAME(i.object_id)
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Table Distribution Across Filegroups")


def view_index_distribution(db):
    """View how indexes are distributed across filegroups"""
    query = """
    SELECT 
        OBJECT_NAME(i.object_id) AS TableName,
        i.name AS IndexName,
        i.type_desc AS IndexType,
        fg.name AS FileGroupName,
        i.is_primary_key AS IsPrimaryKey,
        i.is_unique AS IsUnique,
        CAST(SUM(ps.used_page_count) * 8.0 / 1024 AS DECIMAL(10,2)) AS UsedSpaceMB,
        SUM(ps.row_count) AS [RowCount]
    FROM sys.indexes i
    INNER JOIN sys.dm_db_partition_stats ps ON i.object_id = ps.object_id 
        AND i.index_id = ps.index_id
    INNER JOIN sys.filegroups fg ON i.data_space_id = fg.data_space_id
    WHERE OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1
        AND i.type_desc = 'NONCLUSTERED'
    GROUP BY i.object_id, i.name, i.type_desc, fg.name, i.is_primary_key, i.is_unique
    ORDER BY fg.name, OBJECT_NAME(i.object_id)
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Nonclustered Index Distribution")


def view_space_usage(db):
    """View space usage statistics by filegroup"""
    query = """
    SELECT 
        fg.name AS FileGroupName,
        CAST(SUM(a.total_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS TotalSpaceMB,
        CAST(SUM(a.used_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS UsedSpaceMB,
        CAST((SUM(a.total_pages) - SUM(a.used_pages)) * 8.0 / 1024 AS DECIMAL(10,2)) AS FreeSpaceMB,
        CAST(SUM(a.used_pages) * 100.0 / NULLIF(SUM(a.total_pages), 0) AS DECIMAL(5,2)) AS UsedPercent,
        COUNT(DISTINCT p.object_id) AS ObjectCount
    FROM sys.filegroups fg
    INNER JOIN sys.indexes i ON fg.data_space_id = i.data_space_id
    INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
    GROUP BY fg.name
    ORDER BY SUM(a.total_pages) DESC
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Space Usage by Filegroup")
    
    if results:
        print(f"\n{Fore.CYAN}Space Usage Summary:{Style.RESET_ALL}")
        total_space = sum(row[1] for row in results)
        total_used = sum(row[2] for row in results)
        total_free = sum(row[3] for row in results)
        
        print(f"Total Allocated: {Fore.GREEN}{total_space:.2f} MB{Style.RESET_ALL}")
        print(f"Total Used: {Fore.YELLOW}{total_used:.2f} MB{Style.RESET_ALL}")
        print(f"Total Free: {Fore.CYAN}{total_free:.2f} MB{Style.RESET_ALL}")
        print(f"Overall Usage: {Fore.GREEN}{(total_used/total_space*100):.2f}%{Style.RESET_ALL}")


def view_distribution_summary(db):
    """View comprehensive distribution summary"""
    query = """
    SELECT 
        fg.name AS FileGroupName,
        COUNT(DISTINCT CASE WHEN i.index_id IN (0,1) THEN i.object_id END) AS Tables,
        COUNT(DISTINCT CASE WHEN i.index_id > 1 THEN i.index_id END) AS Indexes,
        SUM(p.rows) AS TotalRows,
        CAST(SUM(a.total_pages) * 8.0 / 1024 AS DECIMAL(10,2)) AS TotalSpaceMB
    FROM sys.filegroups fg
    LEFT JOIN sys.indexes i ON fg.data_space_id = i.data_space_id
    LEFT JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
    LEFT JOIN sys.allocation_units a ON p.partition_id = a.container_id
    GROUP BY fg.name
    ORDER BY fg.name
    """
    columns, results = db.execute_query(query)
    db.display_results(columns, results, "Data Distribution Summary by Filegroup")
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print("FILEGROUP STRATEGY EXPLANATION")
    print(f"{'='*80}{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}PRIMARY:{Style.RESET_ALL}")
    print("  - Reference tables (Categories, Products, Customers, etc.)")
    print("  - Relatively static data with low write frequency")
    
    print(f"\n{Fore.GREEN}ORDERS_FG:{Style.RESET_ALL}")
    print("  - Transactional tables (Orders, OrderCosts, OrderFabrics, etc.)")
    print("  - High-frequency read/write operations")
    print("  - Benefit: Isolated I/O for performance")
    
    print(f"\n{Fore.GREEN}LOGS_FG:{Style.RESET_ALL}")
    print("  - Audit log table (OrderLogs)")
    print("  - Write-heavy, read-occasional")
    print("  - Benefit: Separate backup/maintenance schedule")
    
    print(f"\n{Fore.GREEN}INDEXES_FG:{Style.RESET_ALL}")
    print("  - All nonclustered indexes")
    print("  - Improves query performance")
    print("  - Benefit: Parallel I/O with table data")
    
    print(f"\n{Fore.CYAN}ADVANTAGES:{Style.RESET_ALL}")
    print("  ✓ Better I/O distribution across disks")
    print("  ✓ Selective backup/restore capabilities")
    print("  ✓ Improved maintenance operations")
    print("  ✓ Enhanced scalability")
