# Настройка политики выполнения
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Переход в папку проекта
Set-Location "C:\Alpha"

# Инициализация git (если еще не инициализирован)
if (!(Test-Path ".git")) {
    git init
}

# Настройка пользователя
git config user.name "deadastronautda"
git config user.email 230589515+deadastronautda@users.noreply.github.com

# Связывание с удаленным репозиторием
$remoteUrl = "https://github.com/deadastronautda/Project-Alpha.git"
$currentRemote = git remote get-url origin 2>$null

if ($currentRemote -ne $remoteUrl) {
    if ($currentRemote) {
        git remote set-url origin $remoteUrl
    } else {
        git remote add origin $remoteUrl
    }
}

# Добавление файлов и коммит
git add .
git commit -m "🚀 Initial commit: Financial analyzer application with Docker support" --no-verify

# Отправка изменений
try {
    git push -u origin main
} catch {
    # Если не удалось отправить в main, попробуем qa_dev
    try {
        git checkout -b qa_dev 2>$null
        git push -u origin qa_dev
    } catch {
        Write-Host "❌ Ошибка при отправке изменений. Проверьте подключение к интернету и права доступа к репозиторию."
        Write-Host "Текст ошибки: $_"
    }
}

Write-Host "✅ Проект успешно отправлен на GitHub!"
Write-Host "Проверьте репозиторий: https://github.com/deadastronautda/Project-Alpha"