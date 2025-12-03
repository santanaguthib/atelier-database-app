# 🎯 ROLE-BASED ACCESS CONTROL (RBAC) - Управление через роли БД

## 📋 Обзор

Вместо назначения прав каждому пользователю индивидуально, система теперь использует **роли базы данных** (Database Roles). Это упрощает управление и соответствует лучшим практикам безопасности SQL Server.

---

## ✨ ПРЕИМУЩЕСТВА RBAC

| До (без ролей) | После (с ролями) |
|----------------|------------------|
| ❌ Назначение прав каждому пользователю вручную | ✅ Просто добавить в роль |
| ❌ Риск несоответствия прав между пользователями | ✅ Все в роли имеют одинаковые права |
| ❌ Сложно изменить права всем пользователям | ✅ Изменить права роли → все получают |
| ❌ Много SQL команд при создании пользователя | ✅ Одна команда: ALTER ROLE |
| ❌ Трудно аудитировать права | ✅ Просто: какая роль = какие права |

---

## 🔐 СОЗДАННЫЕ РОЛИ

### 1. **AtelierManager**

**Описание:** Менеджер с полным доступом к данным

**Права:**
- `db_datareader` - чтение всех таблиц
- `db_datawriter` - изменение всех таблиц
- `UNMASK` - видит не маскированные данные (DDM)

**SQL:**
```sql
CREATE ROLE [AtelierManager];
ALTER ROLE [db_datareader] ADD MEMBER [AtelierManager];
ALTER ROLE [db_datawriter] ADD MEMBER [AtelierManager];
GRANT UNMASK TO [AtelierManager];
```

**Кто получает:** Пользователи, регистрирующиеся с ролью `manager`

---

### 2. **AtelierTailor**

**Описание:** Портной, работающий с производственными заказами

**Права:**
- `db_datareader` - чтение всех таблиц
- **INSERT, UPDATE, DELETE** на таблицы:
  - `Orders` - заказы
  - `OrderCosts` - стоимость заказов
  - `OrderComplications` - сложности выполнения
  - `OrderFabrics` - использованные ткани
- **SELECT** (только чтение) на справочные таблицы:
  - `Tailors` - список портных
  - `Fabrics` - список тканей
  - `OrderStatuses` - статусы заказов

**SQL:**
```sql
CREATE ROLE [AtelierTailor];
ALTER ROLE [db_datareader] ADD MEMBER [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[Orders] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderCosts] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderComplications] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderFabrics] TO [AtelierTailor];
```

**Кто получает:** Пользователи, регистрирующиеся с ролью `tailor_user`

**Видит маскированные данные:** ДА (DDM активен)

---

### 3. **AtelierCashier**

**Описание:** Кассир, работающий с платежами

**Права:**
- `db_datareader` - чтение всех таблиц
- **INSERT, UPDATE, DELETE** на таблицу:
  - `CashRegister` - кассовые операции
- **SELECT** (только чтение) на таблицы:
  - `Orders` - просмотр заказов
  - `Customers` - информация о клиентах
  - `OrderStatuses` - статусы заказов

**SQL:**
```sql
CREATE ROLE [AtelierCashier];
ALTER ROLE [db_datareader] ADD MEMBER [AtelierCashier];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[CashRegister] TO [AtelierCashier];
GRANT SELECT ON [dbo].[Orders] TO [AtelierCashier];
GRANT SELECT ON [dbo].[Customers] TO [AtelierCashier];
GRANT SELECT ON [dbo].[OrderStatuses] TO [AtelierCashier];
```

**Кто получает:** Пользователи, регистрирующиеся с ролью `cashier`

**Видит маскированные данные:** ДА (DDM активен)

---

## 🚀 УСТАНОВКА РОЛЕЙ

### Метод 1: SQL скрипт

```bash
# Выполните в SSMS:
C:\AppAppAppAppApp\SQL_Scripts\Step_6a_CreateDatabaseRoles.sql
```

### Метод 2: Python скрипт

```bash
cd C:\AppAppAppAppApp\AtelierApp
python setup_roles.py
```

