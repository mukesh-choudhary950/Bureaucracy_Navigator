# 🚀 Bureaucracy Navigator - Complete Deployment Guide

## 📋 Deployment Overview

Deploy your **AI-powered Bureaucracy Navigator** with autonomous workflow automation from development to production.

---

## 🎯 Prerequisites

### **System Requirements**
- **Node.js 18+** - Frontend development
- **Python 3.8+** - Backend runtime
- **Git** - Version control (recommended)

### **API Keys Required**
- **Groq API Key** - Free tier available at https://console.groq.com/

---

## 📁 Project Structure

```
Bureaucracy_Navigator/
├── backend/                 # FastAPI + Groq + ChromaDB
├── frontend/                # React + Tailwind + Vite
├── .env.example             # Environment template
└── .env.local               # Local environment (create from .env.example)
```

---

## 🐳 Step 1: Local Development Setup

### **System Requirements**
- **Node.js 18+** - Frontend development
- **Python 3.8+** - Backend runtime
- **Git** - Version control (recommended)

### **API Keys Required**
- **Groq API Key** - Free tier available at https://console.groq.com/

---

## 📁 Project Structure

```
Bureaucracy_Navigator/
├── backend/                 # FastAPI + Groq + ChromaDB
├── frontend/                # React + Tailwind + Vite
├── .env.example             # Environment template
└── .env.local               # Local environment (create from .env.example)
```

---

## 🐳 Step 2: Backend Setup

### **Create Virtual Environment**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file from template
cp .env.example .env.local

# Edit environment file
notepad .env.local
```

**Required .env.local Variables:**
```bash
# Groq API Key (Get from https://console.groq.com/)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_DIR=./uploads

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Environment
ENVIRONMENT=development

# Security
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO
```

### **Start Backend Server**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🐳 Step 3: Frontend Setup

### **Install Dependencies**
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Create frontend environment file
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

### **Start Frontend Development**
```bash
# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
# Backend API should be running at http://localhost:8000
```

---

## 🐳 Step 4: Integration Testing

### **Test Backend API**
```bash
# Test health endpoint
curl http://localhost:8000/

# Test auto-load status
curl http://localhost:8000/init-status

# Test AI query endpoint
curl -X POST "http://localhost:8000/api/v1/query/ask-simple" \
  -H "Content-Type: application/json" \
  -d '{"question": "How to apply for business license?"}'
```

### **Test Frontend Integration**
1. **Open browser** to http://localhost:3000
2. **Test login** with any name + "demo123" password
3. **Test AI queries** in the Process Search page
4. **Verify API calls** are working through browser dev tools

---

## 🐳 Step 5: Production Preparation

### **Production Environment**
```bash
# Create production environment file
cp .env.example .env.production

# Edit production environment
notepad .env.production
```

**Production .env.production Variables:**
```bash
# Production API Keys
GROQ_API_KEY=gsk_production_groq_key

# Production Database
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
UPLOAD_DIR=/app/uploads

# Production Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Production Origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production Logging
LOG_LEVEL=WARNING
```

### **Build for Production**
```bash
# Backend - No changes needed (Python runs directly)
# Frontend build
cd frontend
npm run build
```

---

## 🐳 Step 6: Simple Production Deployment

### **Option 1: Direct Server Deployment**

#### **Backend Production Server**
```bash
# Navigate to backend
cd backend

# Activate production environment
# Set environment variable for production
set ENVIRONMENT=production

# Start with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### **Frontend Static Files**
```bash
# Navigate to frontend
cd frontend

# Build for production
npm run build

# Serve static files with any web server
# Option 1: Python simple server
cd dist
python -m http.server 80

# Option 2: Nginx (recommended)
# Install nginx and configure to serve dist/ folder
```

### **Option 2: Cloud Platform Deployment**

#### **Preparation**
```bash
# Create production build
cd frontend && npm run build

# Prepare backend for cloud
cd backend
# Ensure all dependencies are in requirements.txt
# Test production locally with production environment variables
```

