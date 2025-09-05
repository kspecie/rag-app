# Clinical Summary Generator RAG Application

A comprehensive (RAG) application designed for processing medical transcriptions and clinical documents to generate clinical summaries. This application combines document ingestion, vector storage, semantic search, and AI-powered summarization to assist healthcare professionals.

## Features

- **Document Processing**: Supports multiple document formats such as PDF, DOCX, TXT 
- **Medical Transcription Analysis**: Processes transcribed medical conversations to extract key clinical information
- **Intelligent Summarization**: Generates comprehensive clinical summaries using RAG techniques
- **Vector Database**: ChromaDB integration for efficient document retrieval and similarity search
- **Modern Web Interface**: React-based frontend with TypeScript 
- **RESTful API**: FastAPI backend with comprehensive endpoints for document management
- **Containerized Deployment**: Docker support for easy deployment and scaling
- **Message Queue Integration**: RabbitMQ for asynchronous processing of external RAG requests

## Architecture

The application follows a microservices architecture with the following components:

- **RAG Application**: Main FastAPI service handling document processing and summarization
- **TEI Service**: Text Embeddings Inference service for generating document embeddings
- **TGI Service**: Text Generation Inference service for AI-powered summarization
- **ChromaDB**: Vector database for storing and retrieving document embeddings
- **PostgreSQL**: Relational database for summary storage
- **Frontend**: React application for user interaction


### System Requirements
- Linux
- Docker and Docker Compose

### Software Dependencies
- Python 3.8+
- Node.js 18+
- Docker Engine 20.10+
- Docker Compose 2.0+

### Prerequisites and Gaudi Specific Configuration
- Intel Gaudi hardware (Gaudi 2 AI Accelerator)
- Docker with Habana runtime support
- Intel Docker Image with Pytorch:
vault.habana.ai/gaudi-docker/1.21.0/ubuntu24.04/habanalabs/pytorch-installer-2.6.0:latest


## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/kspecie/rag-app.git
cd rag-app
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
# API Configuration
API_KEY=your-unique-api-key-here

# Service URLs
TEI_SERVICE_URL=http://localhost:{PORT}
TGI_SERVICE_URL=http://localhost:{PORT}
CHROMA_HOST=host-name
CHROMA_PORT={PORT}

# Hugging Face Configuration
HF_TOKEN=your-huggingface-token

### 3. Start Services with Docker
docker-compose up -d rag-app

##This will start all required services:
- RAG Application
- TEI Service
- TGI Service 
- ChromaDB
- PostgreSQL


cd frontend
npm run dev
```


## Development Setup

### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt
docker compose up --build rag-app
```
### Frontend Development
```bash
cd frontend
# Install Node.js dependencies
npm install
# Start development server
npm run dev
# Build for production
npm run build
```


## API Endpoints

- `POST /summaries/generate/` - Generate clinical summary from conversation
- `POST /documents/upload/` - Upload new documents
- `GET /documents/` - List all documents
- `DELETE /documents/{document_id}` - Delete a document
- `GET /collections/` - List document collections
- `POST /collections/` - Create new collection
- `GET /summaries/` - Retrieve stored summaries
- `POST /summaries/` - Store new summary

## Testing

### Backend Testing
```bash
# Run all tests
pytest
# Run with coverage
pytest --cov=app
# Run specific test file
pytest tests/test_pipeline.py
```

### Frontend Testing
```bash
cd frontend
# Run unit tests
npm test
# Run tests with UI
npm run test:ui
# Run tests with coverage
npm run test:coverage
```

### Service Configuration
- **TEI Service**: Configured for BAAI/bge-small-en-v1.5 embeddings
- **TGI Service**: Configured for m42-health/Llama3-Med42-8B generation

## 🔒 Security

- API key authentication required for all endpoints
- CORS configured for development and production environments






