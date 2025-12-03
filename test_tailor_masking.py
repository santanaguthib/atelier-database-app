import pyodbc

# Подключение под портным
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Atelier;'
    'UID=tailor_user;'
    'PWD=Tailor@2025!Pass'
)

cursor = conn.cursor()

print('\n' + '='*80)
print('ПРОВЕРКА МАСКИРОВКИ ДЛЯ РОЛИ AtelierTailor (пользователь: tailor_user)')
print('='*80 + '\n')

# Проверяем, какие столбцы замаскированы
print('1. Информация о замаскированных столбцах:')
print('-' * 80)

mask_query = """
SELECT 
    t.name AS TableName,
    c.name AS ColumnName,
    c.masking_function AS MaskingFunction
FROM sys.masked_columns c
JOIN sys.tables t ON c.object_id = t.object_id
ORDER BY t.name, c.name
"""

cursor.execute(mask_query)
masked_columns = cursor.fetchall()

if masked_columns:
    for row in masked_columns:
        print(f'  Таблица: {row[0]:<20} Столбец: {row[1]:<20} Маска: {row[2]}')
else:
    print('  Нет замаскированных столбцов')

# Проверяем данные из таблицы Customers (там должны быть замаскированные поля)
print('\n2. Просмотр данных клиентов (с маскировкой):')
print('-' * 80)

try:
    customer_query = """
    SELECT TOP 5
        CustomerID,
        CustomerName,
        Phone,
        Address
    FROM Customers
    ORDER BY CustomerID
    """
    
    cursor.execute(customer_query)
    customers = cursor.fetchall()
    
    if customers:
        print(f'\n{"ID":<5} {"Имя клиента":<30} {"Телефон":<20} {"Адрес":<30}')
        print('-' * 90)
        for row in customers:
            customer_id = row[0]
            customer_name = row[1] if row[1] else 'NULL'
            phone = row[2] if row[2] else 'NULL'
            address = row[3] if row[3] else 'NULL'
            print(f'{customer_id:<5} {customer_name:<30} {phone:<20} {address:<30}')
    else:
        print('  Нет данных в таблице Customers')
except Exception as e:
    print(f'  Ошибка при чтении Customers: {e}')

# Проверяем права UNMASK
print('\n3. Проверка прав UNMASK:')
print('-' * 80)

unmask_query = """
SELECT 
    dp.name AS PrincipalName,
    perm.permission_name,
    perm.state_desc
FROM sys.database_permissions perm
JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE perm.permission_name = 'UNMASK'
"""

cursor.execute(unmask_query)
unmask_perms = cursor.fetchall()

if unmask_perms:
    for row in unmask_perms:
        print(f'  {row[0]}: {row[2]} {row[1]}')
else:
    print('  Нет прав UNMASK ни у кого')

cursor.close()
conn.close()

print('\n' + '='*80)
print('✓ Проверка завершена')
print('='*80 + '\n')