#### **AWS EC2 Deployment**
```bash
# 1. Create EC2 instance
aws ec2 run-instances \
    --image-id ami-0c55b63cb \
    --instance-type t3.micro \
    --key-name bureaucracy-key \
    --security-group-ids sg-12345678 \
    --user-data file://setup-script.sh

# 2. Setup instance (run commands from setup-script.sh)
ssh -i bureaucracy-key.pem ec2-user@your-instance-ip

# 3. Deploy applications
git clone https://github.com/your-repo.git
cd Bureaucracy-Navigator

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.production .env
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend setup (on same instance)
cd frontend
npm install
npm run build
# Serve with nginx or Apache
```

#### **Google Cloud Run**
```bash
# Deploy backend
gcloud run deploy bureaucracy-navigator-backend \
    --source . \
    --region us-central1 \
    --platform managed \
    --set-env-vars GROQ_API_KEY=$GROQ_API_KEY,ENVIRONMENT=production \
    --allow-unauthenticated
```

---

## 🐳 Step 7: Domain & SSL Setup

### **Domain Configuration**
```bash
# DNS Configuration
# A Record: yourdomain.com → YOUR_SERVER_IP
# CNAME: www.yourdomain.com → yourdomain.com

# SSL Certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
sudo systemctl reload nginx
```

---

## 🐳 Step 8: Monitoring & Maintenance

### **Production Monitoring**
```bash
# Backend monitoring with supervisor
sudo apt install supervisor
echo "[program:bureaucracy]" > /etc/supervisor/conf.d/bureaucracy.conf
echo "command=uvicorn app.main:app --host 0.0.0.0 --port 8000" >> /etc/supervisor/conf.d/bureaucracy.conf
echo "directory=/app" >> /etc/supervisor/conf.d/bureaucracy.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start bureaucracy

# Log monitoring
tail -f /var/log/bureaucracy/app.log

# Health check endpoint
curl -f https://api.yourdomain.com/health
```

### **Database Backups**
```bash
# ChromaDB backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf chroma_backup_$DATE.tar.gz chroma_db/
aws s3 cp chroma_backup_$DATE.tar.gz s3://your-backups/  # If using S3
```

---

## 🐳 Step 9: Troubleshooting

### **Common Issues & Solutions**

#### **Backend Issues**
```bash
# Port already in use
sudo netstat -tulpn | grep :8000
sudo kill -9 PID

# Permission denied
sudo chmod +x start.sh
./start.sh

# Database connection issues
python -c "from app.core.config import settings; print('Database:', settings.DATABASE_URL)"
```

#### **Frontend Issues**
```bash
# Build fails
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# API connection errors
# Check VITE_API_URL in .env.local
echo "Checking API connection..."
curl http://localhost:8000/health
```

---

## 🎯 Production Checklist

### **Pre-Deployment**
- [ ] **Local testing complete** - All features working
- [ ] **Environment configured** - Production variables set
- [ ] **Security reviewed** - No hardcoded secrets
- [ ] **Performance tested** - Load testing completed
- [ ] **Backup plan ready** - Data protection strategy
- [ ] **Rollback procedure** - Quick recovery documented

### **Post-Deployment**
- [ ] **Health checks passing** - All services responding
- [ ] **Monitoring active** - Logs and metrics working
- [ ] **SSL configured** - HTTPS working correctly
- [ ] **Domain resolving** - DNS pointing correctly
- [ ] **Load testing** - Performance under stress
- [ ] **User acceptance** - Production sign-off received

---

## 🚀 Quick Start Commands

### **Development**
```bash
# Start both services (in separate terminals)
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload

cd frontend && npm run dev
```

### **Production**
```bash
# Using production environment
export ENVIRONMENT=production

# Start production server
cd backend && source venv/bin/activate && uvicorn app.main:app --workers 4
```

**Your Bureaucracy Navigator is ready for local development and production deployment!** 🎉
