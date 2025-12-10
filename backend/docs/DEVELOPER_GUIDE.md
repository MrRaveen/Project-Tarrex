# Developer Guide

This guide provides comprehensive information for developers working on the Sri Lankan Situational Awareness Platform.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Data Models](#data-models)
5. [API Development](#api-development)
6. [Task Development](#task-development)
7. [Testing](#testing)
8. [Debugging](#debugging)
9. [Performance Optimization](#performance-optimization)
10. [Contributing Guidelines](#contributing-guidelines)

## Development Environment Setup

### Prerequisites
- Python 3.11+
- MongoDB 5.0+
- Redis 7.0+
- Docker and Docker Compose (optional)
- Git

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/situational-awareness-platform.git
   cd situational-awareness-platform/backend
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Start services with Docker**
   ```bash
   docker-compose up -d mongodb redis
   ```

### IDE Configuration

**VS Code Recommended Settings:**
```json
{
    "python.defaultInterpreterPath": "venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

**PyCharm Configuration:**
- Set Python interpreter to venv
- Enable Black formatter
- Configure flake8 for linting
- Set up Django-style templates for Flask

## Project Structure

### Core Modules

```
app/
├── config/           # Application configuration
│   ├── app_config.py     # Flask app configuration
│   ├── celery_app.py     # Celery configuration
│   ├── mongo_config.py   # MongoDB connection
│   └── settings.py       # Application settings
├── ml/               # Machine learning models
│   ├── anomaly_detector.py  # Anomaly detection
│   ├── clustering_engine.py # Data clustering
│   ├── feature_engineer.py  # Feature engineering
│   ├── trend_analyzer.py   # Trend analysis
│   └── trend_scorer.py     # Trend scoring
├── model/            # Data models (Pydantic)
│   ├── indicator_model.py  # Indicator model
│   ├── insight_model.py    # Insight model
│   ├── news_model.py       # News model
│   ├── pricing_model.py    # Pricing model
│   ├── risk_model.py       # Risk model
│   ├── tax_model.py        # Tax model
│   ├── trends_model.py     # Trends model
│   ├── weather_model.py    # Weather model
│   └── youtube_model.py    # YouTube model
├── modules/          # Business logic modules
│   ├── ScrapModule/       # Data collection
│   ├── ingestionLayer/    # Data ingestion
│   └── preprocessingLayer/ # Data preprocessing
├── routes/           # API routes
│   └── api_routes.py     # REST API endpoints
├── service/          # Service layer
│   ├── general/         # General services
│   └── tasks/          # Celery tasks
└── __init__.py       # Application factory
```

### Key Design Patterns

1. **Repository Pattern**: Data access abstraction
2. **Service Layer**: Business logic encapsulation
3. **Factory Pattern**: Application component creation
4. **Strategy Pattern**: Algorithm selection
5. **Observer Pattern**: Event handling

## Coding Standards

### Python Style Guide

**PEP 8 Compliance:**
- 4 spaces for indentation
- 79 character line limit
- Use descriptive variable names
- Follow import order: stdlib, third-party, local

**Naming Conventions:**
- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_private` (single underscore)

### Code Organization

**File Structure:**
```python
# Standard file structure
"""
Module docstring describing purpose and usage.
"""

# imports: stdlib, third-party, local
import os
import sys
from typing import List, Dict, Optional

# constants
DEFAULT_TIMEOUT = 30

# classes
class MyClass:
    """Class docstring."""
    
    # class variables
    class_var = "value"
    
    def __init__(self, param: str):
        """Initialize with parameter."""
        self.param = param
    
    def public_method(self) -> str:
        """Public method docstring."""
        return self._private_method()
    
    def _private_method(self) -> str:
        """Private method docstring."""
        return self.param.upper()

# functions
def module_function(param: int) -> bool:
    """Function docstring."""
    return param > 0

# main guard
if __name__ == "__main__":
    # test code here
    pass
```

### Type Hints

**Comprehensive Type Annotations:**
```python
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel

def process_data(
    data: List[Dict[str, Any]],
    options: Optional[Dict[str, Union[str, int]]] = None
) -> Dict[str, Any]:
    """Process data with optional options."""
    options = options or {}
    return {"processed": True, "data": data}

class DataModel(BaseModel):
    """Pydantic model for data validation."""
    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = []
```

### Documentation Standards

**Google Style Docstrings:**
```python
class DataProcessor:
    """Processes various types of data for situational awareness.
    
    This class handles data processing including cleaning, normalization,
    and feature extraction specific to Sri Lankan context.
    
    Attributes:
        config: Configuration dictionary for processing options
        logger: Logger instance for logging processing events
    """
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process the input data through the processing pipeline.
        
        Args:
            data: Input DataFrame containing raw data
            
        Returns:
            Processed DataFrame with cleaned and normalized data
            
        Raises:
            ValueError: If data is empty or invalid
            ProcessingError: If processing fails
        """
        # Implementation here
        return processed_data
```

## Data Models

### Pydantic Models

**Base Model Structure:**
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class NewsArticle(BaseModel):
    """Model for news article data."""
    
    id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title", max_length=500)
    content: str = Field(..., description="Article content")
    source: str = Field(..., description="News source")
    published_at: datetime = Field(..., description="Publication timestamp")
    categories: List[str] = Field(default=[], description="Article categories")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    
    @validator('sentiment_score')
    def validate_sentiment(cls, v):
        """Validate sentiment score range."""
        if v is not None and (v < -1 or v > 1):
            raise ValueError('Sentiment score must be between -1 and 1')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### MongoDB Integration

**Repository Pattern Example:**
```python
from pymongo import MongoClient
from typing import List, Optional
from .news_model import NewsArticle

class NewsRepository:
    """Repository for news article data access."""
    
    def __init__(self, db):
        self.collection = db.news_articles
        # Create indexes
        self.collection.create_index([("published_at", -1)])
        self.collection.create_index([("source", 1)])
        self.collection.create_index([("categories", 1)])
    
    async def save_article(self, article: NewsArticle) -> str:
        """Save a news article to database."""
        result = await self.collection.insert_one(article.dict())
        return str(result.inserted_id)
    
    async def get_articles(
        self,
        source: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[NewsArticle]:
        """Get news articles with optional filtering."""
        query = {}
        if source:
            query["source"] = source
        
        cursor = self.collection.find(query).sort("published_at", -1).skip(skip).limit(limit)
        return [NewsArticle(**doc) async for doc in cursor]
```

## API Development

### Route Development

**Flask Blueprint Example:**
```python
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from app.service.news_service import NewsService
from app.model.news_model import NewsArticle

news_bp = Blueprint('news', __name__, url_prefix='/news')
logger = logging.getLogger(__name__)

@news_bp.route('/articles', methods=['GET'])
def get_articles():
    """Get paginated news articles.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        source: Filter by news source
        category: Filter by category
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        source = request.args.get('source')
        category = request.args.get('category')
        
        service = NewsService()
        articles, total = service.get_articles(
            page=page,
            per_page=per_page,
            source=source,
            category=category
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'articles': [article.dict() for article in articles],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        })
    
    except ValueError as e:
        logger.warning(f"Invalid query parameters: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Invalid query parameters',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Internal server error'
        }), 500
```

### Error Handling

**Custom Error Handlers:**
```python
from flask import jsonify
from werkzeug.exceptions import HTTPException

class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}

def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors."""
        return jsonify({
            'status': 'error',
            'error': 'Validation failed',
            'message': str(error),
            'details': error.details
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'status': 'error',
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'status': 'error',
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
```

## Task Development

### Celery Task Patterns

**Task with Retry Logic:**
```python
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
import logging
from typing import Dict, Any

from app.modules.ScrapModule.news_collector import NewsCollector
from app.modules.ingestionLayer.data_ingestor import DataIngestor

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    queue='scraping'
)
def scrape_news_task(self, sources: List[str] = None) -> Dict[str, Any]:
    """Task to scrape news from specified sources.
    
    Args:
        sources: List of news sources to scrape
        
    Returns:
        Dictionary with scraping results
    """
    try:
        collector = NewsCollector()
        ingestor = DataIngestor()
        
        # Scrape news from sources
        articles = collector.scrape_news(sources or ['daily_mirror', 'news_first'])
        
        # Ingest articles into database
        result = ingestor.ingest_news_articles(articles)
        
        logger.info(f"Scraped {len(articles)} news articles from {sources}")
        
        return {
            'status': 'success',
            'articles_scraped': len(articles),
            'articles_ingested': result['ingested_count'],
            'sources': sources
        }
        
    except Exception as exc:
        logger.error(f"News scraping failed: {exc}")
        
        # Retry the task
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.critical(f"News scraping failed after {self.max_retries} retries")
            return {
                'status': 'error',
                'error': str(exc),
                'sources': sources
            }
```

### Task Chaining

**Workflow Orchestration:**
```python
from celery import chain, group
from .scraping_tasks import scrape_news_task, scrape_weather_task
from .processing_tasks import preprocess_data_task
from .analysis_tasks import analyze_trends_task

def create_data_pipeline() -> chain:
    """Create data processing pipeline chain."""
    
    # Scrape data from multiple sources in parallel
    scrape_tasks = group([
        scrape_news_task.s(),
        scrape_weather_task.s(),
        # Add more scraping tasks
    ])
    
    # Process and analyze data sequentially
    pipeline = chain(
        scrape_tasks,
        preprocess_data_task.s(),
        analyze_trends_task.s()
    )
    
    return pipeline

# Usage
pipeline = create_data_pipeline()
result = pipeline.apply_async()
```

## Testing

### Test Structure

**Test File Organization:**
```python
# tests/test_news_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.service.news_service import NewsService
from app.model.news_model import NewsArticle

class TestNewsService:
    """Test cases for NewsService."""
    
    @pytest.fixture
    def news_service(self):
        """Create NewsService instance for testing."""
        return NewsService()
    
    @pytest.fixture
    def sample_articles(self):
        """Create sample news articles for testing."""
        return [
            NewsArticle(
                id="1",
                title="Test Article 1",
                content="Test content 1",
                source="test_source",
                published_at=datetime.now() - timedelta(hours=1),
                categories=["test"],
                sentiment_score=0.5
            ),
            NewsArticle(
                id="2",
                title="Test Article 2",
                content="Test content 2",
                source="test_source",
                published_at=datetime.now() - timedelta(hours=2),
                categories=["test"],
                sentiment_score=-0.2
            )
        ]
    
    def test_get_articles_pagination(self, news_service, sample_articles):
        """Test article pagination functionality."""
        with patch.object(news_service.repository, 'get_articles') as mock_get:
            mock_get.return_value = (sample_articles, 2)
            
            articles, total = news_service.get_articles(page=1, per_page=2)
            
            assert len(articles) == 2
            assert total == 2
            mock_get.assert_called_once_with(page=1, per_page=2, source=None, category=None)
    
    def test_calculate_sentiment_stats(self, news_service, sample_articles):
        """Test sentiment statistics calculation."""
        stats = news_service.calculate_sentiment_stats(sample_articles)
        
        assert stats['count'] == 2
        assert stats['average'] == pytest.approx(0.15)
        assert stats['positive_count'] == 1
        assert stats['negative_count'] == 1
```

### Mocking and Fixtures

**Advanced Testing Patterns:**
```python
@pytest.fixture
def mock_news_repository():
    """Mock news repository for testing."""
    with patch('app.service.news_service.NewsRepository') as mock:
        instance = mock.return_value
        instance.get_articles.return_value = ([], 0)
        instance.save_article.return_value = "test_id"
        yield instance

@patch('app.service.news_service.requests')
def test_fetch_external_news(mock_requests, news_service):
    """Test external news fetching with mocked requests."""
    # Mock API response
    mock_response = Mock()
    mock_response.json.return_value = {
        'articles': [
            {
                'title': 'External News',
                'content': 'External content',
                'source': 'external',
                'publishedAt': '2024-01-01T00:00:00Z'
            }
        ]
    }
    mock_requests.get.return_value = mock_response
    
    articles = news_service.fetch_external_news()
    
    assert len(articles) == 1
    assert articles[0].title == 'External News'
    mock_requests.get.assert_called_once_with(
        'https://newsapi.org/v2/top-headlines',
        params={'country': 'lk', 'apiKey': 'test_key'}
    )
```

## Debugging

### Debugging Techniques

**Logging Configuration:**
```python
import logging
import structlog

# Structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Usage with context
logger.info("processing_data", 
    data_count=len(data), 
    source="news", 
    operation="cleaning"
)
```

**Debugging in Development:**
```python
# Use breakpoints with debugpy
import debugpy

def start_debugging():
    """Start debugger in development mode."""
    if os.getenv('FLASK_ENV') == 'development':
        debugpy.listen(('0.0.0.0', 5678))
        print("Debugger attached on port 5678")

# Add to application startup
start_debugging()
```

### Performance Profiling

**Simple Profiling Decorator:**
```python
import time
from functools import wraps

def profile_function(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

# Usage
@profile_function
def expensive_operation(data):
    # Implementation
    return processed_data
```

## Performance Optimization

### Database Optimization

**Indexing Strategy:**
```python
# Create appropriate indexes
async def create_indexes(db):
    """Create necessary database indexes."""
    
    # News articles
    await db.news_articles.create_index([("published_at", -1)])
    await db.news_articles.create_index([("source", 1)])
    await db.news_articles.create_index([("categories", 1)])
    await db.news_articles.create_index([("sentiment_score", -1)])
    
    # Compound indexes for common queries
    await db.news_articles.create_index([
        ("source", 1),
        ("published_at", -1)
    ])
    
    # Text search index
    await db.news_articles.create_index([
        ("title", "text"),
        ("content", "text")
    ])
```

### Memory Management

**Efficient Data Processing:**
```python
import pandas as pd
from typing import Iterator

def process_large_dataset(filename: str) -> Iterator[pd.DataFrame]:
    """Process large dataset in chunks to avoid memory issues."""
    
    chunk_size = 10000  # Process 10k rows at a time
    
    for chunk in pd.read_csv(filename, chunksize= chunk_size):
        # Process chunk
        processed_chunk = process_data_chunk(chunk)
        yield processed_chunk

# Usage
for chunk in process_large_dataset("large_dataset.csv"):
    save_to_database(chunk)
```

## Contributing Guidelines

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow coding standards and add tests
4. **Run tests**: `python -m pytest tests/ --cov=app`
5. **Update documentation**: Ensure README and docstrings are updated
6. **Commit changes**: Use conventional commit messages
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**: Provide detailed description

### Commit Message Convention

**Format:** `type(scope): description`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test-related changes
- `chore`: Maintenance tasks

**Examples:**
- `feat(news): add news sentiment analysis`
- `fix(api): fix pagination bug in articles endpoint`
- `docs: update deployment guide`

### Code Review Process

1. **Self-review**: Review your own code first
2. **Test coverage**: Ensure adequate test coverage
3. **Documentation**: Verify documentation is complete
4. **Performance**: Check for performance implications
5. **Security**: Review for security vulnerabilities
6. **Style compliance**: Verify PEP 8 and project standards

### Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time developer discussions
- **Email**: dev-support@example.com
- **Documentation**: https://docs.example.com/development

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Active Development