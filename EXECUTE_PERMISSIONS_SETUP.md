# Инструкция: Настройка прав доступа по ролям

## План распределения прав:

### Триггеры (срабатывают автоматически):
✅ **admin, manager, tailor_user, cashier** - триггеры работают при соответствующих операциях

### Представления (Views - SELECT):
✅ **Все пользователи** - могут читать все views (db_datareader)

### Процедуры (Stored Procedures):
✅ **admin, manager** - могут вызывать все  
⚠️ **tailor_user** - может вызывать только те, что работают с Orders/OrderCosts/OrderComplications/OrderFabrics  
⚠️ **cashier** - может вызывать только sp_AddPayment и read-only процедуры

### Функции (Functions):
✅ **Все пользователи** - могут использовать все функции (только SELECT)

---

## Шаг 1: Выполните SQL скрипт для добавления прав

Откройте SQL Server Management Studio (SSMS) и выполните скрипт:

```
C:\AppAppAppAppApp\SQL_Scripts\Grant_Execute_Permissions.sql
```

Или выполните команды вручную:

```sql
USE [Atelier]
GO

-- Права для портных (AtelierTailor)
GRANT EXECUTE ON [dbo].[sp_CreateOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CreateFullOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CalculateOrderCost] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierTailor];

-- Права для кассиров (AtelierCashier)
GRANT EXECUTE ON [dbo].[sp_AddPayment] TO [AtelierCashier];
GRANT EXECUTE ON [dbo].[sp_CalculateOrderCost] TO [AtelierCashier];
GO
```

## Шаг 2: Проверьте права

Выполните скрипт проверки:

```
C:\AppAppAppAppApp\SQL_Scripts\Verify_Permissions_Plan.sql
```

Или проверьте вручную:

```sql
-- Проверка EXECUTE прав
SELECT 
    OBJECT_NAME(major_id) AS ObjectName,
    USER_NAME(grantee_principal_id) AS GrantedTo,
    permission_name AS Permission
FROM sys.database_permissions
WHERE class = 1 
    AND permission_name = 'EXECUTE'
    AND USER_NAME(grantee_principal_id) IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier');

-- Проверка прав на уровне схемы (для Manager)
SELECT 
    dp.name AS RoleName,
    perm.permission_name AS Permission,
    SCHEMA_NAME(perm.major_id) AS OnSchema
FROM sys.database_permissions perm
JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE perm.class = 3 AND perm.permission_name = 'EXECUTE';
```

## Шаг 3: Перезапустите приложение

После выполнения SQL скрипта перезапустите GUI приложение.

## Как использовать в GUI:

1. Войдите как пользователь с ролью `tailor_user` или `cashier`
2. Перейдите в меню **"Business Logic"** → **"Stored Procedures"**
3. Откройте вкладку **"Execute"**
4. Используйте доступные процедуры:
   - **Calculate Order Cost** - доступна всем (Tailor + Cashier)
   - **Add Payment** - только для Cashier
   - **Tailor Report** - только для Tailor

## Доступные процедуры по ролям:

### AtelierTailor (Портной):
- ✅ sp_CreateOrder - создание заказа
- ✅ sp_CreateFullOrder - создание полного заказа с материалами
- ✅ sp_CalculateOrderCost - расчет стоимости заказа
- ✅ sp_FindAvailableTailors - поиск доступных портных
- ✅ sp_TailorReport - отчет по работе портного

### AtelierCashier (Кассир):
- ✅ sp_AddPayment - добавление платежа
- ✅ sp_CalculateOrderCost - расчет стоимости заказа

### AtelierManager & dbo (Админ/Менеджер):
- ✅ Все процедуры без ограничений
- ✅ Все функции без ограничений

## Дополнительно по плану:

### Триггеры:
- ✅ Работают автоматически для всех пользователей при INSERT/UPDATE/DELETE
- ✅ Не требуют явного вызова
- ✅ Срабатывают в контексте прав пользователя, выполняющего операцию

### Представления (Views):
- ✅ Все пользователи могут читать все views через db_datareader
- ✅ Views используются как обычные таблицы в SELECT запросах

### Функции (Functions):
- ✅ Все пользователи могут использовать функции в SELECT запросах
- ✅ Скалярные функции: `SELECT dbo.FunctionName(params)`
- ✅ Табличные функции: `SELECT * FROM dbo.FunctionName(params)`

## Примечания:

- Если процедура недоступна для вашей роли, вы получите ошибку прав доступа
- Все выполненные процедуры логируются в базе данных
- Результаты выполнения отображаются в таблице внизу экрана
- Триггеры, Views и Functions работают согласно утвержденному плану
