# Инструкция по созданию резервной копии приложения

## Вариант 1: GitHub (Рекомендуется для курсового проекта) 🌟

### Преимущества:
- ✅ Версионный контроль (история всех изменений)
- ✅ Доступ с любого компьютера
- ✅ Можно показать преподавателю (ссылка на репозиторий)
- ✅ Защита от потери данных
- ✅ Бесплатно для публичных и приватных репозиториев

### Шаги:

1. **Установить Git** (если еще не установлен):
   - Скачать: https://git-scm.com/download/win
   - Установить с настройками по умолчанию

2. **Создать репозиторий на GitHub**:
   - Зайти на https://github.com
   - Нажать "New repository"
   - Название: `atelier-database-app` (или любое другое)
   - Можно сделать **Private** (приватный) если не хотите публичный доступ

3. **Инициализировать Git в папке проекта**:
   ```powershell
   cd C:\AppAppAppAppApp\AtelierApp
   git init
   git add .
   git commit -m "Initial commit: Atelier Database Management System"
   ```

4. **Связать с GitHub и загрузить**:
   ```powershell
   git remote add origin https://github.com/ваш-username/atelier-database-app.git
   git branch -M main
   git push -u origin main
   ```

### ⚠️ ВАЖНО: Файл .gitignore уже настроен!
- `.env` (пароли) **не будет загружен** на GitHub
- `__pycache__/` и `.venv/` также исключены
- **Безопасно для публичных репозиториев**

---

## Вариант 2: ZIP архив (Простой способ)

Запустите PowerShell скрипт:

```powershell
# backup_app_only.ps1

$BackupDir = "C:\Backups\AtelierApp"
$SourceDir = "C:\AppAppAppAppApp\AtelierApp"
$Date = Get-Date -Format "yyyy-MM-dd_HH-mm"
$BackupFile = "$BackupDir\AtelierApp_$Date.zip"

# Создать папку для бэкапов
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Создать ZIP архив (исключить .env, .venv, __pycache__)
Write-Host "Creating backup: $BackupFile" -ForegroundColor Cyan

# Копировать файлы во временную папку (без исключенных)
$TempDir = "$env:TEMP\AtelierApp_Backup"
if (Test-Path $TempDir) { Remove-Item $TempDir -Recurse -Force }
Copy-Item $SourceDir $TempDir -Recurse

# Удалить исключенные файлы/папки
Remove-Item "$TempDir\.env" -ErrorAction SilentlyContinue
Remove-Item "$TempDir\.venv" -Recurse -ErrorAction SilentlyContinue
Remove-Item "$TempDir\__pycache__" -Recurse -ErrorAction SilentlyContinue
Get-ChildItem $TempDir -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force

# Создать ZIP
Compress-Archive -Path "$TempDir\*" -DestinationPath $BackupFile -Force

# Очистить временную папку
Remove-Item $TempDir -Recurse -Force

Write-Host "✓ Backup created: $BackupFile" -ForegroundColor Green
Write-Host "Size: $([math]::Round((Get-Item $BackupFile).Length / 1MB, 2)) MB"

# Показать содержимое архива
Write-Host "`nArchive contents:" -ForegroundColor Yellow
Expand-Archive -Path $BackupFile -DestinationPath "$env:TEMP\test_extract" -Force
Get-ChildItem "$env:TEMP\test_extract" -Recurse | Select-Object FullName
Remove-Item "$env:TEMP\test_extract" -Recurse -Force
```

Сохранить как `backup_app_only.ps1` и запустить:
```powershell
.\backup_app_only.ps1
```

---

## Вариант 3: Облачное хранилище

### Google Drive / OneDrive / Dropbox:
1. Создать ZIP архив (см. Вариант 2)
2. Загрузить в облако
3. Или скопировать всю папку `AtelierApp` в синхронизируемую папку

---

## Что будет сохранено:

✅ **Включено в резервную копию:**
- Все Python модули (`main.py`, `database.py`, `config.py`, `modules/`)
- `requirements.txt`
- `.env.example` (шаблон без паролей)
- `.gitignore`
- `README.md`, `INSTALL.md` и другая документация
- SQL скрипты (`SQL_Scripts/`)

❌ **НЕ включено (по безопасности):**
- `.env` (файл с реальными паролями)
- `.venv/` (виртуальное окружение Python - 100+ МБ)
- `__pycache__/` (скомпилированный Python код)

---

## Восстановление из резервной копии:

### Из GitHub:
```powershell
git clone https://github.com/ваш-username/atelier-database-app.git
cd atelier-database-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Создать .env вручную или скопировать из старого проекта
```

### Из ZIP:
1. Распаковать архив в новую папку
2. Создать виртуальное окружение: `python -m venv .venv`
3. Активировать: `.venv\Scripts\activate`
4. Установить зависимости: `pip install -r requirements.txt`
5. Создать `.env` файл с учетными данными

---

## Рекомендация для курсового проекта:

**Используйте GitHub + ZIP архив:**
1. **GitHub** - основная резервная копия + можно показать преподавателю
2. **ZIP архив** - быстрая локальная копия на флешке/внешнем диске

**Сделайте приватный репозиторий** если не хотите делать код публичным.

---

## Частота резервного копирования:

- **GitHub**: После каждого значительного изменения (git commit + push)
- **ZIP**: 1 раз в день или перед важными изменениями
- **Перед защитой**: Обязательно сделать финальную копию!
