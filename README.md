# 📊 Financial Sentiment Analysis Dashboard - Puerta Grande Project

A comprehensive dashboard for analyzing the correlation between financial news sentiment and stock prices, built with modern technologies.

## 🚀 Features

- **📈 Real Data**: Stock prices from Yahoo Finance
- **📰 News with Sentiment**: Automatic analysis from Alpha Vantage
- **📊 Interactive Visualizations**: Correlation charts and temporal evolution
- **🔐 Authentication System**: JWT with user and admin roles
- **📰 Complete News Page**: Filters, search and sentiment analysis
- **🏗️ Modern Architecture**: React + FastAPI + PostgreSQL
- **🐳 Containerized**: Docker for easy deployment
- **📱 Responsive**: Interface adapted for mobile and desktop
- **🧪 Complete Tests**: Test coverage for frontend and backend

## 🛠️ Technologies Used

### Frontend
- **React 18** with Vite
- **Chart.js** for visualizations
- **React Router** for navigation
- **CSS3** with modern design
- **TypeScript** for type safety
- **Vitest** for testing
- **ESLint** for linting

### Backend
- **FastAPI** (Python)
- **PostgreSQL** as database
- **Redis** for caching
- **psycopg2** for DB connection
- **Pytest** for testing
- **Black** and **isort** for formatting
- **Flake8** for linting

### Data Engineering
- **DBT** for data transformation
- **Apache Airflow** for orchestration
- **Pandas** for data manipulation

### External APIs
- **Alpha Vantage** for news and sentiment
- **Yahoo Finance** for stock prices

### DevOps & Observability
- **Docker** and Docker Compose
- **Terraform** for Infrastructure as Code
- **GitHub Actions** for CI/CD
- **Prometheus** for metrics
- **Grafana** for visualization
- **AWS CloudWatch** for monitoring
- **Git** for version control

## 📦 Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Installation Steps

#### Option 1: Automatic Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/hugo9917/financial-sentiment-dashboard.git
cd proyecto-puerta-grande

# Run automatic setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### Option 2: Manual Setup
1. **Clone the repository**
```bash
git clone https://github.com/hugo9917/financial-sentiment-dashboard.git
cd proyecto-puerta-grande
```

2. **Configure environment variables**
```bash
# Copy configuration files
cp env.example .env
cp config.example.env config.env

# Edit config.env with your real API keys
# IMPORTANT: Never commit config.env to GitHub
```

3. **Get API Keys**
   - **Alpha Vantage**: [Register here](https://www.alphavantage.co/support/#api-key) (free)
   - **NewsAPI** (optional): [Register here](https://newsapi.org/register) (free)

4. **Run with Docker**
```bash
# For complete development with monitoring
docker-compose -f docker-compose.dev.yml up -d

# For simple version
docker-compose -f docker-compose-simple.yaml up -d
```

5. **Access the dashboard**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090
- Airflow: http://localhost:8080

## 🔑 API Configuration

### Alpha Vantage
1. Register at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get free API key
3. Add to `config.env`:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

## 📊 Project Structure

```
PROYECTO PUERTA GRANDE/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Main pages
│   │   └── App.jsx         # Main component
├── backend/                 # FastAPI backend
│   ├── main.py             # Main server
│   ├── auth.py             # Authentication module
│   ├── ingestion_main.py   # Data ingestion logic
│   └── requirements.txt    # Python dependencies
├── docker-compose-simple.yaml  # Docker configuration
├── init-db.sql             # Database initialization script
└── README.md               # This file
```

## 🎯 Functionality

### Main Dashboard
- **Price Evolution**: Line charts with OHLCV data
- **Statistical Summary**: Key metrics for each stock
- **Symbol Filters**: Selection of specific companies

### Correlation Analysis
- **Scatter Plot**: Sentiment vs Price
- **Summary Table**: Statistics by sentiment category
- **Temporal Analysis**: Correlation evolution

### Authentication System
- **Login/Logout**: Modern authentication interface
- **User Roles**: Admin and regular user
- **Route Protection**: JWT-protected endpoints
- **Session Management**: Secure tokens with expiration

### Complete News Page
- **Advanced Filters**: By source, sentiment and text search
- **Sentiment Analysis**: Score and category visualization
- **Interactive Charts**: Temporal sentiment evolution
- **Real-time Statistics**: News and sentiment metrics
- **Responsive Design**: Optimized for mobile and desktop

### Real-time Data
- **Automatic Updates**: New data every hour
- **Recent News**: Latest news with sentiment analysis
- **Updated Prices**: Real-time market data

## 📈 Included Data

### Covered Stocks
- **AAPL** (Apple)
- **GOOGL** (Google)
- **MSFT** (Microsoft)
- **TSLA** (Tesla)
- **META** (Meta/Facebook)
- And more...

### Data Types
- **OHLCV Prices**: Open, High, Low, Close, Volume
- **News**: Title, description, source, date
- **Sentiment**: Numerical score and category
- **Correlations**: Temporal relationship analysis

## 🔧 Development

### Run in Development Mode
```bash
# Use Docker Compose (Recommended)
docker-compose -f docker-compose.dev.yml up -d

# Or run locally
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Run all tests
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh

# Or run specific tests
./scripts/run-tests.sh backend
./scripts/run-tests.sh frontend
./scripts/run-tests.sh dbt

# Test new implementations
python test_implementation.py
```

### Test New Features

#### Authentication
```bash
# Available test users:
# Admin: admin / [Check environment variables]
# User: user / user123

# Test authentication endpoints
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=$ADMIN_PASSWORD"
```

#### News Page
- Access http://localhost:3000/news
- Test filters by sentiment, source and search
- Verify temporal evolution charts
- Check real-time statistics

### Add New Stocks
```bash
# Add new stock to the system
# 1. Update the stock list in the ingestion script
# 2. Restart the data ingestion process
# 3. The new data will appear in the dashboard
```

## 📊 API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /metrics` - Application metrics

### Authentication Endpoints
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `GET /auth/protected` - Protected route example
- `GET /auth/admin` - Admin-only route

### Data Endpoints
- `GET /api/sentiment/summary` - Sentiment summary
- `GET /api/sentiment/timeline` - Sentiment timeline
- `GET /api/correlation/analysis` - Correlation analysis
- `GET /api/stocks/prices` - Stock prices
- `GET /api/news/latest` - Latest news
- `GET /api/dashboard/stats` - Dashboard statistics

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to cloud platforms
# AWS, Google Cloud, Azure, etc.
```

### Environment Variables
```bash
# Required environment variables
DB_HOST=postgres
DB_NAME=financial_sentiment
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_PORT=5432

# Optional
SECRET_KEY=your-secret-key-here
AWS_REGION=us-east-1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Alpha Vantage** for financial news and sentiment data
- **Yahoo Finance** for stock price data
- **FastAPI** for the excellent Python web framework
- **React** for the frontend framework
- **Chart.js** for beautiful visualizations

## 📞 Support

If you have any questions or need help:

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/hugo9917/financial-sentiment-dashboard/issues)
- 📖 Documentation: [Wiki](https://github.com/hugo9917/financial-sentiment-dashboard/wiki)

---

**Made with ❤️ by the Puerta Grande Team** 