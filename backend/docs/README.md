# Sri Lankan Situational Awareness Platform

A comprehensive real-time situational awareness platform for Sri Lanka that processes news, trends, weather, food pricing, tax revenue, YouTube, and national signals into actionable insights, indicators, risks, trends, and anomalies.

## 🏗️ System Architecture

### Technology Stack
- **Backend Framework**: Flask 2.3.3
- **Task Queue**: Celery 5.3.4 with Redis broker
- **Database**: MongoDB with PyMongo
- **Data Processing**: Pandas, NumPy, SciPy
- **Machine Learning**: Scikit-learn, NLTK
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Flower for Celery monitoring

### Data Flow Pipeline
```
Scraping → Ingestion → Preprocessing → Analysis → API Exposure
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── config/                 # Configuration files
│   │   ├── app_config.py       # Flask application configuration
│   │   ├── celery_app.py       # Celery application setup
│   │   ├── mongo_config.py     # MongoDB connection configuration
│   │   └── settings.py         # Application settings
│   ├── ml/                     # Machine learning models
│   │   ├── anomaly_detector.py # Anomaly detection algorithms
│   │   ├── clustering_engine.py # Data clustering models
│   │   ├── feature_engineer.py # Feature engineering utilities
│   │   ├── trend_analyzer.py   # Trend analysis integration
│   │   └── trend_scorer.py     # Trend scoring algorithms
│   ├── model/                  # MongoDB data models
│   │   ├── indicator_model.py  # Indicator data model
│   │   ├── insight_model.py    # Insight data model
│   │   ├── news_model.py       # News article model
│   │   ├── pricing_model.py    # Food pricing model
│   │   ├── risk_model.py       # Risk assessment model
│   │   ├── tax_model.py        # Tax revenue model
│   │   ├── trends_model.py     # Trends data model
│   │   ├── weather_model.py    # Weather data model
│   │   └── youtube_model.py    # YouTube data model
│   ├── modules/
│   │   ├── ScrapModule/        # Data collection modules
│   │   │   ├── NewsScrapper.py # News data collector
│   │   │   ├── foodPricingScrap.py # Food pricing collector
│   │   │   ├── google_trends_collector.py # Google Trends collector
│   │   │   ├── taxRevenueGather.py # Tax revenue collector
│   │   │   ├── weatherCollector.py # Weather data collector
│   │   │   └── youtube_collector.py # YouTube data collector
│   │   ├── ingestionLayer/     # Data ingestion pipeline
│   │   │   ├── data_ingestor.py # Data ingestion utilities
│   │   │   ├── ingestion_pipeline.py # Main ingestion pipeline
│   │   │   └── scheduler.py    # Ingestion scheduling
│   │   └── preprocessingLayer/ # Data preprocessing
│   │       ├── data_cleaner.py # Data cleaning utilities
│   │       ├── normalization_engine.py # Data normalization
│   │       ├── preprocessing_pipeline.py # Main preprocessing pipeline
│   │       └── text_preprocessor.py # Text preprocessing
│   ├── routes/                 # API routes
│   │   └── api_routes.py       # All REST API endpoints
│   ├── service/
│   │   ├── general/            # General services
│   │   └── tasks/              # Celery task definitions
│   │       ├── analysis_tasks.py # Analysis tasks
│   │       ├── processing_tasks.py # Processing tasks
│   │       └── scraping_tasks.py # Scraping tasks
│   └── __init__.py            # Application initialization
├── docs/                      # Documentation
│   └── README.md              # This file
├── Dockerfile                 # Flask application container
├── Dockerfile.worker          # Celery worker container
├── docker-compose.yml         # Docker compose configuration
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)

### Running with Docker Compose

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Access services**:
   - Flask API: http://localhost:5000
   - Flower (Celery monitoring): http://localhost:5555
   - MongoDB: localhost:27017
   - Redis: localhost:6379

### Manual Setup (Development)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download NLTK data**:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('vader_lexicon')
   ```

3. **Set environment variables**:
   ```bash
   export FLASK_ENV=development
   export MONGODB_URI=mongodb://localhost:27017/situational_awareness
   export REDIS_URL=redis://localhost:6379/0
   ```

4. **Start services**:
   ```bash
   # Start Redis
   redis-server
   
   # Start MongoDB
   mongod
   
   # Start Flask application
   flask run
   
   # Start Celery worker
   celery -A app.celery worker --loglevel=info
   
   # Start Celery beat (scheduler)
   celery -A app.celery beat --loglevel=info
   ```

## 📊 Data Sources & Collection

### News Data
- **Sources**: Daily Mirror, Sunday Times, NewsFirst, Ada Derana
- **Collection**: Web scraping with BeautifulSoup
- **Frequency**: Hourly
- **Data Points**: Headlines, content, publication date, categories

### Google Trends
- **Sources**: Google Trends API
- **Collection**: API integration with fallback simulation
- **Frequency**: Daily
- **Data Points**: Search trends, interest over time, related queries

### YouTube Data
- **Sources**: YouTube Data API
- **Collection**: API integration with fallback simulation
- **Frequency**: Daily
- **Data Points**: Video metrics, engagement, comments sentiment

### Weather Data
- **Sources**: OpenWeatherMap API
- **Collection**: API integration with fallback simulation
- **Frequency**: 3-hour intervals
- **Data Points**: Temperature, humidity, precipitation, wind speed

### Food Pricing
- **Sources**: Market data, government reports
- **Collection**: Web scraping and manual data entry simulation
- **Frequency**: Weekly
- **Data Points**: Commodity prices, market trends, supply indicators

