"""
Setup script to create UserRegistrationRequests table
"""
import pyodbc

# Connection parameters
server = 'localhost'
database = 'Atelier'
username = input("Enter username (atelier_admin): ").strip() or 'atelier_admin'
password = input("Enter password: ").strip()

conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'TrustServerCertificate=yes;'
)

sql_script = """
-- Create table for registration requests
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'UserRegistrationRequests')
BEGIN
    CREATE TABLE [dbo].[UserRegistrationRequests]
    (
        [RequestID] INT IDENTITY(1,1) PRIMARY KEY,
        [Username] NVARCHAR(128) NOT NULL,
        [HashedPassword] NVARCHAR(128) NOT NULL,
        [FullName] NVARCHAR(200) NOT NULL,
        [Email] NVARCHAR(200) NOT NULL,
        [RequestedRole] NVARCHAR(50) NOT NULL CHECK (RequestedRole IN ('manager', 'tailor_user', 'cashier')),
        [Justification] NVARCHAR(500) NULL,
        [RequestDate] DATETIME NOT NULL DEFAULT GETDATE(),
        [Status] NVARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected')),
        [ProcessedDate] DATETIME NULL,
        [ProcessedBy] NVARCHAR(128) NULL,
        [RejectionReason] NVARCHAR(500) NULL,
        
        CONSTRAINT UQ_Username UNIQUE (Username)
    );
    
    PRINT 'Table UserRegistrationRequests created successfully';
END
ELSE
BEGIN
    PRINT 'Table UserRegistrationRequests already exists';
END

-- Create index for faster status queries
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_RegistrationRequests_Status' AND object_id = OBJECT_ID('UserRegistrationRequests'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_RegistrationRequests_Status
    ON [dbo].[UserRegistrationRequests] ([Status])
    INCLUDE ([RequestDate], [Username], [RequestedRole]);
    
    PRINT 'Index IX_RegistrationRequests_Status created';
END

-- Grant permissions for manager to handle registration requests
GRANT SELECT, INSERT ON [dbo].[UserRegistrationRequests] TO [manager];
GRANT UPDATE ON [dbo].[UserRegistrationRequests] TO [manager];

PRINT '';
PRINT 'USER REGISTRATION SYSTEM - Setup Complete';
PRINT 'Features: Registration workflow, Admin approval, Audit trail';
"""

try:
    print("Connecting to database...")
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Executing SQL script...")
    
    # Split by GO and execute each batch
    batches = sql_script.split('GO')
    for batch in batches:
        batch = batch.strip()
        if batch:
            cursor.execute(batch)
            
            # Print any messages
            while cursor.nextset():
                pass
    
    print("\n✓ Setup completed successfully!")
    print("✓ Table 'UserRegistrationRequests' is ready")
    print("✓ Permissions granted to manager role")
    
    # Verify table creation
    cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'UserRegistrationRequests'")
    result = cursor.fetchone()
    
    if result[0] == 1:
        print("\n✓ Verification: Table exists in database")
        
        # Show table structure
        cursor.execute("""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'UserRegistrationRequests'
            ORDER BY ORDINAL_POSITION
        """)
        
        print("\nTable Structure:")
        print("-" * 80)
        for row in cursor.fetchall():
            col_name = row[0]
            data_type = row[1]
            max_len = row[2] if row[2] else ''
            nullable = row[3]
            print(f"  {col_name:25} {data_type}({max_len})  {'NULL' if nullable == 'YES' else 'NOT NULL'}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*80)
    print("You can now use the User Management module in the application!")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
