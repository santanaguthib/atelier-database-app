# Сводная таблица прав доступа

## ✅ Соответствие плану

| Объект БД | admin/dbo | manager | tailor_user | cashier |
|-----------|-----------|---------|-------------|---------|
| **Триггеры** | ✅ Все | ✅ Все | ✅ Orders* | ✅ CashRegister |
| **Views** | ✅ Все | ✅ Все | ✅ Все | ✅ Все |
| **Procedures** | ✅ Все | ✅ Все | ⚠️ Orders only | ⚠️ Payments only |
| **Functions** | ✅ Все | ✅ Все | ✅ Все | ✅ Все |

\* Триггеры срабатывают автоматически при операциях с таблицами, на которые у пользователя есть права

---

## Детальное распределение

### 1. Триггеры (автоматические)
```
✅ admin, manager - все триггеры срабатывают (db_owner/db_datawriter)
✅ tailor_user - триггеры на Orders, OrderCosts, OrderComplications, OrderFabrics
✅ cashier - триггеры на CashRegister
```

**Примечание:** Триггеры выполняются автоматически при INSERT/UPDATE/DELETE операциях. Права пользователя на таблицу автоматически дают возможность триггерам срабатывать.

---

### 2. Представления (Views) - SELECT
```
✅ Все пользователи имеют db_datareader → могут читать все views
```

**Реализация:**
- `ALTER ROLE [db_datareader] ADD MEMBER [RoleName]`
- Views доступны через обычный SELECT

---

### 3. Процедуры (Stored Procedures) - EXECUTE

#### admin/dbo:
```sql
-- db_owner → может выполнять ВСЕ
✅ Все процедуры без ограничений
```

#### manager (AtelierManager):
```sql
GRANT EXECUTE ON SCHEMA::dbo TO [AtelierManager];
-- ✅ Может выполнять ВСЕ процедуры и функции
```

#### tailor_user (AtelierTailor):
```sql
GRANT EXECUTE ON [dbo].[sp_CreateOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CreateFullOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CalculateOrderCost] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierTailor];

-- ⚠️ Только процедуры для работы с заказами
```

#### cashier (AtelierCashier):
```sql
GRANT EXECUTE ON [dbo].[sp_AddPayment] TO [AtelierCashier];
GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierCashier];
GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierCashier];

-- ⚠️ 3 процедуры: платежи + отчеты
```

---

### 4. Функции (Functions) - Используются в SELECT
```
✅ Все пользователи могут использовать все функции
```

**Реализация:**
- Функции вызываются внутри SELECT запросов
- db_datareader даёт право SELECT → автоматически можно использовать функции

**Примеры:**
```sql
-- Скалярная функция
SELECT dbo.CalculateTotal(OrderID) FROM Orders;

-- Табличная функция
SELECT * FROM dbo.GetOrdersByDate('2025-01-01', '2025-12-31');
```

---

## SQL Scripts

### Применение прав:
1. **Step_6a_CreateDatabaseRoles.sql** - Создание ролей с правами (для новой БД)
2. **Grant_Execute_Permissions.sql** - Добавление прав к существующей БД
3. **Verify_Permissions_Plan.sql** - Проверка соответствия плану

### Выполнить в SSMS:
```sql
-- 1. Применить права
USE [Atelier]
GO
EXEC('C:\AppAppAppAppApp\SQL_Scripts\Grant_Execute_Permissions.sql')

-- 2. Проверить результат
EXEC('C:\AppAppAppAppApp\SQL_Scripts\Verify_Permissions_Plan.sql')
```

---

## Проверка в GUI

### Для admin/manager:
1. Войти как `atelier_admin` или `manager`
2. Доступны все разделы меню
3. Stored Procedures → Execute → Все процедуры работают

### Для tailor_user:
1. Войти как `tailor_user`
2. Видны: Orders Management, 2FA Settings
3. Stored Procedures → Execute → Доступны только Orders-процедуры

### Для cashier:
1. Войти как `cashier`
2. Видны: Cash Operations, 2FA Settings
3. Stored Procedures → Execute → Доступны только Payment-процедуры

---

## Статус реализации

| Компонент | Статус | Файл |
|-----------|--------|------|
| Роли созданы | ✅ | Step_6a_CreateDatabaseRoles.sql |
| Права EXECUTE | ✅ | Grant_Execute_Permissions.sql |
| Проверка прав | ✅ | Verify_Permissions_Plan.sql |
| GUI RBAC | ✅ | gui_main.py |
| Execute вкладка | ✅ | gui_features.py |
| Документация | ✅ | EXECUTE_PERMISSIONS_SETUP.md |

**Все соответствует плану! ✅**
