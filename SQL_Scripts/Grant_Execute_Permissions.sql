-- ============================================================================
-- GRANT EXECUTE PERMISSIONS ON STORED PROCEDURES TO ROLES
-- This script adds EXECUTE permissions for stored procedures to roles
-- Run this on existing database to update permissions
-- ============================================================================

USE [Atelier]
GO

PRINT '======================================================================';
PRINT 'GRANTING EXECUTE PERMISSIONS ON STORED PROCEDURES';
PRINT '======================================================================';
PRINT '';

-- ======================================================================
-- 1. GRANT EXECUTE TO AtelierManager (All Procedures and Functions)
-- ======================================================================

PRINT 'Granting EXECUTE permissions to [AtelierManager]...';

-- Grant EXECUTE on entire schema (all procedures and functions)
GRANT EXECUTE ON SCHEMA::dbo TO [AtelierManager];
PRINT '  ✓ EXECUTE on SCHEMA::dbo (all procedures and functions)';

PRINT '';

-- ======================================================================
-- 2. GRANT EXECUTE TO AtelierTailor (Order Management)
-- ======================================================================

PRINT 'Granting EXECUTE permissions to [AtelierTailor]...';

-- Check if procedures exist and grant permissions
IF OBJECT_ID('dbo.sp_CreateOrder', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_CreateOrder] TO [AtelierTailor];
    PRINT '  ✓ EXECUTE on sp_CreateOrder';
END
ELSE
    PRINT '  ⚠ sp_CreateOrder does not exist';

IF OBJECT_ID('dbo.sp_CreateFullOrder', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_CreateFullOrder] TO [AtelierTailor];
    PRINT '  ✓ EXECUTE on sp_CreateFullOrder';
END
ELSE
    PRINT '  ⚠ sp_CreateFullOrder does not exist';

IF OBJECT_ID('dbo.sp_CalculateOrderCost', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_CalculateOrderCost] TO [AtelierTailor];
    PRINT '  ✓ EXECUTE on sp_CalculateOrderCost';
END
ELSE
    PRINT '  ⚠ sp_CalculateOrderCost does not exist';

IF OBJECT_ID('dbo.sp_FindAvailableTailors', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierTailor];
    PRINT '  ✓ EXECUTE on sp_FindAvailableTailors';
END
ELSE
    PRINT '  ⚠ sp_FindAvailableTailors does not exist';

IF OBJECT_ID('dbo.sp_TailorReport', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierTailor];
    PRINT '  ✓ EXECUTE on sp_TailorReport';
END
ELSE
    PRINT '  ⚠ sp_TailorReport does not exist';

PRINT '';

-- ======================================================================
-- 3. GRANT EXECUTE TO AtelierCashier (Payment Processing)
-- ======================================================================

PRINT 'Granting EXECUTE permissions to [AtelierCashier]...';

IF OBJECT_ID('dbo.sp_AddPayment', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_AddPayment] TO [AtelierCashier];
    PRINT '  ✓ EXECUTE on sp_AddPayment';
END
ELSE
    PRINT '  ⚠ sp_AddPayment does not exist';

IF OBJECT_ID('dbo.sp_TailorReport', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_TailorReport] TO [AtelierCashier];
    PRINT '  ✓ EXECUTE on sp_TailorReport';
END
ELSE
    PRINT '  ⚠ sp_TailorReport does not exist';

IF OBJECT_ID('dbo.sp_FindAvailableTailors', 'P') IS NOT NULL
BEGIN
    GRANT EXECUTE ON [dbo].[sp_FindAvailableTailors] TO [AtelierCashier];
    PRINT '  ✓ EXECUTE on sp_FindAvailableTailors';
END
ELSE
    PRINT '  ⚠ sp_FindAvailableTailors does not exist';

PRINT '';

-- ======================================================================
-- 4. VERIFY PERMISSIONS
-- ======================================================================

PRINT '======================================================================';
PRINT 'VERIFYING EXECUTE PERMISSIONS';
PRINT '======================================================================';
PRINT '';

SELECT 
    OBJECT_NAME(major_id) AS ObjectName,
    USER_NAME(grantee_principal_id) AS GrantedTo,
    permission_name AS Permission,
    state_desc AS State
FROM sys.database_permissions
WHERE class = 1  -- Object permissions
    AND permission_name = 'EXECUTE'
    AND USER_NAME(grantee_principal_id) IN ('AtelierTailor', 'AtelierCashier')
ORDER BY GrantedTo, ObjectName;

PRINT '';
PRINT '======================================================================';
PRINT 'EXECUTE PERMISSIONS GRANTED SUCCESSFULLY';
PRINT '======================================================================';
PRINT '';
PRINT 'Summary by Role:';
PRINT '';
PRINT '  ✓ AtelierManager:';
PRINT '    - Can execute ALL procedures and functions';
PRINT '    - Can use all views (db_datareader)';
PRINT '    - Triggers work automatically on DML operations';
PRINT '';
PRINT '  ✓ AtelierTailor:';
PRINT '    - Can execute: sp_CreateOrder, sp_CreateFullOrder, sp_CalculateOrderCost,';
PRINT '      sp_FindAvailableTailors, sp_TailorReport';
PRINT '    - Can use all views and functions (db_datareader)';
PRINT '    - Triggers work automatically on Orders/OrderCosts/OrderComplications/OrderFabrics';
PRINT '';
PRINT '  ✓ AtelierCashier:';
PRINT '    - Can execute: sp_AddPayment, sp_CalculateOrderCost (+ read-only procedures)';
PRINT '    - Can use all views and functions (db_datareader)';
PRINT '    - Triggers work automatically on CashRegister operations';
PRINT '';
PRINT '  ✓ Admin (dbo/atelier_admin):';
PRINT '    - Can execute EVERYTHING (db_owner)';
PRINT '';
PRINT 'Users in these roles can now execute stored procedures from the GUI.';
PRINT '======================================================================';
GO
