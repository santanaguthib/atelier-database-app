# 🎓 ATELIER DATABASE - СИСТЕМА УПРАВЛЕНИЯ БЕЗОПАСНОСТЬЮ

## 📋 Обзор проекта

Комплексное приложение на Python для демонстрации **11 функций безопасности** SQL Server в базе данных Atelier (Ателье).

---

## ✨ РЕАЛИЗОВАННЫЕ ФУНКЦИИ БЕЗОПАСНОСТИ

| № | Функция | Описание | Файл модуля |
|---|---------|----------|-------------|
| 1 | **Audit** | Мониторинг событий безопасности | `modules/audit.py` |
| 2 | **DDM** | Динамическое маскирование данных | `modules/ddm.py` |
| 3 | **Extended Events** | Отслеживание медленных запросов и ошибок входа | `modules/extended_events.py` |
| 4 | **Backup** | Автоматизированная система резервного копирования | `modules/backup.py` |
| 5 | **TDE** | Прозрачное шифрование данных | `modules/tde.py` |
| 6 | **Filegroups** | Распределение данных по файловым группам | `modules/filegroups.py` |
| 7 | **Triggers** | Автоматические триггеры для бизнес-логики | `modules/triggers.py` |
| 8 | **Procedures** | Хранимые процедуры для операций | `modules/procedures.py` |
| 9 | **Views** | Представления для отчетности | `modules/views.py` |
| 10 | **Functions** | Пользовательские функции | `modules/functions.py` |
| 11 | **User Management** | Система регистрации и управления пользователями ⭐ **НОВОЕ** | `modules/user_management.py` |

---

## 🚀 БЫСТРЫЙ СТАРТ

### Предварительные требования
- Python 3.14+
- SQL Server 2025 (или 2019/2022)
- ODBC Driver 17 for SQL Server
- База данных Atelier (см. SQL скрипты)

### Установка

```bash
# 1. Клонируйте репозиторий
cd C:\AppAppAppAppApp\AtelierApp

# 2. Установите зависимости
pip install pyodbc tabulate colorama

# 3. Выполните SQL скрипты в SSMS (по порядку)
.\SQL_Scripts\Atelier.sql              # Основная структура БД
.\SQL_Scripts\Step_1.sql               # Backup система
.\SQL_Scripts\Step_2.sql               # Filegroups
.\SQL_Scripts\Step_3.sql               # Triggers, Views, Procedures, Functions
.\SQL_Scripts\Step_4.sql               # DDM, TDE
.\SQL_Scripts\Step_5.sql               # Audit, Extended Events
.\SQL_Scripts\Step_6_UserRegistration.sql  # User Management ⭐

# 4. Настройте таблицу регистрации
python setup_registration.py

# 5. Запустите приложение
python main.py
```

---

## 👥 ПОЛЬЗОВАТЕЛИ И РОЛИ

### Существующие учетные записи:

| Пользователь | Пароль | Роль | Права доступа |
|--------------|--------|------|---------------|
| `atelier_admin` | `Admin@2025!Strong` | Администратор | Полный доступ ко всем функциям |
| `manager` | `Manager@2025!Pass` | Менеджер | Чтение/запись, видит не маскированные данные |
| `tailor_user` | `Tailor@2025!Pass` | Портной | Работа с заказами, видит маскированные данные |
| `cashier` | `Cashier@2025!Pass` | Кассир | Работа с кассой, видит маскированные данные |

### Регистрация новых пользователей:

**Workflow:**
1. Пользователь заполняет форму регистрации
2. Заявка сохраняется со статусом `Pending`
3. Администратор утверждает/отклоняет заявку
4. При утверждении автоматически создается SQL логин и пользователь БД

**Доступные роли для регистрации:**
- **Manager** - полный доступ к данным, видит не маскированную информацию
- **Tailor** - работа с производственными заказами
- **Cashier** - работа с кассовыми операциями

---

## 📁 СТРУКТУРА ПРОЕКТА

