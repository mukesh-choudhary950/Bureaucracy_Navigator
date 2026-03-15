# Bureaucracy Navigator Agent - RAG Implementation

A FastAPI-based AI agent that helps users understand government procedures by answering queries using retrieved documents with RAG (Retrieval-Augmented Generation).

## 🚀 Features Implemented

### Core Components
- **Document Upload API** - Accept PDF, images, and text files
- **Vector Database Service** - ChromaDB for document embeddings
- **Query API** - RAG-based question answering
- **Agent Workflow** - Simple RAG agent with OpenAI integration
- **Document Processing** - PDF text extraction, OCR for images, text chunking

### Key Endpoints

#### Document Management
- `POST /api/v1/upload/upload` - Upload and process documents
- `GET /api/v1/upload/documents` - List uploaded documents
- `GET /api/v1/upload/document/{id}` - Get specific document
- `DELETE /api/v1/upload/document/{id}` - Delete document

#### Query & Question Answering
- `POST /api/v1/query/ask-simple` - Simple RAG question answering
- `POST /api/v1/query/ask` - Complex RAG with existing system
- `POST /api/v1/query/search` - Document similarity search

#### System Information
- `GET /` - Health check
- `GET /api/v1/query/tools` - Available tools
- `GET /api/v1/query/stats` - System statistics

## 🏗️ Architecture

```
backend/app/
├── main.py                 # FastAPI application entry point
├── api/routes/
│   ├── upload.py          # Document upload endpoints
│   └── query.py           # Query and RAG endpoints
├── services/
│   ├── vector_store.py    # ChromaDB vector database service
│   └── document_processor.py  # Document processing service
├── agent/
│   ├── simple_rag.py      # Simple RAG agent
│   ├── executor.py        # Complex workflow executor
│   └── memory.py          # Memory management
├── models/
│   └── user.py           # SQLAlchemy models
├── core/
│   ├── config.py         # Configuration settings
│   └── database.py       # Database setup
└── utils/
    └── middleware.py     # FastAPI middleware
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Tesseract OCR (for image processing)

### Installation Steps

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup Environment Variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_api_key_here
# SERPAPI_KEY=your_serpapi_key_here
```

3. **Install Tesseract OCR**
- **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Ubuntu**: `sudo apt-get install tesseract-ocr`

4. **Start the Server**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📝 Usage Examples

### Upload a Document
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@passport_guide.pdf"
```

### Ask a Question
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query/ask-simple" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I renew my passport?"}'
```

### Search Documents
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "passport application", "max_results": 5}'
```

## 🧪 Testing

Run the test script to verify system functionality:

```bash
python test_system.py
```

This will:
1. Check API health
2. Test query endpoints
3. Test document upload
4. Test RAG functionality

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for embeddings and generation
- `SERPAPI_KEY` - SerpAPI key for web search (optional)
- `DATABASE_URL` - Database connection string (default: SQLite)
- `REDIS_URL` - Redis connection string (optional)
- `CHROMA_PERSIST_DIRECTORY` - Vector database storage location
- `UPLOAD_DIR` - File upload directory
- `MAX_FILE_SIZE` - Maximum upload file size (default: 10MB)

### Supported File Formats
- **PDF**: `.pdf` - Text extraction using pdfplumber
- **Images**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp` - OCR using Tesseract
- **Text**: `.txt` - Direct text reading

## 🧠 How It Works

### Document Processing Pipeline
1. **Upload** → File saved to disk
2. **Extraction** → Text extracted (PDF/OCR/Text)
3. **Chunking** → Text split into 1000-character chunks
4. **Embedding** → Chunks converted to vectors using OpenAI
5. **Storage** → Vectors stored in ChromaDB with metadata

### Query Processing Pipeline
1. **Question** → User query received
2. **Retrieval** → Similar documents fetched from ChromaDB
3. **Context** → Retrieved documents formatted as context
4. **Generation** → OpenAI generates answer using context
5. **Response** → Answer returned with sources and confidence

## 📊 System Components

### Vector Store Service
- **ChromaDB Integration** - Persistent vector storage
- **OpenAI Embeddings** - text-embedding-3-small model
- **Similarity Search** - Cosine similarity matching
- **Metadata Filtering** - Search by filename, type, etc.

### Document Processor
- **Multi-format Support** - PDF, images, text files
- **Text Extraction** - pdfplumber for PDFs, Tesseract OCR for images
- **Intelligent Chunking** - LangChain RecursiveCharacterTextSplitter
- **Metadata Generation** - File info, chunk indices, statistics

### RAG Agent
- **Context-Aware Answers** - Uses retrieved documents as context
- **Source Citation** - References source documents in answers
- **Confidence Scoring** - Calculates answer confidence based on relevance
- **Query Classification** - Identifies query types for better responses

## 🚀 Future Enhancements

- Advanced LangGraph workflows
- Multi-modal document processing
- Real-time collaboration features
- Advanced filtering and search
- Document versioning
- User authentication and permissions
- Batch document processing
- Export functionality
- Integration with government APIs

## 🐛 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'fastapi.middleware.base'"**
   - Fixed: Updated import to `from starlette.middleware.base import BaseHTTPMiddleware`

2. **"Attribute name 'metadata' is reserved when using the Declarative API"**
   - Fixed: Renamed columns to `document_metadata` and `memory_metadata`

3. **Tesseract not found**
   - Install Tesseract OCR and ensure it's in your PATH

4. **OpenAI API errors**
   - Check your OPENAI_API_KEY in .env file
   - Ensure sufficient API credits

### Debug Mode
Run with debug logging:
```bash
uvicorn app.main:app --reload --log-level debug
```

## 📄 License

This project is part of the Bureaucracy Navigator Agent system.
