# Руководство по установке и настройке

## Шаг 1: Установка ODBC Driver для SQL Server

### Проверка установленных драйверов
```powershell
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
```

### Установка ODBC Driver 17
1. Скачайте установщик:
   - [Microsoft ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

2. Запустите установщик и следуйте инструкциям

3. Проверьте установку:
```powershell
odbcconf /q
```

## Шаг 2: Настройка Python окружения

### Установка Python
1. Убедитесь, что Python 3.8+ установлен:
```powershell
python --version
```

2. Если не установлен, скачайте с [python.org](https://www.python.org/downloads/)

### Создание виртуального окружения
```powershell
# Перейдите в директорию проекта
cd c:\AppAppAppAppApp\AtelierApp

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
.\venv\Scripts\Activate.ps1

# Если возникает ошибка выполнения скриптов, выполните:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Установка зависимостей
```powershell
# Убедитесь, что виртуальное окружение активировано
pip install --upgrade pip
pip install -r requirements.txt
```

## Шаг 3: Настройка базы данных

### Создание базы данных
1. Откройте SQL Server Management Studio (SSMS)
2. Подключитесь к серверу
3. Выполните скрипты из файла `DB scripts.txt`:
   - Создание БД Atelier
   - Создание таблиц
   - Создание пользователей и ролей
   - Создание триггеров, процедур, представлений

### Проверка структуры БД
```sql
-- Проверка таблиц
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
ORDER BY TABLE_NAME;

-- Проверка пользователей
SELECT name, type_desc FROM sys.database_principals 
WHERE type IN ('S', 'U') 
ORDER BY name;

-- Проверка триггеров
SELECT name, OBJECT_NAME(parent_id) AS TableName 
FROM sys.triggers 
WHERE parent_class = 1
ORDER BY name;
```

## Шаг 4: Создание необходимых директорий

Приложение использует следующие директории для хранения файлов:

```powershell
# Создайте директории для аудита, бэкапов и событий
New-Item -ItemType Directory -Force -Path "C:\CP\Audits"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Full"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Diff"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Log"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Partial"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Certificates"
New-Item -ItemType Directory -Force -Path "C:\CP\ExtendedEvents"
```

## Шаг 5: Настройка файла конфигурации

1. Скопируйте файл примера:
```powershell
Copy-Item .env.example .env
```

2. Отредактируйте `.env` в текстовом редакторе:
```ini
# Укажите имя вашего SQL Server
DB_SERVER=localhost
# или DB_SERVER=.\SQLEXPRESS
# или DB_SERVER=YOUR_SERVER_NAME

DB_NAME=Atelier
DB_DRIVER=ODBC Driver 17 for SQL Server

# Учетные данные из скриптов создания БД
ADMIN_USER=atelier_admin
ADMIN_PASSWORD=Admin@2025!Strong

MANAGER_USER=manager
MANAGER_PASSWORD=Manager@2025!Pass

TAILOR_USER=tailor_user
TAILOR_PASSWORD=Tailor@2025!Pass

CASHIER_USER=cashier
CASHIER_PASSWORD=Cashier@2025!Pass
```

## Шаг 6: Тестирование подключения

### Тест через Python скрипт
```powershell
python database.py
```

Вы должны увидеть:
```
Testing Database Connections...

Testing ADMIN: Database Administrator (full access)
✓ Connection successful
  Database: Atelier, User: atelier_admin

Testing MANAGER: Manager (read/write access)
✓ Connection successful
  Database: Atelier, User: manager
...
```

## Шаг 7: Запуск приложения

```powershell
python main.py
```

### Первый запуск
1. Выберите роль (рекомендуется начать с Admin)
2. Проверьте подключение (опция 11 в меню)
3. Протестируйте основные функции:
   - DDM (опция 2) - демонстрация маскировки
   - Backup (опция 4) - статус резервных копий
   - TDE (опция 5) - статус шифрования

## Устранение типичных проблем

### Проблема: "pyodbc.InterfaceError: ('IM002'..."
**Решение:** ODBC драйвер не установлен или имеет неправильное название
```powershell
# Проверьте доступные драйверы
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL*"}

# Обновите DB_DRIVER в .env файле
```

### Проблема: "Login failed for user"
**Решение:** Неправильные учетные данные или пользователь не создан
```sql
-- Проверьте в SSMS:
SELECT name FROM sys.server_principals WHERE name = 'atelier_admin';
SELECT name FROM sys.database_principals WHERE name = 'atelier_admin';
```

### Проблема: "Database 'Atelier' does not exist"
**Решение:** База данных не создана
```sql
-- Создайте БД через SSMS или выполните скрипты из DB scripts.txt
CREATE DATABASE Atelier;
```

### Проблема: SQL Server Agent Jobs не работают
**Решение:** SQL Server Agent должен быть запущен
```powershell
# Проверьте статус в SQL Server Configuration Manager
# Или через SSMS: Object Explorer -> SQL Server Agent -> Start
```

## Дополнительные настройки

### Включение Query Store (для Extended Events)
```sql
ALTER DATABASE Atelier SET QUERY_STORE = ON;
ALTER DATABASE Atelier SET QUERY_STORE (OPERATION_MODE = READ_WRITE);
```

### Включение Audit
```sql
-- Выполните скрипты аудита из DB scripts.txt
-- Audit должен быть создан и запущен
```

### Настройка TDE
```sql
-- Выполните скрипты TDE из DB scripts.txt
-- Убедитесь, что сертификат создан и сделан бэкап
```

## Проверка функциональности

### Чек-лист перед демонстрацией:
- [ ] Все таблицы созданы
- [ ] Все пользователи созданы и имеют права
- [ ] DDM настроен (маскировка Phone, Address, CustomerName)
- [ ] TDE включен (encryption_state = 3)
- [ ] Backup Jobs созданы и работают
- [ ] Триггеры активны
- [ ] Процедуры созданы
- [ ] Представления доступны
- [ ] Функции работают
- [ ] Audit включен (опционально)
- [ ] Extended Events настроены (опционально)

### Быстрая проверка всех компонентов:
```sql
-- Таблицы
SELECT COUNT(*) FROM sys.tables;  -- Должно быть ~15

-- Пользователи
SELECT COUNT(*) FROM sys.database_principals 
WHERE type IN ('S', 'U');  -- Должно быть 4+

-- Триггеры
SELECT COUNT(*) FROM sys.triggers WHERE parent_class = 1;  -- Должно быть 6

-- Процедуры
SELECT COUNT(*) FROM sys.procedures;  -- Должно быть 6

-- Представления
SELECT COUNT(*) FROM sys.views WHERE name LIKE 'vw_%';  -- Должно быть 6

-- Функции
SELECT COUNT(*) FROM sys.objects 
WHERE type IN ('FN', 'IF', 'TF') AND name LIKE 'fn_%';  -- Должно быть 4
```

## Готово к использованию!

Теперь вы можете запустить приложение и продемонстрировать все функции:

```powershell
python main.py
```

---

**Поддержка:** Если возникают проблемы, проверьте:
1. Логи SQL Server
2. Права доступа пользователей
3. Правильность путей к файлам
4. Статус SQL Server Agent
