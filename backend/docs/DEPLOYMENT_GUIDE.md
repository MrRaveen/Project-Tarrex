# Deployment Guide

This guide covers the deployment of the Sri Lankan Situational Awareness Platform in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling Guidelines](#scaling-guidelines)
8. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites
- Python 3.11+
- MongoDB 5.0+
- Redis 7.0+
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/situational-awareness-platform.git
   cd situational-awareness-platform/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

5. **Start MongoDB and Redis**
   ```bash
   # Using Docker (recommended)
   docker run -d --name mongodb -p 27017:27017 mongo:5.0
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   
   # Or using system services
   # sudo systemctl start mongod
   # sudo systemctl start redis-server
   ```

6. **Set environment variables**
   ```bash
   export FLASK_ENV=development
   export MONGODB_URI=mongodb://localhost:27017/situational_awareness
   export REDIS_URL=redis://localhost:6379/0
   export NEWS_API_KEY=your_news_api_key
   export YOUTUBE_API_KEY=your_youtube_api_key
   export OPENWEATHER_API_KEY=your_weather_api_key
   export GOOGLE_TRENDS_API_KEY=your_trends_api_key
   ```

7. **Initialize the database**
   ```bash
   python -c "
   from app.config.mongo_config import get_database
   from app.model import *
   db = get_database()
   print('Database initialized successfully')
   "
   ```

8. **Start the application**
   ```bash
   # Terminal 1: Flask application
   flask run --host=0.0.0.0 --port=5000
   
   # Terminal 2: Celery worker
   celery -A app.celery worker --loglevel=info --concurrency=4
   
   # Terminal 3: Celery beat (scheduler)
   celery -A app.celery beat --loglevel=info
   
   # Terminal 4: Flower monitoring (optional)
   celery -A app.celery flower --port=5555
   ```

### Development Tools

- **Debugging**: Use Flask debug mode with `FLASK_DEBUG=1`
- **Testing**: Run tests with `python -m pytest tests/`
- **Code Quality**: Use `flake8` and `black` for linting and formatting

## Docker Deployment

### Single Container Setup

1. **Build the image**
   ```bash
   docker build -t situational-awareness-app .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Check services**
   ```bash
   docker-compose ps
   docker-compose logs -f app
   ```

### Multi-Container Production Setup

1. **Create production environment file**
   ```bash
   cat > .env.production << EOF
   FLASK_ENV=production
   MONGODB_URI=mongodb://mongodb:27017/situational_awareness
   REDIS_URL=redis://redis:6379/0
   NEWS_API_KEY=your_production_news_api_key
   YOUTUBE_API_KEY=your_production_youtube_api_key
   OPENWEATHER_API_KEY=your_production_weather_api_key
   GOOGLE_TRENDS_API_KEY=your_production_trends_api_key
   GUNICORN_WORKERS=4
   GUNICORN_THREADS=2
   CELERY_CONCURRENCY=4
   EOF
   ```

2. **Start production stack**
   ```bash
   docker-compose -f docker-compose.yml --env-file .env.production up -d
   ```

### Docker Compose Configuration

The `docker-compose.yml` file defines the following services:

- **app**: Flask application with Gunicorn
- **worker**: Celery worker for task processing
- **beat**: Celery beat for scheduled tasks
- **flower**: Celery monitoring dashboard
- **mongodb**: MongoDB database
- **redis**: Redis message broker

### Customizing Docker Deployment

**Resource Limits:**
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

**Health Checks:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/status/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (v1.23+)
- Helm (v3.0+)
- kubectl configured
- Persistent volume provisioner

### Helm Chart Setup

1. **Create values.yaml**
   ```yaml
   # situational-awareness/values.yaml
   replicaCount: 3
   
   image:
     repository: your-registry/situational-awareness-app
     tag: latest
     pullPolicy: Always
   
   service:
     type: LoadBalancer
     port: 5000
   
   ingress:
     enabled: true
     className: nginx
     hosts:
       - host: situational-awareness.your-domain.com
         paths:
           - path: /
             pathType: Prefix
   
   env:
     FLASK_ENV: production
     MONGODB_URI: mongodb://mongodb:27017/situational_awareness
     REDIS_URL: redis://redis:6379/0
   
   resources:
     limits:
       cpu: 1000m
       memory: 1Gi
     requests:
       cpu: 500m
       memory: 512Mi
   
   autoscaling:
     enabled: true
     minReplicas: 2
     maxReplicas: 10
     targetCPUUtilizationPercentage: 80
   ```

2. **Deploy with Helm**
   ```bash
   # Add MongoDB and Redis charts
   helm repo add bitnami https://charts.bitnami.com/bitnami
   
   # Install MongoDB
   helm install mongodb bitnami/mongodb \
     --set auth.enabled=false \
     --set persistence.size=10Gi
   
   # Install Redis
   helm install redis bitnami/redis \
     --set auth.enabled=false \
     --set master.persistence.size=5Gi
   
   # Install application
   helm install situational-awareness ./charts/situational-awareness \
     -f values.yaml
   ```

### Kubernetes Manifests

**Deployment Example:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: situational-awareness-app
  labels:
    app: situational-awareness
spec:
  replicas: 3
  selector:
    matchLabels:
      app: situational-awareness
  template:
    metadata:
      labels:
        app: situational-awareness
    spec:
      containers:
      - name: app
        image: your-registry/situational-awareness-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: MONGODB_URI
          value: "mongodb://mongodb:27017/situational_awareness"
        - name: REDIS_URL
          value: "redis://redis:6379/0"
        resources:
          limits:
            memory: "1Gi"
            cpu: "1000m"
          requests:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /status/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /status/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Production Checklist

### Before Deployment
- [ ] All tests pass (`python -m pytest tests/`)
- [ ] Code linting passes (`flake8 app/`)
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] Backup strategy defined
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Documentation updated

### Environment Configuration
- [ ] Production API keys configured
- [ ] Database connection strings verified
- [ SSL certificates provisioned
- [ ] CDN configured (if applicable)
- [ ] DNS records updated
- [ ] Firewall rules configured

### Deployment Process

1. **Build and test containers**
   ```bash
   docker-compose build
   docker-compose run app python -m pytest tests/
   ```

2. **Push to container registry**
   ```bash
   docker tag situational-awareness-app your-registry/situational-awareness-app:latest
   docker push your-registry/situational-awareness-app:latest
   ```

3. **Deploy to production**
   ```bash
   # Kubernetes
   kubectl apply -f kubernetes/production/
   
   # Or Docker Swarm
   docker stack deploy -c docker-compose.prod.yml situational-awareness
   ```

4. **Verify deployment**
   ```bash
   kubectl get pods
   kubectl get services
   curl https://your-domain.com/status/health
   ```

## Monitoring & Logging

### Application Metrics

**Key Metrics to Monitor:**
- API response times (p95, p99)
- Error rates (4xx, 5xx)
- Database query performance
- Celery task queue lengths
- Memory and CPU usage
- Network throughput

**Tools:**
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for logging
- Datadog or New Relic for APM

### Logging Configuration

**Structured Logging:**
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)
```

**Log Rotation:**
```yaml
# In docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Backup & Recovery

### Database Backup

**MongoDB Backup:**
```bash
# Daily backup script
mongodump --uri="mongodb://localhost:27017/situational_awareness" \
  --out=/backups/mongodb-$(date +%Y%m%d)

# Compress and upload
tar -czf /backups/mongodb-$(date +%Y%m%d).tar.gz /backups/mongodb-$(date +%Y%m%d)
aws s3 cp /backups/mongodb-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

**Redis Backup:**
```bash
# Redis RDB backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backups/redis-$(date +%Y%m%d).rdb
```

### Recovery Procedures

**Database Recovery:**
```bash
# MongoDB restore
mongorestore --uri="mongodb://localhost:27017/situational_awareness" \
  /backups/mongodb-latest/

# Redis restore
cp /backups/redis-latest.rdb /var/lib/redis/dump.rdb
redis-server --appendonly yes
```

**Application Recovery:**
1. Identify failed component
2. Check logs for root cause
3. Restart affected services
4. Verify data consistency
5. Monitor for recurrence

## Scaling Guidelines

### Horizontal Scaling

**Application Scaling:**
- Add more Flask application replicas
- Use load balancer with health checks
- Implement session affinity if needed

**Worker Scaling:**
- Scale Celery workers based on queue length
- Use autoscaling based on queue metrics
- Monitor worker resource usage

**Database Scaling:**
- MongoDB replica sets for read scaling
- Sharding for write scaling
- Use appropriate indexes

### Vertical Scaling

**Resource Limits:**
```yaml
# Kubernetes resource limits
resources:
  limits:
    cpu: "2000m"
    memory: "2Gi"
  requests:
    cpu: "1000m"
    memory: "1Gi"
```

### Performance Optimization

**Database Optimization:**
- Create appropriate indexes
- Use covered queries
- Implement connection pooling
- Monitor slow queries

**Application Optimization:**
- Implement caching (Redis)
- Use CDN for static assets
- Optimize database queries
- Implement pagination for large datasets

## Troubleshooting

### Common Issues

**Application Won't Start:**
- Check environment variables
- Verify database connectivity
- Check port availability

**Celery Tasks Not Processing:**
- Verify Redis connection
- Check worker status
- Review task queue configuration

**Database Connection Issues:**
- Verify connection string
- Check network connectivity
- Review authentication credentials

### Diagnostic Commands

**Kubernetes Diagnostics:**
```bash
# Get pod status
kubectl get pods

# View logs
kubectl logs deployment/situational-awareness-app

# Describe pod issues
kubectl describe pod situational-awareness-app-xyz

# Port forward for debugging
kubectl port-forward deployment/situational-awareness-app 5000:5000
```

**Docker Diagnostics:**
```bash
# Check container status
docker ps
docker stats

# View logs
docker logs situational-awareness-app

# Execute commands in container
docker exec -it situational-awareness-app bash
```

**Database Diagnostics:**
```bash
# MongoDB status
mongosh --eval "db.adminCommand({serverStatus: 1})"

# Redis status
redis-cli INFO
```

### Getting Help

1. **Check Documentation**: Review this guide and API reference
2. **View Logs**: Application, database, and system logs
3. **Community Support**: GitHub issues and discussions
4. **Professional Support**: Contact support@example.com

## Support

For deployment assistance:
- Email: deployment-support@example.com
- Documentation: https://docs.example.com/deployment
- Emergency: +94-11-123-4567 (Sri Lanka)

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready