# 📊 Dashboard de Análisis Financiero - Proyecto Puerta Grande

Un dashboard completo para analizar la correlación entre sentimiento de noticias financieras y precios de acciones, construido con tecnologías modernas.

## 🚀 Características

- **📈 Datos Reales**: Precios de acciones de Yahoo Finance
- **📰 Noticias con Sentimiento**: Análisis automático de Alpha Vantage
- **📊 Visualizaciones Interactivas**: Gráficos de correlación y evolución temporal
- **🏗️ Arquitectura Moderna**: React + FastAPI + PostgreSQL
- **🐳 Containerizado**: Docker para fácil despliegue
- **📱 Responsive**: Interfaz adaptada a móviles y desktop

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18** con Vite
- **Chart.js** para visualizaciones
- **React Router** para navegación
- **CSS3** con diseño moderno

### Backend
- **FastAPI** (Python)
- **PostgreSQL** como base de datos
- **Redis** para caché
- **psycopg2** para conexión a BD

### APIs Externas
- **Alpha Vantage** para noticias y sentimiento
- **Yahoo Finance** para precios de acciones

### DevOps
- **Docker** y Docker Compose
- **Git** para control de versiones

## 📦 Instalación

### Prerrequisitos
- Docker y Docker Compose
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/hugo9917/financial-sentiment-dashboard.git
cd proyecto-puerta-grande
```

2. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp config.example.env config.env

# Editar config.env con tus API keys reales
# IMPORTANTE: Nunca subas config.env a GitHub
```

3. **Obtener API Keys**
   - **Alpha Vantage**: [Registrarse aquí](https://www.alphavantage.co/support/#api-key) (gratuito)
   - **NewsAPI** (opcional): [Registrarse aquí](https://newsapi.org/register) (gratuito)

4. **Ejecutar con Docker**
```bash
docker-compose -f docker-compose-simple.yaml up -d
```

5. **Acceder al dashboard**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 🔑 Configuración de APIs

### Alpha Vantage
1. Registrarse en [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Obtener API key gratuita
3. Agregar a `config.env`:
```
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
```

## 📊 Estructura del Proyecto

```
PROYECTO PUERTA GRANDE/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   ├── pages/          # Páginas principales
│   │   └── App.jsx         # Componente principal
├── backend/                 # API FastAPI
│   ├── main.py             # Servidor principal
│   ├── ingestion_main.py   # Lógica de ingesta de datos
│   └── requirements.txt    # Dependencias Python
├── docker-compose-simple.yaml  # Configuración Docker
├── init-db.sql             # Script de inicialización de BD
└── README.md               # Este archivo
```

## 🎯 Funcionalidades

### Dashboard Principal
- **Evolución de Precios**: Gráficos de líneas con datos OHLCV
- **Resumen Estadístico**: Métricas clave de cada acción
- **Filtros por Símbolo**: Selección de empresas específicas

### Análisis de Correlación
- **Gráfico de Dispersión**: Sentimiento vs Precio
- **Tabla Resumen**: Estadísticas por categoría de sentimiento
- **Análisis Temporal**: Evolución de correlaciones

### Datos en Tiempo Real
- **Actualización Automática**: Nuevos datos cada hora
- **Noticias Recientes**: Últimas noticias con análisis de sentimiento
- **Precios Actualizados**: Datos de mercado en tiempo real

## 📈 Datos Incluidos

### Acciones Cubiertas
- **AAPL** (Apple)
- **GOOGL** (Google)
- **MSFT** (Microsoft)
- **TSLA** (Tesla)
- **META** (Meta/Facebook)
- Y más...

### Tipos de Datos
- **Precios OHLCV**: Open, High, Low, Close, Volume
- **Noticias**: Título, descripción, fuente, fecha
- **Sentimiento**: Score numérico y categoría
- **Correlaciones**: Análisis temporal de relaciones

## 🔧 Desarrollo

### Ejecutar en Modo Desarrollo
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Agregar Nuevas Acciones
1. Editar `STOCK_SYMBOLS` en `backend/quick_fix.py`
2. Ejecutar script de ingesta
3. Los datos se actualizarán automáticamente

## 📝 API Endpoints

### Precios de Acciones
- `GET /api/stock-prices/{symbol}` - Obtener precios por símbolo
- `GET /api/stock-prices/` - Listar todos los precios

### Noticias
- `GET /api/news/{symbol}` - Noticias por símbolo
- `GET /api/news/` - Todas las noticias

### Correlaciones
- `GET /api/correlation/` - Datos de correlación
- `GET /api/correlation/{symbol}` - Correlación por símbolo

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Hugo9917** - [GitHub](https://github.com/hugo9917)

## 🙏 Agradecimientos

- **Alpha Vantage** por proporcionar datos de noticias y sentimiento
- **Yahoo Finance** por datos de precios de acciones
- **FastAPI** por el framework web moderno
- **React** por la biblioteca de interfaz de usuario

## 📞 Soporte

Si tienes preguntas o problemas:
- Contactar: hugo.astorga.17@gmail.com

---

⭐ **¡Dale una estrella al proyecto si te gustó!** ⭐ 