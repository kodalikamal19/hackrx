# HackRX API - Gemini-Powered Document Processor

A highly efficient Flask API that processes PDF documents and answers questions using Google's Gemini AI model. Optimized for deployment on Render with comprehensive memory management.

## Features

- **Memory-Efficient PDF Processing**: Streams PDF downloads and processes text in chunks
- **Intelligent Query Processing**: Uses Google's Gemini Pro model for accurate document-based Q&A
- **Memory Management**: Built-in memory monitoring and garbage collection
- **Error Handling**: Comprehensive error handling with detailed error messages
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Health Monitoring**: Built-in health check endpoint with memory usage stats

## API Endpoints

### POST `/api/v1/hackrx/run`

Main endpoint for processing PDF documents and answering queries.

**Request Body:**
```json
{
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the main topic of this document?",
        "What are the key findings?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "The main topic is...",
        "The key findings are..."
    ]
}
```

**Limits:**
- Maximum 20 questions per request
- Maximum 50MB PDF file size
- Maximum 1000 characters per question

### GET `/api/health`

Health check endpoint that returns service status and memory usage.

**Response:**
```json
{
    "status": "healthy",
    "service": "HackRX API",
    "version": "1.0.0",
    "memory_usage_mb": 45.2,
    "memory_percent": 2.1
}
```

## Memory Optimizations

1. **Streaming Downloads**: PDFs are downloaded in chunks to avoid loading entire files into memory
2. **Page-by-Page Processing**: PDF text extraction processes pages individually with cleanup
3. **Memory Monitoring**: Continuous memory usage monitoring with automatic cleanup
4. **Text Optimization**: Document text is cleaned and truncated to optimal lengths
5. **Garbage Collection**: Forced garbage collection between operations

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `PORT`: Port number for the server (defaults to 5001)

## Local Development

1. **Clone and Setup:**
```bash
cd hackrx-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set Environment Variables:**
```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
```

3. **Run the Application:**
```bash
python src/main.py
```

4. **Test the API:**
```bash
python test_api.py
```

## Deployment on Render

### Method 1: Using Render Dashboard

1. **Connect Repository:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service:**
   - **Name**: `hackrx-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`

3. **Set Environment Variables:**
   - `GOOGLE_API_KEY`: Your Google Gemini API key

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Method 2: Using render.yaml

1. **Push to Repository:**
```bash
git add .
git commit -m "Add HackRX API"
git push origin main
```

2. **Deploy from Dashboard:**
   - The `render.yaml` file will be automatically detected
   - Set the required environment variables in the dashboard

### Memory Configuration for Render

For Render's free tier (512MB RAM limit):
- The API is optimized to use <400MB during processing
- Memory monitoring prevents exceeding limits
- Automatic cleanup between requests

## Testing

### Manual Testing

```bash
# Health check
curl -X GET https://your-app.onrender.com/api/health

# Process document
curl -X POST https://your-app.onrender.com/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": ["What is this document about?"]
  }'
```

### Automated Testing

Run the test suite:
```bash
python test_api.py
```

## Error Handling

The API provides detailed error messages for common issues:

- **400 Bad Request**: Invalid input data, malformed JSON, missing fields
- **507 Insufficient Storage**: Memory limit exceeded
- **500 Internal Server Error**: Unexpected errors with detailed messages

## Performance Considerations

1. **PDF Size**: Large PDFs (>50MB) are rejected to prevent memory issues
2. **Question Limits**: Maximum 20 questions per request for optimal performance
3. **Text Length**: Documents are truncated to ~200KB of text for processing
4. **Timeout**: API calls have 30-second timeouts to prevent hanging

## Security

- CORS enabled for cross-origin requests
- Input validation for all parameters
- No sensitive data logging
- Environment variables for API keys

## Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce PDF size or number of questions
2. **Timeout Errors**: Check PDF accessibility and network connectivity
3. **API Key Errors**: Verify GOOGLE_API_KEY is set correctly

### Logs

Check application logs for detailed error information:
```bash
# On Render, view logs in the dashboard
# Locally, check console output
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.

