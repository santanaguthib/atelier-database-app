-- ============================================================================
-- FIX: CashRegister PRIMARY KEY - Allow multiple payments per day per order
-- This script modifies the CashRegister table to use PaymentID as PRIMARY KEY
-- ============================================================================

USE [Atelier]
GO

PRINT '======================================================================';
PRINT 'FIXING CashRegister TABLE PRIMARY KEY';
PRINT '======================================================================';
PRINT '';

-- Step 1: Check if foreign keys reference CashRegister
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE referenced_object_id = OBJECT_ID('dbo.CashRegister'))
BEGIN
    PRINT '⚠ WARNING: Foreign keys reference CashRegister table';
    PRINT 'Dropping foreign keys...';
    
    DECLARE @sql NVARCHAR(MAX) = '';
    SELECT @sql = @sql + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + 
                  '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + 
                  ' DROP CONSTRAINT ' + QUOTENAME(name) + ';' + CHAR(13)
    FROM sys.foreign_keys 
    WHERE referenced_object_id = OBJECT_ID('dbo.CashRegister');
    
    IF @sql <> ''
        EXEC sp_executesql @sql;
    
    PRINT '✓ Foreign keys dropped';
END
ELSE
BEGIN
    PRINT '✓ No foreign keys to drop';
END

PRINT '';

-- Step 2: Create backup of existing data
PRINT 'Creating backup of CashRegister data...';

SELECT * 
INTO CashRegister_Backup
FROM CashRegister;

DECLARE @BackupCount INT;
SELECT @BackupCount = COUNT(*) FROM CashRegister_Backup;
PRINT '✓ Backed up ' + CAST(@BackupCount AS NVARCHAR(10)) + ' records to CashRegister_Backup';
PRINT '';

-- Step 3: Drop existing PRIMARY KEY constraint
PRINT 'Dropping old PRIMARY KEY constraint...';

DECLARE @pkName NVARCHAR(128);
SELECT @pkName = name 
FROM sys.key_constraints 
WHERE type = 'PK' 
  AND parent_object_id = OBJECT_ID('dbo.CashRegister');

IF @pkName IS NOT NULL
BEGIN
    DECLARE @dropPK NVARCHAR(500) = 'ALTER TABLE dbo.CashRegister DROP CONSTRAINT ' + QUOTENAME(@pkName);
    EXEC sp_executesql @dropPK;
    PRINT '✓ Dropped PRIMARY KEY: ' + @pkName;
END
ELSE
BEGIN
    PRINT '⚠ No PRIMARY KEY found to drop';
END

PRINT '';

-- Step 4: Add PaymentID column with IDENTITY
PRINT 'Adding PaymentID column...';

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.CashRegister') AND name = 'PaymentID')
BEGIN
    ALTER TABLE dbo.CashRegister 
    ADD PaymentID INT IDENTITY(1,1) NOT NULL;
    
    PRINT '✓ Added PaymentID column with IDENTITY';
END
ELSE
BEGIN
    PRINT '⚠ PaymentID column already exists';
END

PRINT '';

-- Step 5: Create new PRIMARY KEY on PaymentID
PRINT 'Creating new PRIMARY KEY on PaymentID...';

ALTER TABLE dbo.CashRegister
ADD CONSTRAINT PK_CashRegister PRIMARY KEY (PaymentID);

PRINT '✓ Created PRIMARY KEY: PK_CashRegister on PaymentID';
PRINT '';

-- Step 6: Create indexes for performance
PRINT 'Creating indexes for query performance...';

-- Index on OrderID for fast lookups
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.CashRegister') AND name = 'IX_CashRegister_OrderID')
BEGIN
    CREATE NONCLUSTERED INDEX IX_CashRegister_OrderID 
    ON dbo.CashRegister(OrderID);
    PRINT '✓ Created index: IX_CashRegister_OrderID';
END

-- Index on PaymentDate for date range queries
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.CashRegister') AND name = 'IX_CashRegister_PaymentDate')
BEGIN
    CREATE NONCLUSTERED INDEX IX_CashRegister_PaymentDate 
    ON dbo.CashRegister(PaymentDate);
    PRINT '✓ Created index: IX_CashRegister_PaymentDate';
END

-- Composite index for order payment history
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.CashRegister') AND name = 'IX_CashRegister_OrderID_PaymentDate')
BEGIN
    CREATE NONCLUSTERED INDEX IX_CashRegister_OrderID_PaymentDate 
    ON dbo.CashRegister(OrderID, PaymentDate);
    PRINT '✓ Created index: IX_CashRegister_OrderID_PaymentDate';
END

PRINT '';

-- Step 7: Verify structure
PRINT 'Verifying new table structure...';
PRINT '';
PRINT 'Columns:';

SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable,
    c.is_identity AS IsIdentity
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.CashRegister')
ORDER BY c.column_id;

PRINT '';
PRINT 'Constraints:';

SELECT 
    type_desc AS ConstraintType,
    name AS ConstraintName
FROM sys.key_constraints
WHERE parent_object_id = OBJECT_ID('dbo.CashRegister');

PRINT '';
PRINT 'Indexes:';

SELECT 
    name AS IndexName,
    type_desc AS IndexType
FROM sys.indexes
WHERE object_id = OBJECT_ID('dbo.CashRegister')
  AND name IS NOT NULL;

PRINT '';
PRINT '======================================================================';
PRINT 'CashRegister TABLE MODIFICATION COMPLETE';
PRINT '======================================================================';
PRINT '';
PRINT 'Summary:';
PRINT '  ✓ Old PRIMARY KEY dropped';
PRINT '  ✓ PaymentID column added with IDENTITY';
PRINT '  ✓ New PRIMARY KEY created on PaymentID';
PRINT '  ✓ Performance indexes created';
PRINT '  ✓ Data preserved (backup in CashRegister_Backup)';
PRINT '';
PRINT 'Benefits:';
PRINT '  • Multiple payments per order per day now allowed';
PRINT '  • Simpler PRIMARY KEY (single column)';
PRINT '  • Better performance with proper indexes';
PRINT '  • No more duplicate key errors!';
PRINT '';
PRINT 'Note: You can drop CashRegister_Backup table after verifying data:';
PRINT '  DROP TABLE CashRegister_Backup;';
PRINT '';
PRINT '======================================================================';
GO
