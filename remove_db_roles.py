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

print('\nУдаление стандартных ролей db_datareader и db_datawriter...\n')

# Список пользователей и ролей для удаления
users_to_update = [
    ('manager', ['db_datareader', 'db_datawriter']),
    ('cashier', ['db_datareader']),
    ('tailor_user', ['db_datareader'])
]

for username, roles in users_to_update:
    for role in roles:
        try:
            sql = f"ALTER ROLE [{role}] DROP MEMBER [{username}]"
            cursor.execute(sql)
            print(f'✓ Роль {role} удалена у пользователя {username}')
        except Exception as e:
            print(f'✗ Ошибка при удалении роли {role} у {username}: {e}')

print('\n' + '='*60)
print('Проверка текущих ролей:')
print('='*60 + '\n')

# Проверяем текущее состояние
query = """
SELECT 
    dp.name AS Username,
    STRING_AGG(r.name, ', ') AS Roles
FROM sys.database_principals dp
LEFT JOIN sys.database_role_members drm ON dp.principal_id = drm.member_principal_id
LEFT JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
WHERE dp.type = 'S' 
    AND dp.name NOT LIKE '##%##'
    AND dp.name IN ('atelier_admin', 'manager', 'cashier', 'tailor_user', 'guest')
GROUP BY dp.name
ORDER BY dp.name
"""

cursor.execute(query)
rows = cursor.fetchall()

print(f'{"Пользователь":<20} | {"Роли":<40}')
print('-' * 62)
for row in rows:
    username = row[0]
    roles = row[1] if row[1] else "(нет ролей)"
    print(f'{username:<20} | {roles:<40}')

cursor.close()
conn.close()

print('\n✓ Готово!')
