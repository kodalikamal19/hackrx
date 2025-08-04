# HackRX API Usage Examples - Gemini Version

This document provides comprehensive examples of how to use the HackRX API with Google Gemini integration for processing PDF documents and answering queries.

## Basic Usage

### Health Check

```bash
curl -X GET https://your-api-url.onrender.com/api/health
```

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

### Process PDF Document

```bash
curl -X POST https://your-api-url.onrender.com/api/v1/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?",
      "Does this policy cover maternity expenses?"
    ]
  }'
```

**Response:**
```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date.",
    "There is a waiting period of thirty-six (36) months for pre-existing diseases.",
    "Yes, the policy covers maternity expenses with a 24-month waiting period."
  ]
}
```

## Programming Examples

### Python Example

```python
import requests
import json

def query_hackrx_api(pdf_url, questions):
    """
    Query the HackRX API with a PDF document and questions
    """
    api_url = "https://your-api-url.onrender.com/api/v1/hackrx/run"
    
    payload = {
        "documents": pdf_url,
        "questions": questions
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["answers"]
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except KeyError:
        print("Unexpected response format")
        return None

# Example usage
pdf_url = "https://example.com/document.pdf"
questions = [
    "What is the main topic of this document?",
    "What are the key findings?",
    "What recommendations are made?"
]

answers = query_hackrx_api(pdf_url, questions)
if answers:
    for i, answer in enumerate(answers, 1):
        print(f"Q{i}: {questions[i-1]}")
        print(f"A{i}: {answer}\n")
```

### JavaScript Example

```javascript
async function queryHackRXAPI(pdfUrl, questions) {
    const apiUrl = 'https://your-api-url.onrender.com/api/v1/hackrx/run';
    
    const payload = {
        documents: pdfUrl,
        questions: questions
    };
    
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result.answers;
        
    } catch (error) {
        console.error('API request failed:', error);
        return null;
    }
}

// Example usage
const pdfUrl = 'https://example.com/document.pdf';
const questions = [
    'What is the main topic of this document?',
    'What are the key findings?',
    'What recommendations are made?'
];

queryHackRXAPI(pdfUrl, questions)
    .then(answers => {
        if (answers) {
            answers.forEach((answer, index) => {
                console.log(`Q${index + 1}: ${questions[index]}`);
                console.log(`A${index + 1}: ${answer}\n`);
            });
        }
    });
```

### Node.js Example

```javascript
const axios = require('axios');

async function queryHackRXAPI(pdfUrl, questions) {
    const apiUrl = 'https://your-api-url.onrender.com/api/v1/hackrx/run';
    
    const payload = {
        documents: pdfUrl,
        questions: questions
    };
    
    const config = {
        method: 'post',
        url: apiUrl,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        data: payload,
        timeout: 120000 // 2 minutes
    };
    
    try {
        const response = await axios(config);
        return response.data.answers;
        
    } catch (error) {
        if (error.response) {
            console.error('API error:', error.response.data);
        } else {
            console.error('Request failed:', error.message);
        }
        return null;
    }
}

// Example usage
const pdfUrl = 'https://example.com/document.pdf';
const questions = [
    'What is the main topic of this document?',
    'What are the key findings?',
    'What recommendations are made?'
];

queryHackRXAPI(pdfUrl, questions)
    .then(answers => {
        if (answers) {
            answers.forEach((answer, index) => {
                console.log(`Q${index + 1}: ${questions[index]}`);
                console.log(`A${index + 1}: ${answer}\n`);
            });
        }
    });
```

## Advanced Examples

### Batch Processing Multiple Documents

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_single_document(pdf_url, questions):
    """Process a single PDF document"""
    api_url = "https://your-api-url.onrender.com/api/v1/hackrx/run"
    
    payload = {
        "documents": pdf_url,
        "questions": questions
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=120)
        response.raise_for_status()
        return {
            "url": pdf_url,
            "answers": response.json()["answers"],
            "status": "success"
        }
    except Exception as e:
        return {
            "url": pdf_url,
            "error": str(e),
            "status": "error"
        }

