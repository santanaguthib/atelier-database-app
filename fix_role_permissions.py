import pyodbc

# Подключение к базе данных
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Atelier;'
    'UID=atelier_admin;'
    'PWD=Admin@2025!Strong',
    autocommit=True
)

cursor = conn.cursor()

print('\n' + '='*80)
print('УДАЛЕНИЕ ЛИШНИХ РАЗРЕШЕНИЙ У КАСТОМНЫХ РОЛЕЙ')
print('='*80 + '\n')

# 1. Удаляем роли db_datareader и db_datawriter у кастомных ролей
print('1. Удаление стандартных ролей db_datareader/db_datawriter:')
print('-' * 80)

roles_to_clean = [
    ('AtelierManager', ['db_datareader', 'db_datawriter']),
    ('AtelierTailor', ['db_datareader']),
    ('AtelierCashier', ['db_datareader'])
]

for role_name, db_roles in roles_to_clean:
    for db_role in db_roles:
        try:
            sql = f"ALTER ROLE [{db_role}] DROP MEMBER [{role_name}]"
            cursor.execute(sql)
            print(f'✓ Роль {db_role} удалена у {role_name}')
        except Exception as e:
            if 'is not a member' in str(e):
                print(f'  {role_name} уже не член {db_role}')
            else:
                print(f'✗ Ошибка при удалении {db_role} у {role_name}: {e}')

# 2. Удаляем лишние разрешения SELECT у AtelierCashier
print('\n2. Удаление лишних SELECT разрешений у AtelierCashier:')
print('-' * 80)

# AtelierCashier должен иметь SELECT только на: CashRegister, Orders, Customers, OrderStatuses
# Все остальные SELECT нужно отозвать
tables_to_keep_select = ['CashRegister', 'Orders', 'Customers', 'OrderStatuses']

# Получаем все таблицы, на которые у AtelierCashier есть SELECT
check_query = """
SELECT DISTINCT OBJECT_NAME(major_id) AS TableName
FROM sys.database_permissions
WHERE grantee_principal_id = (SELECT principal_id FROM sys.database_principals WHERE name = 'AtelierCashier')
    AND permission_name = 'SELECT'
    AND class = 1
"""

cursor.execute(check_query)
current_tables = [row[0] for row in cursor.fetchall()]

for table in current_tables:
    if table not in tables_to_keep_select:
        try:
            sql = f"REVOKE SELECT ON [dbo].[{table}] FROM [AtelierCashier]"
            cursor.execute(sql)
            print(f'✓ Отозван SELECT на {table} у AtelierCashier')
        except Exception as e:
            print(f'✗ Ошибка при отзыве SELECT на {table}: {e}')

# 3. Удаляем лишние разрешения SELECT у AtelierTailor
print('\n3. Удаление лишних SELECT разрешений у AtelierTailor:')
print('-' * 80)

# AtelierTailor должен иметь SELECT на: Orders, OrderFabrics, OrderCosts, OrderComplications, Fabrics, Tailors, OrderStatuses
tables_tailor_select = ['Orders', 'OrderFabrics', 'OrderCosts', 'OrderComplications', 'Fabrics', 'Tailors', 'OrderStatuses']

check_query_tailor = """
SELECT DISTINCT OBJECT_NAME(major_id) AS TableName
FROM sys.database_permissions
WHERE grantee_principal_id = (SELECT principal_id FROM sys.database_principals WHERE name = 'AtelierTailor')
    AND permission_name = 'SELECT'
    AND class = 1
"""

cursor.execute(check_query_tailor)
current_tables_tailor = [row[0] for row in cursor.fetchall()]

for table in current_tables_tailor:
    if table not in tables_tailor_select:
        try:
            sql = f"REVOKE SELECT ON [dbo].[{table}] FROM [AtelierTailor]"
            cursor.execute(sql)
            print(f'✓ Отозван SELECT на {table} у AtelierTailor')
        except Exception as e:
            print(f'✗ Ошибка при отзыве SELECT на {table}: {e}')

# 4. Добавляем недостающие разрешения для AtelierManager
print('\n4. Настройка AtelierManager (должен иметь полный доступ):')
print('-' * 80)

# Получаем список всех пользовательских таблиц
tables_query = """
SELECT name FROM sys.tables 
WHERE is_ms_shipped = 0 
ORDER BY name
"""
cursor.execute(tables_query)
all_tables = [row[0] for row in cursor.fetchall()]

print(f'Всего таблиц в БД: {len(all_tables)}')

for table in all_tables:
    for permission in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
        try:
            sql = f"GRANT {permission} ON [dbo].[{table}] TO [AtelierManager]"
            cursor.execute(sql)
        except Exception as e:
            if 'already granted' not in str(e):
                pass  # Пропускаем уже выданные разрешения

print(f'✓ AtelierManager имеет полный доступ ко всем {len(all_tables)} таблицам')

# 5. Проверяем финальное состояние
print('\n' + '='*80)
print('ФИНАЛЬНАЯ ПРОВЕРКА РАЗРЕШЕНИЙ')
print('='*80 + '\n')

final_check = """
SELECT 
    dp.name AS RoleName,
    perm.permission_name AS Permission,
    COALESCE(OBJECT_NAME(perm.major_id), 'DATABASE') AS ObjectName
FROM sys.database_principals dp
LEFT JOIN sys.database_permissions perm ON dp.principal_id = perm.grantee_principal_id
WHERE dp.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
    AND (perm.class = 0 OR perm.class = 1)
ORDER BY dp.name, ObjectName, perm.permission_name
"""

cursor.execute(final_check)
rows = cursor.fetchall()

current_role = None
for row in rows:
    role = row[0]
    perm = row[1]
    obj = row[2]
    
    if current_role != role:
        if current_role is not None:
            print()
        current_role = role
        print(f'▶ {role}:')
        print('-' * 70)
    
    if obj == 'DATABASE':
        print(f'  {perm} на уровне БД')
    else:
        print(f'  {perm} на {obj}')

cursor.close()
conn.close()

print('\n' + '='*80)
print('✓ Настройка завершена')
print('='*80 + '\n')
