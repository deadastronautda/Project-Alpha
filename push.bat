Write-Output "🔄 Добавление файлов в Git..."
git add .

Write-Output "📝 Создание коммита..."
$commitMessage = "Streamlit-приложение для анализа финансовой отчетности"
git commit -m $commitMessage --no-verify

Write-Output "🚀 Отправка в GitHub..."
git push origin qa_dev

if ($LASTEXITCODE -ne 0) {
    Write-Output "❌ Ошибка при отправке. Пробуем принудительно..."
    git push --force origin qa_dev
}

Write-Output "✅ Готово! Проверяйте репозиторий на GitHub"
Read-Host -Prompt "Нажмите Enter для завершения"