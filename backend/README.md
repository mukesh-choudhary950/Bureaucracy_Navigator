# 🚀 Bureaucracy Navigator Agent

A **FastAPI-based RAG system** for answering questions about government procedures using **Groq API** and **local embeddings**.

## ✨ Features

- 🤖 **RAG Pipeline** - Retrieval-Augmented Generation
- 🆓 **Free Groq API** - Llama 3 8B model for answers
- 🔒 **Local Embeddings** - HuggingFace sentence-transformers
- 📊 **ChromaDB** - Vector database for document storage
- 🔄 **Auto-Loading** - Scrapes government websites automatically
- 📄 **Document Upload** - Support for PDF, images, text files

## 🏗️ Architecture

```
User Question
    ↓
HuggingFace Embeddings (Local)
    ↓
ChromaDB Vector Search
    ↓
Retrieve Document Chunks
    ↓
Groq API (Llama 3 8B)
    ↓
Generated Answer
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env with your API keys
GROQ_API_KEY=gsk_your_groq_api_key_here
```

**Get Groq API Key**: https://console.groq.com/

### 3. Start Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Access API
- **Swagger UI**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/
- **Init Status**: http://127.0.0.1:8000/init-status

## 📋 API Endpoints

### **Query Endpoints**

#### **POST /api/v1/query/ask-simple** - Ask Questions
```json
{
  "question": "How to apply for income certificate in Telangana?",
  "max_results": 5
}
```

#### **POST /api/v1/query/search** - Search Documents
```json
{
  "query": "passport application",
  "max_results": 5
}
```

#### **GET /api/v1/query/stats** - System Statistics
Returns vector store stats and auto-load status.

### **Upload Endpoints**

#### **POST /api/v1/upload/upload** - Upload Documents
Upload PDF, images, or text files.

#### **GET /api/v1/upload/documents** - List Documents
View all uploaded documents.

## 🔄 Auto-Loading System

The system automatically loads documents from government websites on startup:

- **India Government Services Portal**
- **Passport Seva Kendra**
- **Telangana Meeseva**
- **Aadhaar Services**

## 🎯 Usage Examples

### **Ask Questions**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query/ask-simple" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to apply for passport in India?",
    "max_results": 5
  }'
```

### **Upload Documents**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload/upload" \
  -F "file=@government_document.pdf"
```

## 📊 System Status

Check auto-loading status:
```bash
curl http://127.0.0.1:8000/init-status
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
CHROMA_PERSIST_DIRECTORY=./chroma_db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
```

### **Supported File Types**
- **PDF** - `.pdf`
- **Images** - `.jpg`, `.jpeg`, `.png`
- **Text** - `.txt`

## 🎉 Benefits

- **💰 Free** - No LLM costs with Groq's free tier
- **🔒 Private** - Documents processed locally
- **⚡ Fast** - Sub-second response times
- **🔄 Automatic** - No manual document loading needed
- **🌐 Web Scraping** - Free government data sources

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/routes/         # API endpoints
│   ├── agent/              # RAG agents
│   ├── services/           # Core services
│   └── core/               # Configuration
├── chroma_db/              # Vector database
├── uploads/                # Uploaded files
├── .env                    # Environment variables
└── requirements.txt        # Dependencies
```

**Your Bureaucracy Navigator Agent is ready to help with government procedures!** 🚀
