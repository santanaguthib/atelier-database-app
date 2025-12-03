# СИСТЕМА РЕГИСТРАЦИИ И УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ

## 📋 Обзор

Добавлена полная система управления пользователями с workflow утверждения администратором:
- ✅ Регистрация новых пользователей
- ✅ Система заявок с утверждением/отклонением
- ✅ Автоматическое создание SQL Server логинов и пользователей БД
- ✅ Управление учетными записями (деактивация, удаление)
- ✅ Аудит активности пользователей

---

## 🚀 Установка

### 1. Выполните SQL скрипт создания таблицы

```sql
-- Выполните в SSMS:
.\SQL_Scripts\Step_6_UserRegistration.sql
```

Этот скрипт создаст:
- Таблицу `UserRegistrationRequests` для хранения заявок
- Индекс для оптимизации запросов по статусу
- Права доступа для роли manager

### 2. Проверьте работу приложения

Модуль автоматически интегрирован в главное меню приложения.

---

## 👤 Процесс регистрации пользователя

### Шаг 1: Запуск приложения

```bash
cd c:\AppAppAppAppApp\AtelierApp
python main.py
```

### Шаг 2: Выбор опции регистрации

При запуске приложения:
```
DATABASE LOGIN - SQL Server Authentication
================================================================================

Options:
  1. Login with existing account
  2. Register new account  ← Выберите это
  0. Exit
```

### Шаг 3: Заполнение формы регистрации

```
USER REGISTRATION - Atelier Database
================================================================================

Username (login): ivan_petrov
Password: ********
Confirm password: ********
Full Name: Иван Петров
Email: ivan.petrov@atelier.com

Select desired role:
1. Manager - Read/Write access to all data
2. Tailor - Work with orders and production
3. Cashier - Process payments

Choice (1-3): 2

Why do you need access? (brief justification): 
Требуется доступ для работы с производственными заказами
```

### Шаг 4: Подтверждение

```
✓ Registration request submitted successfully!
✓ An administrator will review your request.
✓ You will be able to login once approved.
```

Заявка сохранена в БД со статусом **Pending**.

---

## 👨‍💼 Процесс утверждения администратором

### Шаг 1: Вход как администратор

Войдите в приложение с учетной записью `atelier_admin`.

### Шаг 2: Открытие меню управления пользователями

```
MAIN MENU - Database Security & Functionality Features
...
Administration:
 11. User Management - Registration & Approvals  ← Выберите
```

### Шаг 3: Просмотр заявок

```
USER MANAGEMENT - Registration & Administration
================================================================================
1. View Pending Registration Requests  ← Выберите
2. Approve Registration Request
3. Reject Registration Request
...
```

Вы увидите все заявки:
```
┌───────────┬──────────────┬──────────────┬─────────────────┬──────────────┐
│ RequestID │ Username     │ FullName     │ RequestedRole   │ RequestDate  │
├───────────┼──────────────┼──────────────┼─────────────────┼──────────────┤
│         1 │ ivan_petrov  │ Иван Петров  │ tailor_user     │ 2025-12-03   │
└───────────┴──────────────┴──────────────┴─────────────────┴──────────────┘
```

### Шаг 4: Утверждение заявки

```
2. Approve Registration Request  ← Выберите

Enter RequestID to approve (0 to cancel): 1

Request Details:
Username: ivan_petrov
Full Name: Иван Петров
Email: ivan.petrov@atelier.com
Requested Role: tailor_user

Approve this request? (yes/no): yes

Creating SQL Server login...
Creating database user...

✓ Registration approved successfully!
✓ SQL Server login created: ivan_petrov
✓ Database user created with role: tailor_user
```

### Что происходит при утверждении:

1. **Создается SQL Server Login:**
   ```sql
   CREATE LOGIN [ivan_petrov] WITH PASSWORD = N'********'
   ```

2. **Создается Database User:**
   ```sql
   CREATE USER [ivan_petrov] FOR LOGIN [ivan_petrov]
   ```

3. **Назначаются права согласно роли:**
   - **manager**: `db_datareader`, `db_datawriter`, `GRANT UNMASK`
   - **tailor_user**: `db_datareader`, права на `INSERT/UPDATE/DELETE` в таблицы заказов
   - **cashier**: `db_datareader`, права на `INSERT/UPDATE/DELETE` в `CashRegister`

4. **Обновляется статус заявки:**
   ```sql
   UPDATE UserRegistrationRequests
   SET Status = 'Approved', ProcessedDate = GETDATE(), ProcessedBy = CURRENT_USER
   ```

---

## ❌ Отклонение заявки

```
3. Reject Registration Request  ← Выберите

Enter RequestID to reject (0 to cancel): 2
Rejection reason: Недостаточное обоснование необходимости доступа

Reject this request? (yes/no): yes

✓ Request rejected.
```

---

## 🔧 Дополнительные функции администратора

### Просмотр всех пользователей
```
4. View All Users
```
Показывает всех пользователей БД с датами создания и статусами.

### Деактивация учетной записи
```
5. Disable User Account
```
Временно отключает возможность входа (без удаления данных):
```sql
ALTER LOGIN [username] DISABLE
```

### Активация учетной записи
```
6. Enable User Account
```
Восстанавливает доступ:
```sql
ALTER LOGIN [username] ENABLE
```

### Полное удаление пользователя
```
7. Delete User Account (PERMANENT)
```
⚠️ **ОСТОРОЖНО!** Необратимо удаляет пользователя:
```
Type 'DELETE username' to confirm: DELETE ivan_petrov

✓ User 'ivan_petrov' deleted permanently.
```

