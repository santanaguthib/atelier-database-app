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

# Запрос для получения пользователей и их ролей
query = """
SELECT 
    dp.name AS Username,
    STRING_AGG(r.name, ', ') AS Roles
FROM sys.database_principals dp
LEFT JOIN sys.database_role_members drm ON dp.principal_id = drm.member_principal_id
LEFT JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
WHERE dp.type = 'S' AND dp.name NOT LIKE '##%##'
GROUP BY dp.name
ORDER BY dp.name
"""

cursor.execute(query)
rows = cursor.fetchall()

print('\nПользователи и их роли:')
print('=' * 70)
print(f'{"Пользователь":<30} | {"Роли":<35}')
print('-' * 70)

for row in rows:
    username = row[0]
    roles = row[1] if row[1] else "(нет ролей)"
    print(f'{username:<30} | {roles:<35}')

print('=' * 70)
print(f'\nВсего пользователей: {len(rows)}')

cursor.close()
conn.close()
