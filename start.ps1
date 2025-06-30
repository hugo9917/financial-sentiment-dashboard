Write-Host "🚀 Iniciando Proyecto Puerta Grande - Pipeline de Datos Financieros" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Verificar si Docker está instalado
try {
    docker --version | Out-Null
    Write-Host "✅ Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Verificar si Docker Compose está instalado
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero." -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creando archivo .env desde env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ Archivo .env creado. Puedes editarlo si necesitas cambiar configuraciones." -ForegroundColor Green
}

# Inicializar Airflow si es la primera vez
if (-not (Test-Path "logs")) {
    Write-Host "🔧 Inicializando Airflow..." -ForegroundColor Yellow
    docker-compose --profile init up airflow-init
    Write-Host "✅ Airflow inicializado correctamente." -ForegroundColor Green
}

# Construir las imágenes
Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Yellow
docker-compose build --no-cache

# Iniciar todos los servicios
Write-Host "🚀 Iniciando todos los servicios..." -ForegroundColor Yellow
docker-compose up -d

# Esperar un momento para que los servicios se inicien
Write-Host "⏳ Esperando que los servicios se inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar el estado de los servicios
Write-Host "🔍 Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "🎉 ¡Proyecto iniciado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Servicios disponibles:" -ForegroundColor Cyan
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   • Airflow UI: http://localhost:8080 (usuario: airflow, contraseña: airflow)" -ForegroundColor White
Write-Host "   • PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "   • Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   • Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   • Detener servicios: docker-compose down" -ForegroundColor White
Write-Host "   • Reiniciar servicios: docker-compose restart" -ForegroundColor White
Write-Host "   • Ver estado: docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Para desarrollo:" -ForegroundColor Cyan
Write-Host "   • Los cambios en el código se reflejan automáticamente" -ForegroundColor White
Write-Host "   • Los logs se pueden ver con: docker-compose logs -f [servicio]" -ForegroundColor White
Write-Host "" 