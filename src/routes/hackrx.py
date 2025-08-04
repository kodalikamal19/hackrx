import os
import io
import gc
import tempfile
from typing import List, Dict, Any
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import pypdf
import google.generativeai as genai
from src.utils.memory_manager import MemoryManager, chunk_text, StreamingProcessor

hackrx_bp = Blueprint("hackrx", __name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class PDFProcessor:
    """Memory-efficient PDF processor"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()


    
    @MemoryManager.cleanup_decorator
    def download_pdf(self, url: str) -> bytes:
        """Download PDF from URL with memory optimization"""
        try:
            # Set headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                # Try anyway, some servers don't set correct content-type
                pass
            
            # Check content length to avoid downloading huge files
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
                raise ValueError("PDF file too large (>50MB)")
            
            # Read in chunks to manage memory
            pdf_data = io.BytesIO()
            total_size = 0
            max_size = 50 * 1024 * 1024  # 50MB limit
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    total_size += len(chunk)
                    if total_size > max_size:
                        pdf_data.close()
                        raise ValueError("PDF file too large (>50MB)")
                    
                    pdf_data.write(chunk)
                    
                    # Check memory usage periodically
                    if total_size % (1024 * 1024) == 0:  # Every MB
                        if not self.memory_manager.memory_limit_check(400):  # 400MB limit
                            pdf_data.close()
                            raise MemoryError("Memory limit exceeded during download")
            
            pdf_bytes = pdf_data.getvalue()
            pdf_data.close()
            
            return pdf_bytes
            
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing PDF download: {str(e)}")
    
    @MemoryManager.cleanup_decorator
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes with memory optimization"""
        try:
            # Use BytesIO to avoid writing to disk
            pdf_stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(pdf_stream)
            
            # Check number of pages
            num_pages = len(reader.pages)
            if num_pages > 500:  # Limit pages to prevent memory issues
                print(f"Warning: PDF has {num_pages} pages, processing first 500 only")
                num_pages = 500
            
            text_parts = []
            for page_num in range(min(num_pages, len(reader.pages))):
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                    
                    # Clear page from memory
                    del page
                    
                    # Garbage collect every 10 pages and check memory
                    if page_num % 10 == 0:
                        gc.collect()
                        if not self.memory_manager.memory_limit_check(400):
                            print(f"Memory limit reached at page {page_num}, stopping extraction")
                            break
                        
                except Exception as e:
                    print(f"Warning: Failed to extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            # Clean up
            pdf_stream.close()
            del reader
            gc.collect()
            
            if not text_parts:
                raise Exception("No text could be extracted from the PDF")
            
            # Join text parts efficiently
            full_text = "\n\n".join(text_parts)
            del text_parts
            
            # Limit text length to prevent memory issues
            max_text_length = 200000  # ~200KB of text
            if len(full_text) > max_text_length:
                full_text = full_text[:max_text_length] + "\n\n[Document truncated due to length]"
            
            return full_text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

class QueryProcessor:
    """Efficient query processing using Gemini"""   
    
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.memory_manager = MemoryManager()
        self.streaming_processor = StreamingProcessor(max_memory_mb=400)
    
    @MemoryManager.cleanup_decorator
    def process_queries(self, document_text: str, questions: List[str]) -> List[str]:
        """Process multiple queries efficiently"""
        try:
            # Optimize document text for processing
            optimized_text = self._optimize_document_text(document_text)
            
            answers = []
            
            for i, question in enumerate(questions):
                try:
                    print(f"Processing question {i+1}/{len(questions)}")
                    
                    # Process with memory monitoring
                    answer = self.streaming_processor.process_with_memory_check(
                        lambda q: self._answer_single_query(optimized_text, q),
                        question
                    )
                    answers.append(answer)
                    
                    # Force cleanup between questions
                    gc.collect()
                    
                except Exception as e:
                    print(f"Error processing question '{question}': {str(e)}")
                    answers.append(f"Error processing this question: {str(e)}")
            
            return answers
            
        except Exception as e:
            raise Exception(f"Failed to process queries: {str(e)}")
    
    def _optimize_document_text(self, document_text: str) -> str:
        """Optimize document text for processing"""
        # Remove excessive whitespace
        lines = document_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Skip very short lines
                cleaned_lines.append(line)
        
        optimized_text = '\n'.join(cleaned_lines)
        
        # Limit text length for API efficiency
        max_length = 80000  # Conservative limit for API
        if len(optimized_text) > max_length:
            # Try to cut at paragraph boundary
            cut_point = optimized_text.rfind('\n\n', 0, max_length)
            if cut_point > max_length // 2:
                optimized_text = optimized_text[:cut_point] + "\n\n[Document truncated]"
            else:
                optimized_text = optimized_text[:max_length] + "\n\n[Document truncated]"
        
        return optimized_text
    
    def _answer_single_query(self, document_text: str, question: str) -> str:
        """Answer a single query using Gemini"""
        try:
            # Create focused prompt
            prompt = f"""Based on the following document, answer the question accurately and concisely.

Document:
{document_text}

Question: {question}

Instructions:
- Provide a direct, factual answer based only on the document
- If information is not in the document, state "Information not available in the document"
- Keep the answer concise but complete
- Quote specific details when relevant"""

            response = self.model.generate_content(prompt)
            
            answer = response.text.strip()
            return answer
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

@hackrx_bp.route('/v1/hackrx/run', methods=['POST'])
@cross_origin()
def hackrx_run():
    """Main HackRX API endpoint"""
    memory_manager = MemoryManager()
    
    try:
        # Log initial memory usage
        initial_memory = memory_manager.get_memory_usage()
        print(f"Initial memory usage: {initial_memory['rss_mb']:.2f}MB")
        
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        # Validate required fields
        if 'documents' not in data:
            return jsonify({'error': 'documents field is required'}), 400
        
        if 'questions' not in data:
            return jsonify({'error': 'questions field is required'}), 400
        
        documents_url = data['documents']
        questions = data['questions']
        
        # Validate inputs
        if not isinstance(documents_url, str) or not documents_url.strip():
            return jsonify({'error': 'documents must be a valid URL string'}), 400
        
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({'error': 'questions must be a non-empty list'}), 400
        
        if len(questions) > 20:  # Reduced limit for memory efficiency
            return jsonify({'error': 'Maximum 20 questions allowed'}), 400
        
        # Validate each question
        for i, question in enumerate(questions):
            if not isinstance(question, str) or not question.strip():
                return jsonify({'error': f'Question {i+1} must be a non-empty string'}), 400
            if len(question) > 1000:  # Limit question length
                return jsonify({'error': f'Question {i+1} too long (max 1000 characters)'}), 400
        
        # Process PDF
        try:
            print("Starting PDF processing...")
            pdf_processor = PDFProcessor()
            pdf_bytes = pdf_processor.download_pdf(documents_url)
            
            # Check memory after download
            memory_after_download = memory_manager.get_memory_usage()
            print(f"Memory after PDF download: {memory_after_download['rss_mb']:.2f}MB")
            
            document_text = pdf_processor.extract_text_from_pdf(pdf_bytes)
            
            # Clear PDF bytes from memory immediately
            del pdf_bytes
            gc.collect()
            
            print(f"Extracted text length: {len(document_text)} characters")
            
        except Exception as e:
            return jsonify({'error': f'PDF processing failed: {str(e)}'}), 400
        
        # Process queries
        try:
            print("Starting query processing...")
            query_processor = QueryProcessor()
            answers = query_processor.process_queries(document_text, questions)
            
            # Clear document text from memory
            del document_text
            gc.collect()
            
            print("Query processing completed")
            
        except Exception as e:
            return jsonify({'error': f'Query processing failed: {str(e)}'}), 500
        
        # Validate response
        if len(answers) != len(questions):
            return jsonify({'error': 'Mismatch between number of questions and answers'}), 500
        
        # Final memory check
        final_memory = memory_manager.get_memory_usage()
        print(f"Final memory usage: {final_memory['rss_mb']:.2f}MB")
        
        response = {
            'answers': answers
        }
        
        return jsonify(response), 200
        
    except MemoryError as e:
        memory_manager.force_garbage_collection()
        return jsonify({'error': f'Memory limit exceeded: {str(e)}'}), 507
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Unexpected error in hackrx_run: {str(e)}")
        memory_manager.force_garbage_collection()
        return jsonify({'error': 'Internal server error'}), 500

@hackrx_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    memory_manager = MemoryManager()
    memory_usage = memory_manager.get_memory_usage()
    
    return jsonify({
        'status': 'healthy',
        'service': 'HackRX API',
        'version': '1.0.0',
        'memory_usage_mb': round(memory_usage['rss_mb'], 2),
        'memory_percent': round(memory_usage['percent'], 2)
    }), 200