**Результат:**
```
✓ Role [AtelierManager] created
✓ Role [AtelierTailor] created
✓ Role [AtelierCashier] created
✓ Existing users updated
```

---

## 📊 КАК ЭТО РАБОТАЕТ В ПРИЛОЖЕНИИ

### Старый метод (без ролей):

```python
# Много команд для каждого пользователя
if role == 'manager':
    db.execute_query("ALTER ROLE [db_datareader] ADD MEMBER [username]")
    db.execute_query("ALTER ROLE [db_datawriter] ADD MEMBER [username]")
    db.execute_query("GRANT UNMASK TO [username]")
elif role == 'tailor_user':
    db.execute_query("ALTER ROLE [db_datareader] ADD MEMBER [username]")
    db.execute_query("GRANT INSERT, UPDATE, DELETE ON Orders TO [username]")
    db.execute_query("GRANT INSERT, UPDATE, DELETE ON OrderCosts TO [username]")
    # ... и так далее
```

### Новый метод (с ролями):

```python
# Одна команда!
role_mapping = {
    'manager': 'AtelierManager',
    'tailor_user': 'AtelierTailor',
    'cashier': 'AtelierCashier'
}

db_role = role_mapping[role]
db.execute_query(f"ALTER ROLE [{db_role}] ADD MEMBER [{username}]")
```

**Код сократился в 5-10 раз!** 🎯

---

## 🔍 ПРОВЕРКА РОЛЕЙ И ЧЛЕНСТВА

### Посмотреть все роли:

```sql
SELECT 
    name AS RoleName,
    create_date AS CreatedDate
FROM sys.database_principals
WHERE type = 'R' AND name LIKE 'Atelier%'
ORDER BY name;
```

**Результат:**
```
RoleName         CreatedDate
AtelierCashier   2025-12-03 12:30:00
AtelierManager   2025-12-03 12:30:00
AtelierTailor    2025-12-03 12:30:00
```

### Посмотреть членов каждой роли:

```sql
SELECT 
    r.name AS RoleName,
    m.name AS MemberName,
    m.create_date AS UserCreated
FROM sys.database_role_members rm
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
WHERE r.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY r.name, m.name;
```

**Результат:**
```
RoleName         MemberName    UserCreated
AtelierCashier   cashier       2025-11-29 10:39:28
AtelierCashier   test_cashier  (если утвержден)
AtelierManager   manager       2025-11-29 10:39:28
AtelierTailor    tailor_user   2025-11-29 10:39:28
AtelierTailor    test_tailor   2025-12-03 12:35:00
```

### Посмотреть права роли:

```sql
-- Права на уровне БД (UNMASK, etc.)
SELECT 
    pr.name AS RoleName,
    pe.permission_name AS Permission,
    pe.state_desc AS State
FROM sys.database_permissions pe
JOIN sys.database_principals pr ON pe.grantee_principal_id = pr.principal_id
WHERE pr.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY pr.name, pe.permission_name;

-- Права на объекты (таблицы)
SELECT 
    pr.name AS RoleName,
    OBJECT_NAME(pe.major_id) AS ObjectName,
    pe.permission_name AS Permission
FROM sys.database_permissions pe
JOIN sys.database_principals pr ON pe.grantee_principal_id = pr.principal_id
WHERE pr.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
    AND pe.class = 1  -- Object permissions
ORDER BY pr.name, OBJECT_NAME(pe.major_id), pe.permission_name;
```

---

## 🛠️ УПРАВЛЕНИЕ РОЛЯМИ

### Добавить пользователя в роль:

```sql
ALTER ROLE [AtelierManager] ADD MEMBER [new_username];
```

### Удалить пользователя из роли:

```sql
ALTER ROLE [AtelierManager] DROP MEMBER [username];
```

### Изменить права всей роли:

```sql
-- Пример: разрешить AtelierTailor удалять клиентов
GRANT DELETE ON [dbo].[Customers] TO [AtelierTailor];

-- Теперь ВСЕ пользователи в роли AtelierTailor получили это право!
```