def batch_process_documents(documents_and_questions, max_workers=3):
    """
    Process multiple documents concurrently
    
    Args:
        documents_and_questions: List of tuples (pdf_url, questions)
        max_workers: Maximum number of concurrent requests
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_doc = {
            executor.submit(process_single_document, url, questions): url
            for url, questions in documents_and_questions
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_doc):
            result = future.result()
            results.append(result)
            print(f"Completed: {result['url']} - {result['status']}")
    
    return results

# Example usage
documents = [
    ("https://example.com/doc1.pdf", ["What is the main topic?", "What are the conclusions?"]),
    ("https://example.com/doc2.pdf", ["What is the methodology?", "What are the results?"]),
    ("https://example.com/doc3.pdf", ["What is the scope?", "What are the recommendations?"])
]

results = batch_process_documents(documents)
for result in results:
    if result["status"] == "success":
        print(f"\nDocument: {result['url']}")
        for i, answer in enumerate(result["answers"]):
            print(f"Answer {i+1}: {answer}")
    else:
        print(f"\nError processing {result['url']}: {result['error']}")
```

### Error Handling and Retry Logic

```python
import requests
import time
from typing import List, Optional

class HackRXAPIClient:
    def __init__(self, base_url: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def query_document(self, pdf_url: str, questions: List[str]) -> Optional[List[str]]:
        """
        Query a PDF document with retry logic and error handling
        """
        url = f"{self.base_url}/api/v1/hackrx/run"
        payload = {
            "documents": pdf_url,
            "questions": questions
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, 
                    json=payload, 
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json()["answers"]
                elif response.status_code == 507:  # Memory limit exceeded
                    print(f"Memory limit exceeded. Reducing questions and retrying...")
                    # Reduce number of questions and retry
                    if len(questions) > 1:
                        questions = questions[:len(questions)//2]
                        payload["questions"] = questions
                        continue
                    else:
                        raise Exception("Cannot reduce questions further")
                elif response.status_code >= 500:  # Server error, retry
                    if attempt < self.max_retries:
                        print(f"Server error (attempt {attempt + 1}). Retrying in {self.retry_delay}s...")
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        raise Exception(f"Server error after {self.max_retries} retries")
                else:
                    # Client error, don't retry
                    error_msg = response.json().get("error", "Unknown error")
                    raise Exception(f"API error: {error_msg}")
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"Request timeout (attempt {attempt + 1}). Retrying...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Request timeout after retries")
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    print(f"Request failed (attempt {attempt + 1}): {e}. Retrying...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception(f"Request failed after retries: {e}")
        
        return None
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False

# Example usage
client = HackRXAPIClient("https://your-api-url.onrender.com")

# Check health first
if not client.health_check():
    print("API is not healthy!")
    exit(1)

# Query document with error handling
pdf_url = "https://example.com/document.pdf"
questions = [
    "What is the main topic?",
    "What are the key findings?",
    "What are the recommendations?"
]

try:
    answers = client.query_document(pdf_url, questions)
    if answers:
        for i, answer in enumerate(answers):
            print(f"Q{i+1}: {questions[i]}")
            print(f"A{i+1}: {answer}\n")
    else:
        print("Failed to get answers")
except Exception as e:
    print(f"Error: {e}")
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
HACKRX_API_URL = "https://your-api-url.onrender.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.get_json()
    
    if not data or 'pdf_url' not in data or 'questions' not in data:
        return jsonify({'error': 'Missing pdf_url or questions'}), 400
    
    try:
        # Call HackRX API
        response = requests.post(
            f"{HACKRX_API_URL}/api/v1/hackrx/run",
            json={
                "documents": data['pdf_url'],
                "questions": data['questions']
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'API request failed'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### React Frontend Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const DocumentAnalyzer = () => {
    const [pdfUrl, setPdfUrl] = useState('');
    const [questions, setQuestions] = useState(['']);
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const addQuestion = () => {
        setQuestions([...questions, '']);
    };

    const updateQuestion = (index, value) => {
        const newQuestions = [...questions];
        newQuestions[index] = value;
        setQuestions(newQuestions);
    };

    const removeQuestion = (index) => {
        const newQuestions = questions.filter((_, i) => i !== index);
        setQuestions(newQuestions);
    };

    const analyzeDocument = async () => {
        setLoading(true);
        setError('');
        setAnswers([]);

        try {
            const response = await axios.post(
                'https://your-api-url.onrender.com/api/v1/hackrx/run',
                {
                    documents: pdfUrl,
                    questions: questions.filter(q => q.trim() !== '')
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 120000
                }
            );

            setAnswers(response.data.answers);
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="document-analyzer">
            <h2>PDF Document Analyzer</h2>
            
            <div className="form-group">
                <label>PDF URL:</label>
                <input
                    type="url"
                    value={pdfUrl}
                    onChange={(e) => setPdfUrl(e.target.value)}
                    placeholder="https://example.com/document.pdf"
                />
            </div>

            <div className="form-group">
                <label>Questions:</label>
                {questions.map((question, index) => (
                    <div key={index} className="question-input">
                        <input
                            type="text"
                            value={question}
                            onChange={(e) => updateQuestion(index, e.target.value)}
                            placeholder={`Question ${index + 1}`}
                        />
                        {questions.length > 1 && (
                            <button onClick={() => removeQuestion(index)}>Remove</button>
                        )}
                    </div>
                ))}
                <button onClick={addQuestion}>Add Question</button>
            </div>

            <button 
                onClick={analyzeDocument} 
                disabled={loading || !pdfUrl || questions.every(q => !q.trim())}
            >
                {loading ? 'Analyzing...' : 'Analyze Document'}
            </button>

            {error && <div className="error">{error}</div>}

            {answers.length > 0 && (
                <div className="results">
                    <h3>Results:</h3>
                    {answers.map((answer, index) => (
                        <div key={index} className="qa-pair">
                            <strong>Q{index + 1}:</strong> {questions[index]}
                            <br />
                            <strong>A{index + 1}:</strong> {answer}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DocumentAnalyzer;
```

## Testing Examples

### Unit Tests

```python
import unittest
from unittest.mock import patch, Mock
import requests
from your_api_client import HackRXAPIClient

class TestHackRXAPI(unittest.TestCase):
    def setUp(self):
        self.client = HackRXAPIClient("https://test-api.com")
    
    @patch('requests.post')
    def test_successful_query(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answers": ["Answer 1", "Answer 2"]
        }
        mock_post.return_value = mock_response
        
        # Test
        result = self.client.query_document(
            "https://example.com/test.pdf",
            ["Question 1", "Question 2"]
        )
        
        # Assertions
        self.assertEqual(result, ["Answer 1", "Answer 2"])
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_memory_limit_retry(self, mock_post):
        # Mock memory limit response, then success
        mock_response_507 = Mock()
        mock_response_507.status_code = 507
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"answers": ["Answer 1"]}
        
        mock_post.side_effect = [mock_response_507, mock_response_200]
        
        # Test
        result = self.client.query_document(
            "https://example.com/test.pdf",
            ["Question 1", "Question 2"]
        )
        
        # Should succeed with reduced questions
        self.assertEqual(result, ["Answer 1"])
        self.assertEqual(mock_post.call_count, 2)

if __name__ == '__main__':
    unittest.main()
```

## Performance Optimization Tips

1. **Batch Questions**: Send multiple questions in a single request rather than multiple requests
2. **Optimize PDF Size**: Use smaller PDFs when possible (under 10MB recommended)
3. **Cache Results**: Cache frequently asked questions about the same document
4. **Concurrent Processing**: Use threading for multiple documents, but limit concurrency
5. **Error Handling**: Implement proper retry logic with exponential backoff

## Rate Limiting Considerations

While the API doesn't currently implement rate limiting, consider these best practices:

- Limit concurrent requests to 3-5 per client
- Add delays between requests if processing many documents
- Monitor response times and adjust accordingly
- Implement client-side caching for repeated queries

## Troubleshooting Common Issues

### 1. Memory Limit Exceeded (507)
```python
# Reduce number of questions or PDF size
if response.status_code == 507:
    questions = questions[:len(questions)//2]  # Reduce questions
    # Or use smaller PDF
```

### 2. Timeout Errors
```python
# Increase timeout for large documents
response = requests.post(url, json=payload, timeout=180)  # 3 minutes
```

### 3. PDF Access Issues
```python
# Verify PDF URL is accessible
test_response = requests.head(pdf_url)
if test_response.status_code != 200:
    print("PDF URL is not accessible")
```

This comprehensive guide should help you integrate and use the HackRX API effectively in your applications.

