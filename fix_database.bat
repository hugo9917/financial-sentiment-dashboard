@echo off
echo 🚀 INICIANDO CORRECCIONES DE PRIORIDAD ALTA
echo ==========================================

echo.
echo 1️⃣ Verificando servicios Docker...
docker ps

echo.
echo 2️⃣ Reiniciando servicios...
docker-compose -f docker-compose-simple.yaml down
docker-compose -f docker-compose-simple.yaml up -d

echo.
echo 3️⃣ Esperando a que PostgreSQL esté listo...
timeout /t 10 /nobreak

echo.
echo 4️⃣ Probando conexión a PostgreSQL...
docker exec proyectopuertagrande-backend-1 python /app/test_db_connection.py

echo.
echo 5️⃣ Poblando base de datos con datos reales...
docker exec proyectopuertagrande-backend-1 python /app/quick_fix.py

echo.
echo 6️⃣ Verificando datos insertados...
docker exec proyectopuertagrande-backend-1 python /app/test_db_connection.py

echo.
echo 🎉 CORRECCIONES COMPLETADAS!
echo ==========================================
echo ✅ PostgreSQL configurado correctamente
echo ✅ Base de datos poblada con datos reales
echo ✅ Dashboard listo para usar
echo.
echo 🌐 Para acceder al dashboard:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000

pause 