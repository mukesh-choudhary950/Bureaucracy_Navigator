# 🚀 Bureaucracy Navigator Frontend

A **React-based frontend** for the AI-powered Bureaucracy Navigator system with autonomous workflow automation.

## ✨ Features

- 🤖 **AI Process Analysis** - Query government procedures with AI
- 📊 **Task Assignment Dashboard** - AI-powered task distribution
- 🔄 **Workflow Tracking** - Real-time progress monitoring
- 👥 **Smart Insights** - AI recommendations for optimization
- 🎯 **Multi-Agent System** - Autonomous task assignment
- 📱 **Responsive Design** - Works on all devices

## 🏗️ Architecture

```
React Frontend
    ↓
FastAPI Backend (Groq API)
    ↓
ChromaDB Vector Store
    ↓
HuggingFace Embeddings
    ↓
Government Process Intelligence
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Login**: Use any name + "demo123" password

## 📁 Frontend Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── contexts/           # React context providers
│   ├── pages/              # Main application pages
│   ├── main.jsx           # Application entry point
│   └── styles.css          # Tailwind CSS styles
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── postcss.config.js       # PostCSS configuration
```

## 📋 Pages & Features

### **1. Dashboard** (`/`)
- **Quick Actions** - Common government process queries
- **Statistics** - Task completion metrics
- **Recent Activity** - AI analysis history
- **Custom Query** - Free-form process questions

### **2. Process Search** (`/search`)
- **AI Query Input** - Natural language questions
- **Real-time Analysis** - Groq API integration
- **Source Attribution** - Document references
- **Confidence Scores** - AI response reliability

### **3. Task Assignment** (`/tasks`)
- **Task Statistics** - Completed, in-progress, pending, delayed
- **Smart Assignment** - AI-powered employee matching
- **Priority Management** - High, medium, low priority
- **Reassignment Logic** - AI recommendations for bottlenecks

### **4. Workflow Tracker** (`/workflow`)
- **Progress Visualization** - Real-time workflow status
- **Step-by-Step Tracking** - Individual task monitoring
- **AI Insights** - Bottleneck detection and optimization
- **Historical Analysis** - Performance comparisons

### **5. Login** (`/login`)
- **Role Selection** - Manager, Legal, Compliance, Finance, Operations
- **Department Assignment** - Team organization
- **Demo Access** - Quick testing credentials

## 🎯 Key Features

### **AI-Powered Components**

#### **Query Analysis**
- Natural language processing
- Government procedure identification
- Step-by-step breakdown
- Source document retrieval
- Confidence scoring

#### **Task Assignment**
- Skill-based employee matching
- Workload balancing
- Priority optimization
- Automated reassignment suggestions

#### **Workflow Monitoring**
- Real-time progress tracking
- Bottleneck detection
- Performance analytics
- Predictive completion estimates

## 🎨 Design System

### **Technology Stack**
- **React 18** - Component framework
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Vite** - Build tool

### **UI/UX Principles**
- **Mobile-First** - Responsive design
- **Accessibility** - WCAG compliant
- **Performance** - Optimized loading
- **Intuitive** - Clear navigation and actions

## 🔧 Configuration

### **Environment Variables**
```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# Development Mode
VITE_DEV_MODE=true
```

### **Customization**
```javascript
// src/contexts/QueryContext.jsx
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
}
```

## 🎭 Demo Credentials

For quick testing and demonstration:

| Role | Username | Password |
|-------|----------|---------|
| Manager | John Manager | demo123 |
| Legal Team | Sarah Chen | demo123 |
| Compliance | Mike Johnson | demo123 |
| Finance | Alex Kumar | demo123 |
| Operations | Priya Singh | demo123 |

## 📊 AI Integration

### **Backend Connection**
- **Groq API** - Llama 3 8B model
- **ChromaDB** - Vector search integration
- **Auto-Loading** - Government document scraping
- **Real-time Updates** - Live workflow status

### **Smart Features**
- **Auto-Assignment** - AI suggests optimal task distribution
- **Delay Detection** - Identifies workflow bottlenecks
- **Optimization Tips** - Performance improvement recommendations
- **Confidence Scoring** - AI response reliability metrics

## 🚀 Production Deployment

### **Build Commands**
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### **Environment Setup**
```bash
# Production variables
VITE_API_URL=https://your-api-domain.com
VITE_DEV_MODE=false
```

## 🎉 Benefits

- **🤖 AI-First** - Every feature powered by AI intelligence
- **🔄 Autonomous** - Minimal human intervention required
- **📊 Data-Driven** - Real-time analytics and insights
- **🎯 Process-Oriented** - Designed for government workflows
- **🌐 Scalable** - Handles multiple concurrent workflows
- **📱 User-Friendly** - Intuitive interface for all users

**Your Bureaucracy Navigator Frontend is ready for production!** 🚀
