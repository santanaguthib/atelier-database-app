import pyodbc

# Подключение к базе данных
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Atelier;'
    'UID=atelier_admin;'
    'PWD=Admin@2025!Strong'
)

cursor = conn.cursor()

print('\n' + '='*80)
print('ПРАВА ПОЛЬЗОВАТЕЛЬСКИХ РОЛЕЙ В БАЗЕ ДАННЫХ ATELIER')
print('='*80 + '\n')

# Запрос для получения разрешений ролей
query = """
SELECT 
    dp.name AS RoleName,
    dp.type_desc AS RoleType,
    CASE 
        WHEN perm.state_desc IS NULL THEN 'НЕТ ПРЯМЫХ РАЗРЕШЕНИЙ'
        ELSE perm.state_desc 
    END AS PermissionState,
    COALESCE(perm.permission_name, '-') AS Permission,
    COALESCE(OBJECT_NAME(perm.major_id), perm.class_desc) AS ObjectName
FROM sys.database_principals dp
LEFT JOIN sys.database_permissions perm ON dp.principal_id = perm.grantee_principal_id
WHERE dp.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY dp.name, perm.permission_name, ObjectName
"""

cursor.execute(query)
rows = cursor.fetchall()

current_role = None
for row in rows:
    role_name = row[0]
    role_type = row[1]
    perm_state = row[2]
    permission = row[3]
    object_name = row[4]
    
    if current_role != role_name:
        if current_role is not None:
            print()
        current_role = role_name
        print(f'\n{"▶ " + role_name}')
        print('-' * 80)
    
    if permission == '-':
        print(f'  {perm_state}')
    else:
        print(f'  {perm_state:<10} {permission:<30} на {object_name}')

# Дополнительная информация о членстве в других ролях
print('\n' + '='*80)
print('ЧЛЕНСТВО В СТАНДАРТНЫХ РОЛЯХ')
print('='*80 + '\n')

membership_query = """
SELECT 
    role.name AS RoleName,
    member.name AS MemberRole
FROM sys.database_role_members drm
JOIN sys.database_principals role ON drm.role_principal_id = role.principal_id
JOIN sys.database_principals member ON drm.member_principal_id = member.principal_id
WHERE member.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY member.name, role.name
"""

cursor.execute(membership_query)
membership_rows = cursor.fetchall()

if membership_rows:
    current_member = None
    for row in membership_rows:
        parent_role = row[0]
        member_role = row[1]
        
        if current_member != member_role:
            if current_member is not None:
                print()
            current_member = member_role
            print(f'\n▶ {member_role}')
            print('-' * 80)
        
        print(f'  Член роли: {parent_role}')
else:
    print('Нет членства в стандартных ролях')

# Проверка специальных разрешений (UNMASK)
print('\n' + '='*80)
print('СПЕЦИАЛЬНЫЕ РАЗРЕШЕНИЯ НА УРОВНЕ БАЗЫ ДАННЫХ')
print('='*80 + '\n')

special_query = """
SELECT 
    dp.name AS RoleName,
    perm.permission_name AS Permission,
    perm.state_desc AS State
FROM sys.database_permissions perm
JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE dp.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
    AND perm.class = 0  -- Database-level permissions
ORDER BY dp.name, perm.permission_name
"""

cursor.execute(special_query)
special_rows = cursor.fetchall()

if special_rows:
    for row in special_rows:
        role_name = row[0]
        permission = row[1]
        state = row[2]
        print(f'▶ {role_name}: {state} {permission}')
else:
    print('Нет специальных разрешений на уровне БД')

cursor.close()
conn.close()

print('\n' + '='*80)
print('✓ Анализ завершен')
print('='*80 + '\n')
