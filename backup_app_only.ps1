# Создание резервной копии приложения (без БД)
# Исключает .env, .venv, __pycache__

$BackupDir = "C:\Backups\AtelierApp"
$SourceDir = "C:\AppAppAppAppApp\AtelierApp"
$Date = Get-Date -Format "yyyy-MM-dd_HH-mm"
$BackupFile = "$BackupDir\AtelierApp_$Date.zip"

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "РЕЗЕРВНОЕ КОПИРОВАНИЕ ПРИЛОЖЕНИЯ ATELIER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Создать папку для бэкапов
if (!(Test-Path $BackupDir)) {
    Write-Host "`nСоздание папки для резервных копий: $BackupDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "`nИсточник: $SourceDir" -ForegroundColor White
Write-Host "Назначение: $BackupFile" -ForegroundColor White

# Копировать файлы во временную папку (без исключенных)
Write-Host "`n[1/5] Копирование файлов во временную папку..." -ForegroundColor Cyan
$TempDir = "$env:TEMP\AtelierApp_Backup_$(Get-Date -Format 'HHmmss')"
Copy-Item $SourceDir $TempDir -Recurse

# Удалить исключенные файлы/папки
Write-Host "[2/5] Удаление конфиденциальных файлов (.env)..." -ForegroundColor Cyan
Remove-Item "$TempDir\.env" -ErrorAction SilentlyContinue -Force

Write-Host "[3/5] Удаление виртуального окружения (.venv)..." -ForegroundColor Cyan
Remove-Item "$TempDir\.venv" -Recurse -ErrorAction SilentlyContinue -Force

Write-Host "[4/5] Удаление кэш-файлов Python (__pycache__)..." -ForegroundColor Cyan
Get-ChildItem $TempDir -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Удалить тестовые скрипты если есть
Remove-Item "$TempDir\test_*.py" -ErrorAction SilentlyContinue -Force
Remove-Item "$TempDir\check_*.py" -ErrorAction SilentlyContinue -Force
Remove-Item "$TempDir\show_*.py" -ErrorAction SilentlyContinue -Force
Remove-Item "$TempDir\fix_*.py" -ErrorAction SilentlyContinue -Force
Remove-Item "$TempDir\remove_*.py" -ErrorAction SilentlyContinue -Force
Remove-Item "$TempDir\setup_*.py" -ErrorAction SilentlyContinue -Force

# Создать ZIP
Write-Host "[5/5] Создание ZIP архива..." -ForegroundColor Cyan
Compress-Archive -Path "$TempDir\*" -DestinationPath $BackupFile -Force

# Очистить временную папку
Remove-Item $TempDir -Recurse -Force

$FileSize = [math]::Round((Get-Item $BackupFile).Length / 1MB, 2)

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "✓ РЕЗЕРВНАЯ КОПИЯ СОЗДАНА УСПЕШНО!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "Файл: $BackupFile" -ForegroundColor White
Write-Host "Размер: $FileSize МБ" -ForegroundColor White

# Показать список всех резервных копий
Write-Host "`nВсе резервные копии в $BackupDir`:" -ForegroundColor Yellow
Get-ChildItem $BackupDir -Filter "AtelierApp_*.zip" | Sort-Object LastWriteTime -Descending | Format-Table Name, @{Label="Размер (МБ)"; Expression={[math]::Round($_.Length / 1MB, 2)}}, LastWriteTime -AutoSize

Write-Host "`nЧто НЕ включено в резервную копию (по соображениям безопасности):" -ForegroundColor Yellow
Write-Host "  ✗ .env (файл с паролями)" -ForegroundColor Red
Write-Host "  ✗ .venv/ (виртуальное окружение Python)" -ForegroundColor Red
Write-Host "  ✗ __pycache__/ (скомпилированный код)" -ForegroundColor Red
Write-Host "  ✗ test_*.py (тестовые скрипты)" -ForegroundColor Red

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Для восстановления:" -ForegroundColor Cyan
Write-Host "  1. Распаковать ZIP архив" -ForegroundColor White
Write-Host "  2. Создать .venv: python -m venv .venv" -ForegroundColor White
Write-Host "  3. Активировать: .venv\Scripts\activate" -ForegroundColor White
Write-Host "  4. Установить: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  5. Создать .env файл с учетными данными" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`nНажмите Enter для выхода..." -ForegroundColor Yellow
Read-Host
