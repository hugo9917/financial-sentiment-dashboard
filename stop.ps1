Write-Host "🛑 Deteniendo Proyecto Puerta Grande" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

# Detener todos los servicios
Write-Host "⏹️ Deteniendo todos los servicios..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "✅ Servicios detenidos correctamente" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Para volver a iniciar el proyecto, ejecuta: .\start.ps1" -ForegroundColor Cyan
Write-Host "" 