### Tax Revenue
- **Sources**: Government revenue reports
- **Collection**: Data scraping and simulation
- **Frequency**: Monthly
- **Data Points**: Tax categories, revenue amounts, trends

## 🔧 API Endpoints

### Health & Status
- `GET /status/health` - System health check
- `GET /status/queues` - Celery queue status

### Pipeline Control
- `POST /scrape/run` - Trigger scraping pipeline
- `POST /preprocess/run` - Trigger preprocessing pipeline
- `POST /analyze/run` - Trigger analysis pipeline

### Data Access
- `GET /indicators/latest` - Latest situational indicators
- `GET /risks/latest` - Current risk assessments
- `GET /insights/overview` - Comprehensive insights overview
- `GET /trends` - Current trends across all data types

### Query Parameters
- `type` - Filter by data type (news, weather, prices, tax, youtube, all)
- `lookback` - Number of days to look back (default: 30)
- `limit` - Number of results to return

## 🤖 Machine Learning Features

### Anomaly Detection
- **Univariate Methods**: Z-score, IQR (Interquartile Range)
- **Multivariate Methods**: Isolation Forest
- **Sri Lankan Context**: Custom thresholds for local patterns

### Trend Analysis
- **Composite Scoring**: Slope, R-squared, momentum, volatility
- **Weighted Averages**: Sri Lankan context-specific weights
- **Cross-Domain Correlation**: Weather → prices, news → sentiment

### Clustering
- **Algorithms**: KMeans with silhouette score optimization
- **Applications**: News categorization, price pattern grouping
- **Sri Lankan Features**: Local stopwords, regional patterns

### Feature Engineering
- **Temporal Features**: Day of week, hour, fiscal periods
- **Rolling Statistics**: Moving averages, standard deviations
- **Cross-Domain Features**: Weather-impacted pricing, sentiment-driven trends

## 🗃️ Database Schema

### Collections
- `news_articles` - Raw and processed news data
- `weather_data` - Meteorological observations
- `food_prices` - Commodity pricing information
- `tax_revenue` - Government revenue data
- `youtube_metrics` - Social media engagement data
- `trends_data` - Processed trend information
- `indicators` - Calculated situational indicators
- `risks` - Risk assessment results
- `insights` - Business intelligence insights

### Indexes
- Time-based indexes for all collections
- Category indexes for efficient filtering
- Text indexes for search functionality

## ⚙️ Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0

# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017/situational_awareness
MONGODB_DB_NAME=situational_awareness

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# API Keys (for production)
NEWS_API_KEY=your_news_api_key
YOUTUBE_API_KEY=your_youtube_api_key
OPENWEATHER_API_KEY=your_weather_api_key
GOOGLE_TRENDS_API_KEY=your_trends_api_key
```

### Celery Configuration
- **Broker**: Redis
- **Result Backend**: Redis
- **Task Queues**: scraping, processing, analysis
- **Concurrency**: 4 workers per queue
- **Scheduled Tasks**: Hourly scraping, daily analysis

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_scrapers.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Test Structure
```
tests/
├── test_scrapers.py          # Data collector tests
├── test_ingestion.py         # Ingestion pipeline tests
├── test_preprocessing.py     # Preprocessing tests
├── test_ml_models.py         # Machine learning tests
├── test_api_routes.py        # API endpoint tests
└── conftest.py               # Test configuration
```

## 📈 Monitoring & Logging

### Application Logging
- **Level**: INFO for production, DEBUG for development
- **Format**: JSON structured logging
- **Output**: Console and file rotation

### Performance Monitoring
- **Celery**: Flower dashboard at http://localhost:5555
- **MongoDB**: Built-in monitoring and profiling
- **Redis**: Redis CLI monitoring commands
- **Application**: Custom metrics endpoint

### Health Checks
- **Database Connectivity**: MongoDB ping
- **Queue Health**: Celery worker status
- **API Responsiveness**: Endpoint response times

## 🚢 Deployment

### Production Deployment

1. **Build and push containers**:
   ```bash
   docker-compose build
   docker-compose push
   ```

2. **Deploy to orchestration**:
   ```bash
   # Kubernetes example
   kubectl apply -f kubernetes/
   ```

3. **Configure production environment**:
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export MONGODB_URI=mongodb://production-mongodb:27017/situational_awareness
   export REDIS_URL=redis://production-redis:6379/0
   ```

### Scaling Considerations
- **Horizontal Scaling**: Multiple Celery workers
- **Database**: MongoDB replica sets
- **Caching**: Redis cluster for high availability
- **Load Balancing**: Multiple Flask instances behind load balancer

## 🔒 Security

### Data Protection
- **Encryption**: TLS for all external communications
- **Authentication**: API key authentication for external services
- **Authorization**: Role-based access control for internal APIs

### Vulnerability Management
- **Dependency Scanning**: Regular security updates
- **Code Analysis**: Static security analysis
- **Penetration Testing**: Regular security assessments

### Compliance
- **Data Retention**: Configurable retention policies
- **Audit Logging**: Comprehensive activity logging
- **Privacy**: Anonymization of personal data

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Code Standards
- **Python**: PEP 8 compliance
- **Documentation**: Google-style docstrings
- **Testing**: 80%+ test coverage
- **Type Hints**: Comprehensive type annotations

## 📞 Support

### Documentation
- This README
- API documentation at `/docs` endpoint
- Code comments and docstrings

### Issue Tracking
- GitHub Issues for bug reports
- Feature requests via Pull Requests
- Security vulnerabilities: security@example.com

### Community
- Discord channel for developers
- Regular community meetings
- Contributor recognition program

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Sri Lankan government open data initiatives
- Open source community contributions
- Research institutions supporting situational awareness
- Development team and contributors

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Status**: Production Ready