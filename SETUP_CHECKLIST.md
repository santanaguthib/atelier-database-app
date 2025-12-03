# ===================================================================
# ATELIER DATABASE MANAGEMENT SYSTEM - SETUP CHECKLIST
# ===================================================================

## ШАГ 1: ПРОВЕРКА ПРЕДВАРИТЕЛЬНЫХ ТРЕБОВАНИЙ

### SQL Server
□ SQL Server 2019+ установлен и запущен
□ SQL Server Management Studio (SSMS) установлен
□ База данных Atelier создана
□ Все пользователи созданы (atelier_admin, manager, tailor_user, cashier)
□ Все таблицы, триггеры, процедуры, представления созданы

### Python
□ Python 3.8+ установлен
□ pip обновлен до последней версии

### ODBC Driver
□ ODBC Driver 17 for SQL Server установлен

## ШАГ 2: СОЗДАНИЕ ДИРЕКТОРИЙ

Выполните в PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "C:\CP\Audits"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Full"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Diff"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Log"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Atelier\Partial"
New-Item -ItemType Directory -Force -Path "C:\CP\Backups\Certificates"
New-Item -ItemType Directory -Force -Path "C:\CP\ExtendedEvents"
```

## ШАГ 3: УСТАНОВКА ПРИЛОЖЕНИЯ

```powershell
# Перейдите в директорию проекта
cd c:\AppAppAppAppApp\AtelierApp

# Создайте виртуальное окружение (опционально, но рекомендуется)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Если возникает ошибка политики выполнения:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

## ШАГ 4: НАСТРОЙКА ПОДКЛЮЧЕНИЯ

```powershell
# Скопируйте файл примера конфигурации
Copy-Item .env.example .env

# Отредактируйте .env в Notepad
notepad .env
```

Измените следующие параметры:
- DB_SERVER - имя вашего SQL Server (например: localhost, .\SQLEXPRESS)
- Пароли пользователей (если изменяли при создании)

## ШАГ 5: ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ

```powershell
# Протестируйте подключение ко всем пользователям
python database.py
```

Ожидаемый результат:
```
Testing ADMIN: Database Administrator (full access)
✓ Connection successful
  Database: Atelier, User: atelier_admin

Testing MANAGER: Manager (read/write access)
✓ Connection successful
...
```

## ШАГ 6: ЗАПУСК ПРИЛОЖЕНИЯ

```powershell
python main.py
```

## ШАГ 7: ДЕМОНСТРАЦИЯ ФУНКЦИЙ

### Тест 1: DDM (Dynamic Data Masking)
1. При запуске выберите роль: 1 (Admin)
2. В главном меню выберите: 2 (DDM)
3. Выберите: 4 (Side-by-Side Comparison)
4. Наблюдайте разницу между Admin и Cashier

### Тест 2: TDE (Transparent Data Encryption)
1. В главном меню выберите: 5 (TDE)
2. Выберите: 1 (View Database Encryption Status)
3. Проверьте статус шифрования

### Тест 3: Backup (Резервное копирование)
1. В главном меню выберите: 4 (Backup)
2. Выберите: 1 (View SQL Agent Jobs Status)
3. Просмотрите настроенные задания

### Тест 4: Triggers (Триггеры)
1. В главном меню выберите: 7 (Triggers)
2. Выберите: 1 (View All Triggers)
3. Просмотрите список триггеров

### Тест 5: Filegroups (Файловые группы)
1. В главном меню выберите: 6 (Filegroups)
2. Выберите: 6 (View Distribution Summary)
3. Просмотрите распределение данных

## УСТРАНЕНИЕ ПРОБЛЕМ

### Ошибка: "pyodbc.InterfaceError: ('IM002'..."
**Причина:** ODBC драйвер не установлен
**Решение:** Установите ODBC Driver 17 for SQL Server
URL: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Ошибка: "Login failed for user"
**Причина:** Неправильные учетные данные
**Решение:** 
1. Проверьте пароли в .env файле
2. Убедитесь, что пользователи созданы в SQL Server

### Ошибка: "Database 'Atelier' does not exist"
**Причина:** База данных не создана
**Решение:** Выполните SQL скрипты из файла "DB scripts.txt"

### Ошибка: "ModuleNotFoundError"
**Причина:** Зависимости не установлены
**Решение:** 
```powershell
pip install -r requirements.txt
```

## ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ДЕМОНСТРАЦИЕЙ

□ Приложение запускается без ошибок
□ Можно войти под всеми ролями (admin, manager, tailor, cashier)
□ DDM демонстрирует разницу между ролями
□ TDE показывает статус шифрования
□ Backup Jobs видны и работают
□ Триггеры отображаются
□ Процедуры доступны
□ Представления работают
□ Функции выполняются

## ПОЛЕЗНЫЕ КОМАНДЫ

### Проверка версии Python
```powershell
python --version
```

### Проверка установленных пакетов
```powershell
pip list
```

### Переустановка зависимостей
```powershell
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Проверка ODBC драйверов
```powershell
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL*"}
```

### Деактивация виртуального окружения
```powershell
deactivate
```

## КОНТАКТЫ И ПОДДЕРЖКА

Если возникают проблемы:
1. Проверьте логи SQL Server
2. Убедитесь, что все скрипты из DB scripts.txt выполнены
3. Проверьте права доступа пользователей в SQL Server
4. Убедитесь, что SQL Server Agent запущен (для Backup Jobs)

---

ГОТОВО! Приложение настроено и готово к демонстрации!

Для запуска: python main.py
