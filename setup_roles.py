"""
Setup script to create custom database roles for user management
"""
import pyodbc

# Connection parameters
server = 'localhost'
database = 'Atelier'
username = 'atelier_admin'
password = 'Admin@2025!Strong'

conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'TrustServerCertificate=yes;'
)

print("="*80)
print("CREATING CUSTOM DATABASE ROLES FOR USER MANAGEMENT")
print("="*80)
print()

try:
    print("Connecting to database...")
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()
    print("✓ Connected successfully\n")
    
    # ================================================================
    # 1. Create AtelierManager role
    # ================================================================
    print("Creating role: AtelierManager")
    
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierManager' AND type = 'R')
        BEGIN
            CREATE ROLE [AtelierManager];
        END
    """)
    
    cursor.execute("ALTER ROLE [db_datareader] ADD MEMBER [AtelierManager]")
    cursor.execute("ALTER ROLE [db_datawriter] ADD MEMBER [AtelierManager]")
    cursor.execute("GRANT UNMASK TO [AtelierManager]")
    
    print("  ✓ Role created")
    print("  ✓ Permissions: db_datareader, db_datawriter, UNMASK")
    print()
    
    # ================================================================
    # 2. Create AtelierTailor role
    # ================================================================
    print("Creating role: AtelierTailor")
    
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierTailor' AND type = 'R')
        BEGIN
            CREATE ROLE [AtelierTailor];
        END
    """)
    
    cursor.execute("ALTER ROLE [db_datareader] ADD MEMBER [AtelierTailor]")
    
    # Grant specific permissions for orders
    tables = ['Orders', 'OrderCosts', 'OrderComplications', 'OrderFabrics']
    for table in tables:
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[{table}] TO [AtelierTailor]")
    
    # Grant read-only for reference tables (only if they exist)
    ref_tables = ['Tailors', 'Fabrics', 'OrderStatuses']
    for table in ref_tables:
        try:
            cursor.execute(f"GRANT SELECT ON [dbo].[{table}] TO [AtelierTailor]")
        except Exception as e:
            if "does not exist" not in str(e):
                raise
    
    print("  ✓ Role created")
    print("  ✓ Permissions: db_datareader + INSERT/UPDATE/DELETE on Orders, OrderCosts, etc.")
    print()
    
    # ================================================================
    # 3. Create AtelierCashier role
    # ================================================================
    print("Creating role: AtelierCashier")
    
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierCashier' AND type = 'R')
        BEGIN
            CREATE ROLE [AtelierCashier];
        END
    """)
    
    cursor.execute("ALTER ROLE [db_datareader] ADD MEMBER [AtelierCashier]")
    cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[CashRegister] TO [AtelierCashier]")
    
    # Grant read-only for orders and customers
    cursor.execute("GRANT SELECT ON [dbo].[Orders] TO [AtelierCashier]")
    cursor.execute("GRANT SELECT ON [dbo].[Customers] TO [AtelierCashier]")
    cursor.execute("GRANT SELECT ON [dbo].[OrderStatuses] TO [AtelierCashier]")
    
    print("  ✓ Role created")
    print("  ✓ Permissions: db_datareader + INSERT/UPDATE/DELETE on CashRegister")
    print()
    
    # ================================================================
    # 4. Update existing users to use roles
    # ================================================================
    print("="*80)
    print("UPDATING EXISTING USERS")
    print("="*80)
    print()
    
    user_role_mapping = [
        ('manager', 'AtelierManager'),
        ('tailor_user', 'AtelierTailor'),
        ('cashier', 'AtelierCashier')
    ]
    
    for user, role in user_role_mapping:
        cursor.execute(f"SELECT COUNT(*) FROM sys.database_principals WHERE name = '{user}'")
        if cursor.fetchone()[0] > 0:
            try:
                cursor.execute(f"ALTER ROLE [{role}] ADD MEMBER [{user}]")
                print(f"✓ User [{user}] added to role [{role}]")
            except Exception as e:
                if "already a member" in str(e).lower():
                    print(f"  ℹ User [{user}] already in role [{role}]")
                else:
                    print(f"  ⚠ Warning for [{user}]: {e}")
    
    print()
    
    # ================================================================
    # 5. Verify roles
    # ================================================================
    print("="*80)
    print("VERIFICATION - Current Database Roles")
    print("="*80)
    print()
    
    cursor.execute("""
        SELECT 
            r.name AS RoleName,
            COUNT(DISTINCT m.principal_id) AS MemberCount
        FROM sys.database_principals r
        LEFT JOIN sys.database_role_members rm ON r.principal_id = rm.role_principal_id
        LEFT JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
        WHERE r.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
        GROUP BY r.name
        ORDER BY r.name
    """)
    
    print(f"{'Role Name':<25} {'Members':<10}")
    print("-"*40)
    for row in cursor.fetchall():
        print(f"{row[0]:<25} {row[1]:<10}")
    
    print()
    print("="*80)
    print("✓ DATABASE ROLES SETUP COMPLETED SUCCESSFULLY!")
    print("="*80)
    print()
    print("Benefits of Role-Based Access Control (RBAC):")
    print("  • Simplified user management - just add to role")
    print("  • Consistent permissions across all users")
    print("  • Easy to modify permissions for entire group")
    print("  • Better security and audit trail")
    print()
    print("Usage in application:")
    print("  When approving registration, execute:")
    print("    ALTER ROLE [AtelierManager] ADD MEMBER [new_username]")
    print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
