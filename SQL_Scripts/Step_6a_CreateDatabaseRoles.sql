-- ======================================================================
-- STEP 6a: DATABASE ROLES FOR USER MANAGEMENT
-- ======================================================================
-- This script creates custom database roles with predefined permissions
-- for each user category (Manager, Tailor, Cashier)
-- This simplifies user management - just add user to appropriate role

USE [Atelier];
GO

PRINT '======================================================================';
PRINT 'CREATING CUSTOM DATABASE ROLES';
PRINT '======================================================================';
PRINT '';

-- ======================================================================
-- 1. ROLE: AtelierManager
-- ======================================================================
-- Full read/write access, can see unmasked data

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierManager' AND type = 'R')
BEGIN
    CREATE ROLE [AtelierManager];
    PRINT '✓ Role [AtelierManager] created';
END
ELSE
BEGIN
    PRINT '✓ Role [AtelierManager] already exists';
END
GO

-- Grant read/write permissions
ALTER ROLE [db_datareader] ADD MEMBER [AtelierManager];
ALTER ROLE [db_datawriter] ADD MEMBER [AtelierManager];
GO

-- Grant UNMASK permission to see real data (not masked)
GRANT UNMASK TO [AtelierManager];

-- Grant EXECUTE on all stored procedures and functions
GRANT EXECUTE ON SCHEMA::dbo TO [AtelierManager];
GO

PRINT '  • Permissions: db_datareader, db_datawriter, UNMASK';
PRINT '  • Can EXECUTE all stored procedures and functions';
PRINT '  • Can use all views (via db_datareader)';
PRINT '  • Triggers work automatically on DML operations';
PRINT '';

-- ======================================================================
-- 2. ROLE: AtelierTailor
-- ======================================================================
-- Read access + work with orders and production

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierTailor' AND type = 'R')
BEGIN
    CREATE ROLE [AtelierTailor];
    PRINT '✓ Role [AtelierTailor] created';
END
ELSE
BEGIN
    PRINT '✓ Role [AtelierTailor] already exists';
END
GO

-- Grant read access
ALTER ROLE [db_datareader] ADD MEMBER [AtelierTailor];
GO

-- Grant specific permissions for orders and production
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[Orders] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderCosts] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderComplications] TO [AtelierTailor];
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[OrderFabrics] TO [AtelierTailor];

-- Read-only access to reference tables
GRANT SELECT ON [dbo].[Tailors] TO [AtelierTailor];
GRANT SELECT ON [dbo].[Fabrics] TO [AtelierTailor];
GRANT SELECT ON [dbo].[Services] TO [AtelierTailor];
GRANT SELECT ON [dbo].[OrderStatuses] TO [AtelierTailor];

-- Grant EXECUTE on stored procedures for order management
GRANT EXECUTE ON [dbo].[sp_CreateOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CreateFullOrder] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_CalculateOrderCost] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierTailor];
GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierTailor];
GO

PRINT '  • Permissions: db_datareader + INSERT/UPDATE/DELETE on Orders, OrderCosts, OrderComplications, OrderFabrics';
PRINT '  • EXECUTE permissions: sp_CreateOrder, sp_CreateFullOrder, sp_CalculateOrderCost, sp_FindAvailableTailors, sp_TailorReport';
PRINT '  • Can use all views and functions (via db_datareader)';
PRINT '  • Triggers work automatically on Orders/OrderCosts/OrderComplications/OrderFabrics operations';
PRINT '';

-- ======================================================================
-- 3. ROLE: AtelierCashier
-- ======================================================================
-- Read access + work with cash register

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'AtelierCashier' AND type = 'R')
BEGIN
    CREATE ROLE [AtelierCashier];
    PRINT '✓ Role [AtelierCashier] created';
END
ELSE
BEGIN
    PRINT '✓ Role [AtelierCashier] already exists';
END
GO

-- Grant read access
ALTER ROLE [db_datareader] ADD MEMBER [AtelierCashier];
GO

-- Grant specific permissions for cash operations
GRANT SELECT, INSERT, UPDATE, DELETE ON [dbo].[CashRegister] TO [AtelierCashier];

-- Read-only access to orders and customers
GRANT SELECT ON [dbo].[Orders] TO [AtelierCashier];
GRANT SELECT ON [dbo].[Customers] TO [AtelierCashier];
GRANT SELECT ON [dbo].[OrderStatuses] TO [AtelierCashier];

-- Grant EXECUTE on stored procedures for payment processing
GRANT EXECUTE ON [dbo].[sp_AddPayment] TO [AtelierCashier];
GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierCashier];
GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierCashier];
-- Note: Read-only procedures (that only SELECT) are allowed via db_datareader
GO

PRINT '  • Permissions: db_datareader + INSERT/UPDATE/DELETE on CashRegister';
PRINT '  • EXECUTE permissions: sp_AddPayment, sp_TailorReport, sp_FindAvailableTailors';
PRINT '  • Can use all views and functions (via db_datareader)';
PRINT '  • Triggers work automatically on CashRegister operations';
PRINT '';

-- ======================================================================
-- 4. UPDATE EXISTING USERS TO USE ROLES
-- ======================================================================

PRINT '======================================================================';
PRINT 'UPDATING EXISTING USERS';
PRINT '======================================================================';
PRINT '';

-- Manager → AtelierManager role
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'manager')
BEGIN
    -- Remove old individual permissions (if needed, keep role memberships)
    ALTER ROLE [AtelierManager] ADD MEMBER [manager];
    PRINT '✓ User [manager] added to role [AtelierManager]';
END

-- Tailor → AtelierTailor role
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'tailor_user')
BEGIN
    ALTER ROLE [AtelierTailor] ADD MEMBER [tailor_user];
    PRINT '✓ User [tailor_user] added to role [AtelierTailor]';
END

-- Cashier → AtelierCashier role
IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'cashier')
BEGIN
    ALTER ROLE [AtelierCashier] ADD MEMBER [cashier];
    PRINT '✓ User [cashier] added to role [AtelierCashier]';
END
GO

PRINT '';
PRINT '======================================================================';
PRINT 'DATABASE ROLES - Setup Complete';
PRINT '======================================================================';
PRINT '';
PRINT 'Created Roles:';
PRINT '  ✓ AtelierManager  - Full access, sees unmasked data';
PRINT '  ✓ AtelierTailor   - Work with orders and production';
PRINT '  ✓ AtelierCashier  - Work with cash register';
PRINT '';
PRINT 'Benefits:';
PRINT '  • Simplified user management';
PRINT '  • Consistent permissions across users';
PRINT '  • Easy to modify permissions for all users at once';
PRINT '  • Better security through role-based access control (RBAC)';
PRINT '';
PRINT 'Usage in User Management module:';
PRINT '  When approving registration, just execute:';
PRINT '    ALTER ROLE [AtelierManager] ADD MEMBER [new_username]';
PRINT '';
PRINT '======================================================================';
GO

-- ======================================================================
-- 5. VERIFY ROLES AND PERMISSIONS
-- ======================================================================

PRINT '';
PRINT 'Current Database Roles and Members:';
PRINT '======================================================================';

SELECT 
    r.name AS RoleName,
    m.name AS MemberName,
    m.type_desc AS MemberType
FROM sys.database_role_members rm
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
WHERE r.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY r.name, m.name;

PRINT '';
PRINT '======================================================================';
PRINT 'Setup completed successfully!';
PRINT '======================================================================';
GO
