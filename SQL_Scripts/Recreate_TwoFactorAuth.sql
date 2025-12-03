-- Пересоздание таблицы TwoFactorAuth для 2FA функционала

USE Atelier;
GO

-- Удалить старую таблицу если существует
IF OBJECT_ID('dbo.TwoFactorAuth', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.TwoFactorAuth;
    PRINT '✓ Старая таблица TwoFactorAuth удалена';
END
GO

-- Создать новую таблицу
CREATE TABLE dbo.TwoFactorAuth (
    UserID INT PRIMARY KEY,
    SecretKey NVARCHAR(100) NOT NULL,
    IsEnabled BIT DEFAULT 0 NOT NULL,
    BackupCodes NVARCHAR(500) NULL,
    CreatedAt DATETIME DEFAULT GETDATE() NOT NULL
);
GO

PRINT '✓ Таблица TwoFactorAuth успешно создана';
GO

-- Проверка структуры таблицы
SELECT 
    c.name AS ColumnName,
    t.name AS DataType,
    c.max_length AS MaxLength,
    c.is_nullable AS IsNullable
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.TwoFactorAuth')
ORDER BY c.column_id;
GO

PRINT '';
PRINT '✓ Таблица готова к использованию';
PRINT '  - UserID: INT (PRIMARY KEY, связан с sys.database_principals)';
PRINT '  - SecretKey: NVARCHAR(100) - секретный ключ для TOTP';
PRINT '  - IsEnabled: BIT - статус активации 2FA';
PRINT '  - BackupCodes: NVARCHAR(500) - резервные коды через запятую';
PRINT '  - CreatedAt: DATETIME - дата создания записи';
GO