### Просмотр активности пользователей
```
8. View User Activity Log
```
Показывает статистику из таблицы `OrderLogs`:
- Количество операций каждого пользователя
- Даты первой и последней активности

---

## 🗂️ Структура таблицы UserRegistrationRequests

```sql
CREATE TABLE UserRegistrationRequests (
    RequestID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(128) NOT NULL UNIQUE,
    HashedPassword NVARCHAR(128) NOT NULL,
    FullName NVARCHAR(200) NOT NULL,
    Email NVARCHAR(200) NOT NULL,
    RequestedRole NVARCHAR(50) CHECK (RequestedRole IN ('manager', 'tailor_user', 'cashier')),
    Justification NVARCHAR(500) NULL,
    RequestDate DATETIME NOT NULL DEFAULT GETDATE(),
    Status NVARCHAR(20) CHECK (Status IN ('Pending', 'Approved', 'Rejected')),
    ProcessedDate DATETIME NULL,
    ProcessedBy NVARCHAR(128) NULL,
    RejectionReason NVARCHAR(500) NULL
)
```

### Статусы заявок:
- **Pending** - Ожидает рассмотрения администратором
- **Approved** - Утверждена, пользователь создан
- **Rejected** - Отклонена администратором

---

## 📊 Примеры запросов

### Посмотреть все заявки в ожидании
```sql
SELECT RequestID, Username, FullName, RequestedRole, RequestDate
FROM UserRegistrationRequests
WHERE Status = 'Pending'
ORDER BY RequestDate ASC
```

### История обработанных заявок
```sql
SELECT 
    Username,
    Status,
    ProcessedDate,
    ProcessedBy,
    RejectionReason
FROM UserRegistrationRequests
WHERE Status IN ('Approved', 'Rejected')
ORDER BY ProcessedDate DESC
```

### Статистика по ролям
```sql
SELECT 
    RequestedRole,
    COUNT(*) AS TotalRequests,
    SUM(CASE WHEN Status = 'Approved' THEN 1 ELSE 0 END) AS Approved,
    SUM(CASE WHEN Status = 'Rejected' THEN 1 ELSE 0 END) AS Rejected,
    SUM(CASE WHEN Status = 'Pending' THEN 1 ELSE 0 END) AS Pending
FROM UserRegistrationRequests
GROUP BY RequestedRole
```

---

## 🔐 Безопасность

### Преимущества реализованной системы:

1. **Централизованный контроль доступа**
   - Все новые пользователи проходят через администратора
   - Невозможно самостоятельно создать учетную запись

2. **Аудит всех действий**
   - Записывается кто и когда обработал заявку
   - Причины отклонения сохраняются

3. **Гибкое управление**
   - Временная деактивация без потери данных
   - Возможность восстановления доступа

4. **Разделение прав по ролям**
   - Автоматическое назначение прав согласно выбранной роли
   - Принцип наименьших привилегий (least privilege)

### ⚠️ Важные замечания:

- **Пароли не шифруются** в таблице заявок (для демонстрации)
  - В production используйте `HASHBYTES('SHA2_256', password)`
  
- **Защита от SQL-инъекций**
  - Используются параметризованные запросы через pyodbc
  
- **Системные учетные записи защищены**
  - Невозможно удалить `atelier_admin`, `sa`, `dbo`, `manager`

---

## 🧪 Тестирование системы

### Тест 1: Регистрация нового пользователя
1. Запустите приложение
2. Выберите "2. Register new account"
3. Заполните форму
4. Проверьте в БД:
   ```sql
   SELECT * FROM UserRegistrationRequests WHERE Status = 'Pending'
   ```

### Тест 2: Утверждение заявки
1. Войдите как `atelier_admin`
2. Меню "11. User Management" → "2. Approve Registration Request"
3. Проверьте создание логина:
   ```sql
   SELECT name, create_date FROM sys.server_principals WHERE name = 'ivan_petrov'
   ```
4. Проверьте создание пользователя:
   ```sql
   SELECT name, create_date FROM sys.database_principals WHERE name = 'ivan_petrov'
   ```

### Тест 3: Вход нового пользователя
1. Перезапустите приложение
2. Войдите с новыми учетными данными
3. Проверьте доступные функции согласно роли

### Тест 4: Отклонение заявки
1. Создайте еще одну заявку
2. Отклоните её через админское меню
3. Проверьте сохранение причины отклонения:
   ```sql
   SELECT Username, RejectionReason FROM UserRegistrationRequests WHERE Status = 'Rejected'
   ```

---

## 📈 Интеграция с существующими функциями

Новая система полностью интегрирована:

- **Главное меню**: Опция 11 для админов (User Management)
- **Аудит**: Все действия логируются через `CURRENT_USER`
- **Роли**: Автоматическое назначение прав согласно существующей системе ролей
- **DDM**: Новые пользователи автоматически получают маскирование данных (кроме manager)

---

## ✅ Преимущества для курсового проекта

1. **Демонстрация управления доступом**
   - Реальный workflow утверждения
   - Безопасное создание пользователей

2. **Расширенная функциональность**
   - 11-я функция безопасности (дополнение к 10 базовым)
   - Комплексная система администрирования

3. **Практическое применение**
   - Реальный сценарий использования
   - Интеграция с существующей системой безопасности

---

## 🎯 Итог

Теперь ваше приложение имеет полноценную систему управления пользователями:

✅ Пользователи регистрируются самостоятельно  
✅ Администратор контролирует доступ  
✅ Автоматическое создание SQL Server логинов  
✅ Гибкое управление учетными записями  
✅ Полный аудит всех действий  

Это значительно повышает практическую ценность проекта и демонстрирует комплексный подход к безопасности БД! 🎓
