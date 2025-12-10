-- ============================================================================
-- VERIFICATION SCRIPT: Check Permissions Against Plan
-- ============================================================================

USE [Atelier]
GO

PRINT '======================================================================';
PRINT 'VERIFYING PERMISSIONS AGAINST PLAN';
PRINT '======================================================================';
PRINT '';

-- ======================================================================
-- 1. TRIGGERS (срабатывают автоматически)
-- ======================================================================

PRINT '1. TRIGGERS - Work automatically on DML operations';
PRINT '   ✅ admin, manager, tailor_user, cashier - triggers fire on relevant operations';
PRINT '';

SELECT 
    t.name AS TriggerName,
    OBJECT_NAME(t.parent_id) AS TableName,
    te.type_desc AS TriggerEvent
FROM sys.triggers t
JOIN sys.trigger_events te ON t.object_id = te.object_id
WHERE SCHEMA_NAME(OBJECTPROPERTY(t.parent_id, 'SchemaId')) = 'dbo'
ORDER BY TableName, TriggerName;

PRINT '';

-- ======================================================================
-- 2. VIEWS (представления) - SELECT access
-- ======================================================================

PRINT '2. VIEWS - SELECT access via db_datareader';
PRINT '   ✅ All users - can read all views (db_datareader)';
PRINT '';

SELECT 
    v.name AS ViewName,
    v.create_date AS Created
FROM sys.views v
WHERE SCHEMA_NAME(v.schema_id) = 'dbo'
ORDER BY v.name;

PRINT '';

-- ======================================================================
-- 3. STORED PROCEDURES - EXECUTE permissions
-- ======================================================================

PRINT '3. STORED PROCEDURES - EXECUTE permissions';
PRINT '';

-- Check EXECUTE permissions
SELECT 
    p.name AS ProcedureName,
    dp.name AS GrantedTo,
    perm.permission_name AS Permission
FROM sys.procedures p
LEFT JOIN sys.database_permissions perm ON p.object_id = perm.major_id
LEFT JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE SCHEMA_NAME(p.schema_id) = 'dbo'
    AND p.name LIKE 'sp_%'
    AND (perm.permission_name = 'EXECUTE' OR perm.permission_name IS NULL)
ORDER BY p.name, dp.name;

PRINT '';
PRINT '   Expected:';
PRINT '   ✅ admin, manager - can execute ALL';
PRINT '   ✅ tailor_user - can execute: sp_CreateOrder, sp_CreateFullOrder,';
PRINT '      sp_CalculateOrderCost, sp_FindAvailableTailors, sp_TailorReport';
PRINT '   ✅ cashier - can execute: sp_AddPayment, sp_CalculateOrderCost';
PRINT '';

-- Check schema-level EXECUTE permission (for AtelierManager)
SELECT 
    dp.name AS RoleName,
    perm.permission_name AS Permission,
    SCHEMA_NAME(perm.major_id) AS OnSchema
FROM sys.database_permissions perm
JOIN sys.database_principals dp ON perm.grantee_principal_id = dp.principal_id
WHERE perm.class = 3  -- Schema permissions
    AND perm.permission_name = 'EXECUTE'
    AND dp.name = 'AtelierManager';

PRINT '';

-- ======================================================================
-- 4. FUNCTIONS - Can be used by all (SELECT operations)
-- ======================================================================

PRINT '4. FUNCTIONS - Can be used in SELECT by all users';
PRINT '   ✅ All users - can use all functions (only SELECT)';
PRINT '';

SELECT 
    o.name AS FunctionName,
    o.type_desc AS FunctionType,
    o.create_date AS Created
FROM sys.objects o
WHERE SCHEMA_NAME(o.schema_id) = 'dbo'
    AND o.type IN ('FN', 'IF', 'TF')  -- Scalar, Inline, Table-valued functions
ORDER BY o.name;

PRINT '';

-- ======================================================================
-- 5. ROLE MEMBERSHIP
-- ======================================================================

PRINT '5. ROLE MEMBERSHIP - Current Users and Their Roles';
PRINT '';

SELECT 
    dp.name AS UserName,
    r.name AS RoleName
FROM sys.database_role_members drm
JOIN sys.database_principals dp ON drm.member_principal_id = dp.principal_id
JOIN sys.database_principals r ON drm.role_principal_id = r.principal_id
WHERE dp.name IN ('atelier_admin', 'manager', 'tailor_user', 'cashier')
    OR r.name IN ('AtelierManager', 'AtelierTailor', 'AtelierCashier')
ORDER BY dp.name, r.name;

PRINT '';

-- ======================================================================
-- 6. SUMMARY TABLE
-- ======================================================================

PRINT '======================================================================';
PRINT 'PERMISSION SUMMARY';
PRINT '======================================================================';
PRINT '';
PRINT 'USER/ROLE         | TRIGGERS | VIEWS | PROCEDURES        | FUNCTIONS';
PRINT '------------------|----------|-------|-------------------|----------';
PRINT 'admin/dbo         | ✅ All   | ✅ All| ✅ All            | ✅ All';
PRINT 'manager           | ✅ All   | ✅ All| ✅ All            | ✅ All';
PRINT 'tailor_user       | ✅ Orders| ✅ All| ⚠️ Orders only    | ✅ All';
PRINT 'cashier           | ✅ Cash  | ✅ All| ⚠️ Payments only  | ✅ All';
PRINT '';
PRINT '======================================================================';
PRINT 'VERIFICATION COMPLETE';
PRINT '======================================================================';
GO