### Отозвать права у роли:

```sql
REVOKE DELETE ON [dbo].[Customers] FROM [AtelierTailor];
```

---

## 🎓 ЛУЧШИЕ ПРАКТИКИ RBAC

### ✅ DO (Делайте):

1. **Используйте роли вместо прав на пользователя**
   ```sql
   -- Правильно
   ALTER ROLE [AtelierTailor] ADD MEMBER [new_user];
   
   -- Неправильно
   GRANT SELECT ON Orders TO [new_user];
   GRANT INSERT ON Orders TO [new_user];
   -- ... много команд
   ```

2. **Создавайте роли по функциям, а не по людям**
   ```sql
   -- Правильно: AtelierManager, AtelierTailor
   -- Неправильно: IvanRole, MariaRole
   ```

3. **Документируйте права каждой роли**
   - Что может делать роль
   - Почему эти права необходимы
   - Кто должен быть в этой роли

4. **Используйте принцип наименьших привилегий**
   - Давайте только те права, которые реально нужны
   - AtelierTailor не нужен доступ к CashRegister
   - AtelierCashier не нужен доступ к OrderFabrics

### ❌ DON'T (Не делайте):

1. **Не давайте всем db_owner**
   ```sql
   -- Плохо
   ALTER ROLE [db_owner] ADD MEMBER [new_user];
   ```

2. **Не создавайте роль для каждого человека**
   - Теряется смысл ролей
   - Сложно управлять

3. **Не забывайте про audit**
   - Логируйте изменения ролей
   - Кто добавил/удалил пользователя из роли

---

## 📈 МОНИТОРИНГ И АУДИТ

### Кто и когда изменял роли:

```sql
-- Используйте Server Audit
SELECT 
    event_time,
    server_principal_name AS WhoChanged,
    database_principal_name AS AffectedUser,
    statement AS WhatHappened
FROM sys.fn_get_audit_file('C:\CP\Audit\Atelier\*.sqlaudit', DEFAULT, DEFAULT)
WHERE statement LIKE '%ALTER ROLE%'
ORDER BY event_time DESC;
```

### История членства в ролях:

Можно создать триггер или использовать Extended Events для отслеживания изменений.

---

## 🆚 СРАВНЕНИЕ: ДО И ПОСЛЕ

### Создание нового пользователя Manager:

**До (без ролей):**
```sql
CREATE LOGIN [new_manager] WITH PASSWORD = N'***';
CREATE USER [new_manager] FOR LOGIN [new_manager];
ALTER ROLE [db_datareader] ADD MEMBER [new_manager];
ALTER ROLE [db_datawriter] ADD MEMBER [new_manager];
GRANT UNMASK TO [new_manager];
-- 5 команд
```

**После (с ролями):**
```sql
CREATE LOGIN [new_manager] WITH PASSWORD = N'***';
CREATE USER [new_manager] FOR LOGIN [new_manager];
ALTER ROLE [AtelierManager] ADD MEMBER [new_manager];
-- 3 команды (+ права уже в роли!)
```

### Изменение прав для всех менеджеров:

**До:** Нужно изменить права каждому пользователю отдельно (10 пользователей = 10 команд)

**После:** Одна команда изменяет права для всех в роли:
```sql
GRANT EXECUTE ON [dbo].[sp_NewProcedure] TO [AtelierManager];
-- Все менеджеры получили право автоматически!
```

---

## ✅ ИТОГ

**Роли БД (RBAC) - это:**
- ✅ Проще в управлении
- ✅ Безопаснее (меньше ошибок)
- ✅ Легче аудитировать
- ✅ Стандартная практика в SQL Server
- ✅ Масштабируемо (100 пользователей = 1 команда на роль)

**Ваше приложение теперь использует RBAC:**
- 3 роли созданы и настроены
- Существующие пользователи переведены на роли
- Новые пользователи автоматически получают роль при утверждении
- Код упрощен в 5-10 раз

**Это значительно повышает профессионализм проекта для защиты!** 🎓🎯
