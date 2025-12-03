-- ======================================================================
-- STEP 6: USER REGISTRATION & MANAGEMENT SYSTEM
-- ======================================================================
-- This script creates a table to store user registration requests
-- and implements an approval workflow for new user accounts

USE [Atelier];
GO

-- Create table for registration requests
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'UserRegistrationRequests')
BEGIN
    CREATE TABLE [dbo].[UserRegistrationRequests]
    (
        [RequestID] INT IDENTITY(1,1) PRIMARY KEY,
        [Username] NVARCHAR(128) NOT NULL,
        [HashedPassword] NVARCHAR(128) NOT NULL,
        [FullName] NVARCHAR(200) NOT NULL,
        [Email] NVARCHAR(200) NOT NULL,
        [RequestedRole] NVARCHAR(50) NOT NULL CHECK (RequestedRole IN ('manager', 'tailor_user', 'cashier')),
        [Justification] NVARCHAR(500) NULL,
        [RequestDate] DATETIME NOT NULL DEFAULT GETDATE(),
        [Status] NVARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected')),
        [ProcessedDate] DATETIME NULL,
        [ProcessedBy] NVARCHAR(128) NULL,
        [RejectionReason] NVARCHAR(500) NULL,
        
        CONSTRAINT UQ_Username UNIQUE (Username)
    );
    
    PRINT '✓ Table UserRegistrationRequests created successfully';
END
ELSE
BEGIN
    PRINT '✓ Table UserRegistrationRequests already exists';
END
GO

-- Create index for faster status queries
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_RegistrationRequests_Status' AND object_id = OBJECT_ID('UserRegistrationRequests'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_RegistrationRequests_Status
    ON [dbo].[UserRegistrationRequests] ([Status])
    INCLUDE ([RequestDate], [Username], [RequestedRole]);
    
    PRINT '✓ Index IX_RegistrationRequests_Status created';
END
GO

-- Grant permissions for manager to handle registration requests
GRANT SELECT, INSERT ON [dbo].[UserRegistrationRequests] TO [manager];
GRANT UPDATE ON [dbo].[UserRegistrationRequests] TO [manager];
GO

PRINT '';
PRINT '======================================================================';
PRINT 'USER REGISTRATION SYSTEM - Setup Complete';
PRINT '======================================================================';
PRINT '';
PRINT 'Features Implemented:';
PRINT '  ✓ Registration request table with approval workflow';
PRINT '  ✓ Support for 3 roles: manager, tailor_user, cashier';
PRINT '  ✓ Admin approval/rejection mechanism';
PRINT '  ✓ Audit trail (ProcessedBy, ProcessedDate, RejectionReason)';
PRINT '';
PRINT 'Workflow:';
PRINT '  1. User submits registration request → Status: Pending';
PRINT '  2. Admin reviews request in application';
PRINT '  3. Admin approves → SQL login + database user created';
PRINT '     OR';
PRINT '     Admin rejects → Status: Rejected with reason';
PRINT '';
PRINT '======================================================================';
GO
