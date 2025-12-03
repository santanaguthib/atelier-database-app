# Atelier Database Management System

Комплексное Python-приложение для демонстрации возможностей безопасности и функциональности базы данных Atelier (SQL Server).

## 🎯 Основные возможности

### Безопасность
- **Audit** - Просмотр событий безопасности и аудита
- **DDM (Dynamic Data Masking)** - Наглядная демонстрация маскировки данных между ролями
- **Extended Events** - Мониторинг медленных запросов и неудачных попыток входа
- **Backup** - Автоматизация резервного копирования через SQL Agent Jobs
- **TDE (Transparent Data Encryption)** - Статус шифрования базы данных

### Архитектура
- **Filegroups** - Распределение данных по файловым группам

### Бизнес-логика
- **Triggers** - Автоматизация бизнес-правил
- **Stored Procedures** - Бизнес-операции
- **Views** - Отчеты и представления данных
- **Functions** - Вспомогательные вычисления

## 📋 Требования

### Система
- Windows 10/11
- Python 3.8+
- SQL Server 2019+
- ODBC Driver 17 for SQL Server

### База данных
- База данных **Atelier** должна быть создана и настроена
- Пользователи: `atelier_admin`, `manager`, `tailor_user`, `cashier`
- Все триггеры, процедуры, представления и функции должны быть созданы

## 🚀 Установка

### 1. Клонирование/Копирование проекта
```powershell
cd c:\AppAppAppAppApp\AtelierApp
```

### 2. Создание виртуального окружения (рекомендуется)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей
```powershell
pip install -r requirements.txt
```

### 4. Настройка подключения к БД

Скопируйте файл `.env.example` в `.env`:
```powershell
Copy-Item .env.example .env
```

Отредактируйте `.env` и укажите правильные параметры подключения:
```ini
DB_SERVER=localhost
DB_NAME=Atelier
DB_DRIVER=ODBC Driver 17 for SQL Server

ADMIN_USER=atelier_admin
ADMIN_PASSWORD=Admin@2025!Strong

MANAGER_USER=manager
MANAGER_PASSWORD=Manager@2025!Pass

TAILOR_USER=tailor_user
TAILOR_PASSWORD=Tailor@2025!Pass

CASHIER_USER=cashier
CASHIER_PASSWORD=Cashier@2025!Pass
```

## 📖 Использование

### Запуск приложения
```powershell
python main.py
```

### Выбор роли
При запуске приложение предложит выбрать роль:
1. **Admin** - Полный доступ, видит немаскированные данные
2. **Manager** - Полный доступ к данным
3. **Tailor** - Ограниченный доступ, видит маскированные данные
4. **Cashier** - Доступ к кассе, видит маскированные данные

### Навигация
Используйте числовое меню для навигации по функциям. Каждый модуль содержит подменю с детальными опциями.

## 📂 Структура проекта

```
AtelierApp/
│
├── main.py                 # Главное приложение
├── config.py               # Конфигурация подключения
├── database.py             # Класс для работы с БД
├── requirements.txt        # Зависимости Python
├── .env.example           # Пример конфигурации
├── .env                   # Ваша конфигурация (не коммитится)
├── README.md              # Этот файл
│
└── modules/               # Модули функциональности
    ├── __init__.py
    ├── audit.py           # Аудит безопасности
    ├── ddm.py             # Dynamic Data Masking
    ├── extended_events.py # Extended Events
    ├── backup.py          # Резервное копирование
    ├── tde.py             # Transparent Data Encryption
    ├── filegroups.py      # Файловые группы
    ├── triggers.py        # Триггеры
    ├── procedures.py      # Хранимые процедуры
    ├── views.py           # Представления
    └── functions.py       # Функции
```

## 🔐 Роли и права доступа

### Admin (atelier_admin)
- Полный доступ ко всем данным
- Видит немаскированные личные данные клиентов
- Может выполнять все операции

### Manager
- Полный доступ к чтению и записи данных
- Видит немаскированные данные (UNMASK permission)
- Может управлять заказами и клиентами

### Tailor (tailor_user)
- Доступ к чтению всех данных
- Может изменять свои заказы
- Видит маскированные личные данные клиентов

### Cashier
- Доступ к чтению данных
- Может работать с кассой (CashRegister)
- Видит маскированные личные данные клиентов

## 📊 Примеры использования

### Демонстрация DDM
1. Выберите пункт меню **2. DDM**
2. Выберите **4. Side-by-Side Comparison**
3. Увидите разницу между данными Admin и Cashier

### Просмотр статуса TDE
1. Выберите пункт меню **5. TDE**
2. Выберите **1. View Database Encryption Status**
3. Увидите статус шифрования базы данных

### Тестирование триггеров
1. Выберите пункт меню **7. Triggers**
2. Выберите нужный триггер для тестирования
3. Увидите как работает автоматизация

## 🛠️ Устранение неполадок

### Ошибка подключения к БД
```
Failed to connect to database!
```
**Решение:**
- Проверьте, что SQL Server запущен
- Убедитесь, что база данных Atelier существует
- Проверьте учетные данные в файле `.env`
- Убедитесь, что установлен ODBC Driver 17

### Ошибка "Driver not found"
**Решение:**
Установите ODBC Driver 17 for SQL Server:
```
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Ошибка импорта модулей
```
ModuleNotFoundError: No module named 'pyodbc'
```
**Решение:**
```powershell
pip install -r requirements.txt
```

## 📝 Примечания

### Для курсового проекта
Это приложение демонстрирует:
1. ✅ Реализацию системы безопасности БД
2. ✅ Различные механизмы защиты данных
3. ✅ Автоматизацию бизнес-процессов
4. ✅ Архитектурные решения (filegroups)
5. ✅ Мониторинг и аудит

### Важные файлы для демонстрации
- **Audit logs**: `C:\CP\Audits\`
- **Backups**: `C:\CP\Backups\Atelier\`
- **Extended Events**: `C:\CP\ExtendedEvents\`

## 👨‍💻 Автор

Курсовой проект по дисциплине "Системы безопасности баз данных"

## 📄 Лицензия

Для образовательных целей

## 🔗 Связанные файлы

- `DB scripts.txt` - SQL скрипты для создания базы данных
- Все DDL и DML скрипты включены в исходный файл

---

**Последнее обновление:** Декабрь 2025
