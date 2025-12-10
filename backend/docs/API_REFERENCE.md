# API Reference Guide

## Overview
This document provides detailed information about all API endpoints available in the Sri Lankan Situational Awareness Platform.

## Base URL
All API endpoints are relative to the base URL:
- Development: `http://localhost:5000`
- Production: `https://your-production-domain.com`

## Authentication
Currently, the API uses simple API key authentication. Include the API key in the request header:
```
X-API-Key: your_api_key_here
```

## Response Format
All responses follow a consistent JSON format:
```json
{
    "status": "success|error",
    "data": {},
    "message": "Descriptive message",
    "timestamp": "2024-12-10T10:30:00Z"
}
```

## Endpoints

### Health & Status Endpoints

#### GET /status/health
Check system health and connectivity.

**Response:**
```json
{
    "status": "success",
    "data": {
        "flask": "healthy",
        "mongodb": "connected",
        "redis": "connected",
        "celery": "running",
        "timestamp": "2024-12-10T10:30:00Z"
    },
    "message": "System is healthy"
}
```

#### GET /status/queues
Get Celery queue status and worker information.

**Query Parameters:**
- `detailed` (boolean): Include detailed queue information

**Response:**
```json
{
    "status": "success",
    "data": {
        "queues": {
            "scraping": {
                "tasks": 5,
                "workers": 2,
                "status": "active"
            },
            "processing": {
                "tasks": 3,
                "workers": 2,
                "status": "active"
            },
            "analysis": {
                "tasks": 2,
                "workers": 2,
                "status": "active"
            }
        },
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

### Pipeline Control Endpoints

#### POST /scrape/run
Trigger the scraping pipeline to collect new data.

**Request Body:**
```json
{
    "sources": ["news", "weather", "prices", "tax", "youtube", "trends"],
    "force": false
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "task_id": "celery-task-uuid-1234",
        "sources": ["news", "weather", "prices"],
        "estimated_duration": "5 minutes",
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

#### POST /preprocess/run
Trigger the preprocessing pipeline.

**Request Body:**
```json
{
    "batch_size": 1000,
    "clean_text": true,
    "normalize": true
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "task_id": "celery-task-uuid-5678",
        "operations": ["cleaning", "normalization", "feature_engineering"],
        "estimated_duration": "3 minutes",
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

#### POST /analyze/run
Trigger the analysis pipeline.

**Request Body:**
```json
{
    "analyses": ["anomaly_detection", "trend_analysis", "clustering"],
    "lookback_days": 30
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "task_id": "celery-task-uuid-9012",
        "analyses": ["anomaly_detection", "trend_analysis"],
        "lookback_days": 30,
        "estimated_duration": "7 minutes",
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

### Data Access Endpoints

#### GET /indicators/latest
Get the latest situational indicators.

**Query Parameters:**
- `limit` (number): Number of results (default: 10)
- `type` (string): Filter by indicator type
- `min_confidence` (number): Minimum confidence score (0.0-1.0)

**Response:**
```json
{
    "status": "success",
    "data": {
        "indicators": [
            {
                "id": "indicator-001",
                "type": "economic",
                "value": 0.75,
                "confidence": 0.92,
                "description": "Food price stability indicator",
                "trend": "improving",
                "timestamp": "2024-12-10T10:00:00Z",
                "source": "food_prices"
            }
        ],
        "count": 1,
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

#### GET /risks/latest
Get current risk assessments.

**Query Parameters:**
- `severity` (string): Filter by risk severity (low, medium, high, critical)
- `category` (string): Filter by risk category
- `limit` (number): Number of results (default: 10)

**Response:**
```json
{
    "status": "success",
    "data": {
        "risks": [
            {
                "id": "risk-001",
                "severity": "medium",
                "category": "economic",
                "description": "Rising food inflation risk",
                "confidence": 0.85,
                "impact": 0.7,
                "timestamp": "2024-12-10T10:00:00Z",
                "mitigation": "Monitor price trends closely"
            }
        ],
        "count": 1,
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

#### GET /insights/overview
Get comprehensive insights overview.

**Query Parameters:**
- `timeframe` (string): Timeframe for insights (day, week, month)
- `limit` (number): Number of insights (default: 20)

**Response:**
```json
{
    "status": "success",
    "data": {
        "insights": [
            {
                "id": "insight-001",
                "type": "correlation",
                "title": "Weather patterns affecting food prices",
                "description": "Recent rainfall patterns show strong correlation with vegetable price fluctuations",
                "confidence": 0.88,
                "impact": "high",
                "timestamp": "2024-12-10T10:00:00Z",
                "sources": ["weather", "food_prices"],
                "recommendations": ["Increase vegetable storage capacity", "Diversify supply sources"]
            }
        ],
        "summary": {
            "total_insights": 15,
            "high_impact": 3,
            "trending_topics": ["food_security", "weather_impact", "economic_stability"]
        },
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

#### GET /trends
Get current trends across data types.

**Query Parameters:**
- `type` (string): Data type (news, weather, prices, tax, youtube, all)
- `lookback` (number): Lookback period in days (default: 30)
- `min_confidence` (number): Minimum trend confidence (0.0-1.0)

**Response:**
```json
{
    "status": "success",
    "data": {
        "trends": [
            {
                "id": "trend-001",
                "type": "price",
                "direction": "increasing",
                "strength": 0.82,
                "confidence": 0.91,
                "description": "Rice prices showing steady increase",
                "timeframe": "2 weeks",
                "impact": "medium",
                "timestamp": "2024-12-10T10:00:00Z",
                "related_indicators": ["food_inflation", "supply_chain"]
            }
        ],
        "summary": {
            "data_type": "prices",
            "lookback_days": 30,
            "trend_count": 8,
            "strong_trends": 3,
            "dominant_direction": "increasing"
        },
        "timestamp": "2024-12-10T10:30:00Z"
    }
}
```

## Error Responses

### Common Error Codes

| HTTP Code | Error Type | Description |
|-----------|------------|-------------|
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format
```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid parameter: limit must be between 1 and 100",
        "details": {
            "parameter": "limit",
            "value": 150,
            "constraints": "Must be between 1 and 100"
        }
    },
    "timestamp": "2024-12-10T10:30:00Z"
}
```

## Rate Limiting

- **General Endpoints**: 100 requests per minute
- **Data Processing Endpoints**: 10 requests per minute
- **Health Endpoints**: Unlimited

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1639141200
```

## Pagination

Endpoints returning multiple results support pagination:

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `per_page` (number): Items per page (default: 10, max: 100)

**Response Headers:**
```
X-Total-Count: 150
X-Total-Pages: 15
X-Current-Page: 1
X-Per-Page: 10
```

## Examples

### cURL Examples

**Health Check:**
```bash
curl -X GET "http://localhost:5000/status/health" \
  -H "X-API-Key: your_api_key_here"
```

**Get Latest Indicators:**
```bash
curl -X GET "http://localhost:5000/indicators/latest?limit=5&min_confidence=0.8" \
  -H "X-API-Key: your_api_key_here"
```

**Trigger Scraping:**
```bash
curl -X POST "http://localhost:5000/scrape/run" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"sources": ["news", "weather"], "force": true}'
```

### Python Examples

```python
import requests

# Health check
response = requests.get(
    "http://localhost:5000/status/health",
    headers={"X-API-Key": "your_api_key_here"}
)
print(response.json())

# Get trends
response = requests.get(
    "http://localhost:5000/trends",
    params={"type": "prices", "lookback": 7},
    headers={"X-API-Key": "your_api_key_here"}
)
data = response.json()
print(f"Found {len(data['data']['trends'])} price trends")
```

## Changelog

### Version 1.0.0 (2024-12-10)
- Initial API release
- All core endpoints implemented
- Basic authentication and rate limiting
- Comprehensive error handling
- Pagination support for data endpoints

## Support

For API support and questions:
- Email: api-support@example.com
- Documentation: https://docs.example.com
- Issue Tracker: GitHub Issues