```
C:\AppAppAppAppApp\
│
├── AtelierApp\                    # Основное приложение
│   ├── main.py                    # Точка входа (270+ строк)
│   ├── database.py                # Подключение к БД (133 строки)
│   ├── config.py                  # Конфигурация (54 строки)
│   │
│   ├── modules\                   # Модули функций безопасности
│   │   ├── audit.py              # 220 строк
│   │   ├── ddm.py                # 185 строк
│   │   ├── extended_events.py    # 217 строк
│   │   ├── backup.py             # 266 строк
│   │   ├── tde.py                # 190 строк
│   │   ├── filegroups.py         # 228 строк (исправлены RowCount ошибки)
│   │   ├── triggers.py           # 290 строк (исправлены OrderLogs колонки)
│   │   ├── procedures.py         # 485 строк (исправлены даты)
│   │   ├── views.py              # 279 строк (исправлены все колонки)
│   │   ├── functions.py          # 266 строк (исправлен StatusName)
│   │   └── user_management.py    # 540 строк ⭐ НОВОЕ
│   │
│   ├── setup_registration.py     # Установка таблицы регистрации
│   └── test_registration.py      # Тестовые данные
│
├── SQL_Scripts\                   # SQL скрипты
│   ├── Atelier.sql               # Структура БД, пользователи
│   ├── Step_1.sql                # Backup стратегия
│   ├── Step_2.sql                # Filegroups
│   ├── Step_3.sql                # Triggers, Views, Procedures, Functions
│   ├── Step_4.sql                # DDM, TDE
│   ├── Step_5.sql                # Audit, Extended Events
│   └── Step_6_UserRegistration.sql  # User Management ⭐ НОВОЕ
│
├── REGISTRATION_GUIDE.md          # Полная инструкция (400+ строк)
├── DEMO_REGISTRATION.md           # Быстрая демонстрация
└── README.md                      # Этот файл
```

**Всего кода:** ~4500+ строк Python + ~800 строк SQL

---

## 🎯 ФУНКЦИИ ПО КАТЕГОРИЯМ

### 🔒 Безопасность данных
- **Audit** - Файловый аудит с спецификациями сервера и БД
- **DDM** - Маскирование ФИО, телефонов, адресов
- **TDE** - AES-256 шифрование, сертификат до 2030 года
- **User Management** ⭐ - Централизованное управление доступом

### 📊 Мониторинг
- **Extended Events** - Медленные запросы (>2 сек), неудачные входы
- **Backup** - 3 SQL Agent jobs (Full/Differential/Log)

### 🏗️ Архитектура
- **Filegroups** - 4 группы (PRIMARY, ORDERS_FG, LOGS_FG, INDEXES_FG)
- **Views** - 6 представлений для отчетности
- **Functions** - 4 пользовательских функции

### 💼 Бизнес-логика
- **Triggers** - 6 триггеров для автоматизации
- **Procedures** - 6 процедур для операций

---

## 🆕 НОВОЕ: USER MANAGEMENT

### Возможности модуля:

**Для пользователей:**
1. Регистрация через форму в приложении
2. Выбор роли (manager/tailor/cashier)
3. Указание обоснования необходимости доступа

**Для администратора (меню 11):**
1. ✅ Просмотр заявок на регистрацию
2. ✅ Утверждение заявок → автоматическое создание SQL логина
3. ✅ Отклонение заявок с указанием причины
4. ✅ Просмотр всех пользователей БД
5. ✅ Деактивация учетных записей (временно)
6. ✅ Активация учетных записей
7. ✅ Полное удаление пользователей
8. ✅ Просмотр активности пользователей из логов

### Таблица UserRegistrationRequests:

```sql
RequestID          INT PRIMARY KEY
Username           NVARCHAR(128) UNIQUE
HashedPassword     NVARCHAR(128)
FullName           NVARCHAR(200)
Email              NVARCHAR(200)
RequestedRole      NVARCHAR(50)    -- manager/tailor_user/cashier
Justification      NVARCHAR(500)
RequestDate        DATETIME
Status             NVARCHAR(20)    -- Pending/Approved/Rejected
ProcessedDate      DATETIME
ProcessedBy        NVARCHAR(128)
RejectionReason    NVARCHAR(500)
```

### Автоматические действия при утверждении:

```sql
-- 1. Создание SQL Server Login
CREATE LOGIN [username] WITH PASSWORD = N'***'

-- 2. Создание Database User
CREATE USER [username] FOR LOGIN [username]

-- 3. Назначение прав согласно роли
-- Manager:
ALTER ROLE db_datareader ADD MEMBER [username]
ALTER ROLE db_datawriter ADD MEMBER [username]
GRANT UNMASK TO [username]

-- Tailor:
ALTER ROLE db_datareader ADD MEMBER [username]
GRANT INSERT, UPDATE, DELETE ON Orders TO [username]
GRANT INSERT, UPDATE, DELETE ON OrderCosts TO [username]

-- Cashier:
ALTER ROLE db_datareader ADD MEMBER [username]
GRANT INSERT, UPDATE, DELETE ON CashRegister TO [username]

-- 4. Обновление статуса заявки
UPDATE UserRegistrationRequests
SET Status = 'Approved', ProcessedDate = GETDATE(), ProcessedBy = CURRENT_USER
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Быстрый тест всей системы:

```bash
# 1. Создайте тестовые заявки
python test_registration.py

# 2. Запустите приложение
python main.py

# 3. Войдите как администратор
Username: atelier_admin
Password: Admin@2025!Strong

# 4. Меню 11 → User Management
# 5. Просмотр заявок (опция 1)
# 6. Утверждение заявки (опция 2)
# 7. Выход и вход новым пользователем
```

### Проверка в SQL Server:

```sql
-- Проверка созданного логина
SELECT name, create_date, is_disabled 
FROM sys.server_principals 
WHERE type = 'S' AND name NOT LIKE '##%'

-- Проверка пользователя БД
SELECT name, create_date 
FROM sys.database_principals 
WHERE type = 'S'

-- Статистика заявок
SELECT 
    Status,
    COUNT(*) AS Total
FROM UserRegistrationRequests
GROUP BY Status
```

---

## 📚 ДОКУМЕНТАЦИЯ

| Файл | Описание |
|------|----------|
| `REGISTRATION_GUIDE.md` | Полная инструкция по User Management (400+ строк) |
| `DEMO_REGISTRATION.md` | Быстрая демонстрация для защиты проекта |
| `README.md` | Общий обзор (этот файл) |

---

## ✅ СТАТУС ПРОЕКТА

### Все функции протестированы и работают:

- [x] Audit - операционный
- [x] DDM - маскирование работает
- [x] Extended Events - 2 сессии активны
- [x] Backup - 3 SQL Agent jobs запланированы
- [x] TDE - база зашифрована AES-256
- [x] Filegroups - 4 группы настроены
- [x] Triggers - все 6 триггеров активны
- [x] Procedures - все 6 процедур рабочие
- [x] Views - все 6 представлений исправлены
- [x] Functions - все 4 функции работают
- [x] User Management - полностью функциональный ⭐

### Исправленные баги:

✅ **filegroups.py** - ошибки RowCount (зарезервированное слово)  
✅ **triggers.py** - колонки OrderLogs (OperationType, OperationDate)  
✅ **views.py** - все 6 представлений (индексы массива, названия колонок)  
✅ **functions.py** - StatusName вместо OrderStatus  
✅ **procedures.py** - обработка дат (CAST(GETDATE() AS DATE))  

---

## 🎓 ДЛЯ ЗАЩИТЫ КУРСОВОГО ПРОЕКТА

### Ключевые моменты для демонстрации:

1. **11 функций безопасности** - полная реализация
2. **4500+ строк кода** - серьезный объем работы
3. **Реальный workflow** - система регистрации с утверждением
4. **Автоматизация** - создание пользователей без ручного SQL
5. **Безопасность** - валидация, аудит, защита системных учетных записей
6. **Интеграция** - все модули работают вместе

### Преимущества проекта:

✅ **Практичность** - реальный сценарий использования  
✅ **Полнота** - все аспекты безопасности SQL Server  
✅ **Качество** - обработка ошибок, документация  
✅ **Расширяемость** - легко добавить новые функции  
✅ **Масштабируемость** - готов к реальному использованию  

---

## 🔧 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

**Технологии:**
- Python 3.14
- pyodbc 5.3.0
- SQL Server 2025 (совместимо с 2019/2022)
- ODBC Driver 17 for SQL Server
- Windows PowerShell 5.1

**Конфигурация SQL Server:**
- Режим восстановления: Full
- TDE: Включен (AES-256)
- SQL Server Authentication
- Файловые группы: 4 (PRIMARY, ORDERS_FG, LOGS_FG, INDEXES_FG)

**Пути:**
- Аудит: `C:\CP\Audit\Atelier\`
- Бэкапы: `C:\CP\Backups\Atelier\{Full|Diff|Log}\`

---

## 📞 КОНТАКТЫ

**Проект:** Система управления безопасностью БД Atelier  
**Дата:** Декабрь 2025  
**Статус:** ✅ Готов к защите  

---

## 🌟 ИТОГ

**Комплексное приложение с 11 функциями безопасности SQL Server**

- ✅ Полная документация
- ✅ Все функции протестированы
- ✅ Реальные сценарии использования
- ✅ Готово к демонстрации

**Можно защищать курсовой проект!** 🎓🎯
