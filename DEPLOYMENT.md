# Bureaucracy Navigator Agent - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Bureaucracy Navigator Agent system to production.

## Architecture

- **Backend**: FastAPI with Python
- **Frontend**: Next.js with TypeScript
- **Database**: SQLite (development), PostgreSQL (production recommended)
- **Vector Database**: Chroma
- **Cache**: Redis
- **Deployment**: Docker with Docker Compose

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Required API Keys**
   - OpenAI API Key (for LLM operations)
   - SerpAPI Key (for web search)

3. **Domain Name** (for production SSL)
   - Purchase a domain name
   - Configure DNS to point to your server

## Environment Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Bureaucracy_Navigator
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit environment variables
   nano .env
   ```
   
   Update the following variables:
   ```env
   OPENAI_API_KEY=your_actual_openai_key
   SERPAPI_KEY=your_actual_serpapi_key
   DATABASE_URL=postgresql://user:password@localhost:5432/bureaucracy_db  # Production
   NEXT_PUBLIC_API_URL=https://yourdomain.com  # Production
   ```

## Development Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# Initialize demo data
docker-compose exec backend python app/core/demo_data.py

# View logs
docker-compose logs -f
```

### Services Available

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (as above)
# Install Docker Compose (as above)

# Create application directory
sudo mkdir -p /opt/bureaucracy-navigator
sudo chown $USER:$USER /opt/bureaucracy-navigator
cd /opt/bureaucracy-navigator
```

### 2. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Setup auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Production Configuration

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SERPAPI_KEY=${SERPAPI_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/bureaucracy_db
      - REDIS_URL=redis://redis:6379
    volumes:
      - backend_data:/app/chroma_db
      - backend_uploads:/app/uploads
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - bureaucracy-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=https://yourdomain.com
    restart: unless-stopped
    networks:
      - bureaucracy-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=bureaucracy_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - bureaucracy-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - bureaucracy-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - bureaucracy-network

volumes:
  backend_data:
  backend_uploads:
  postgres_data:
  redis_data:

networks:
  bureaucracy-network:
    driver: bridge
```

### 4. Nginx Configuration

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS configuration
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL certificates
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        # SSL settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend docs
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Deploy to Production

```bash
# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Initialize database (if using PostgreSQL)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Initialize demo data
docker-compose -f docker-compose.prod.yml exec backend python app/core/demo_data.py
```

## Cloud Deployment Options

### Render (Recommended for Backend)

1. **Backend Deployment**
   - Connect GitHub repository
   - Set environment variables in Render dashboard
   - Use Dockerfile
   - Deploy to `https://your-app.onrender.com`

2. **Database**
   - Create PostgreSQL database on Render
   - Update `DATABASE_URL` environment variable

### Vercel (Recommended for Frontend)

1. **Frontend Deployment**
   - Connect GitHub repository
   - Set environment variables:
     - `NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com`
   - Deploy to `https://your-app.vercel.app`

### Railway (Alternative)

1. **Deploy with Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Deploy
   railway up
   ```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Health check endpoints
curl https://yourdomain.com/api/v1/health
```

### Backup Strategy

```bash
# Backup database
docker-compose exec db pg_dump -U postgres bureaucracy_db > backup.sql

# Backup Chroma data
tar -czf chroma_backup.tar.gz backend_data/

# Backup uploaded files
tar -czf uploads_backup.tar.gz backend_uploads/
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml up -d --build

# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify environment variables are set correctly
   - Check API key validity and quotas

2. **Database Connection Issues**
   - Verify database is running
   - Check connection string format
   - Ensure database migrations are run

3. **Frontend Build Issues**
   - Clear node_modules and reinstall
   - Check environment variables
   - Verify API URL is accessible

4. **Chroma Vector Database Issues**
   - Check disk space
   - Verify permissions on data directory
   - Restart Chroma service

### Performance Optimization

1. **Backend Optimization**
   - Enable Redis caching
   - Use connection pooling
   - Implement request rate limiting

2. **Frontend Optimization**
   - Enable Next.js production optimizations
   - Implement image optimization
   - Use CDN for static assets

## Security Considerations

1. **API Security**
   - Use HTTPS in production
   - Implement rate limiting
   - Validate all inputs
   - Use environment variables for secrets

2. **Database Security**
   - Use strong passwords
   - Limit database access
   - Regular backups
   - Enable audit logging

3. **File Upload Security**
   - Validate file types
   - Scan for malware
   - Limit file sizes
   - Use secure storage

## Scaling

### Horizontal Scaling

1. **Load Balancing**
   - Use multiple backend instances
   - Configure Nginx load balancing
   - Implement session affinity

2. **Database Scaling**
   - Read replicas for read-heavy workloads
   - Connection pooling
   - Database sharding if needed

### Vertical Scaling

1. **Resource Allocation**
   - Increase CPU/RAM for containers
   - Optimize database queries
   - Use caching strategies

## Support

For deployment issues:
1. Check logs for error messages
2. Verify environment configuration
3. Test individual services
4. Consult documentation
5. Create GitHub issue with details
