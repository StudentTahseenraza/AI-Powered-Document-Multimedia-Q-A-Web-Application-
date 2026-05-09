# backend/app/services/llm_service_http.py (Alternative)
import requests
import logging
from typing import AsyncGenerator
import asyncio
import json
import os

logger = logging.getLogger(__name__)

class GeminiHTTPService:
    """Gemini API using direct HTTP requests"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.available = bool(self.api_key and self.api_key != "YOUR_ACTUAL_GEMINI_API_KEY_HERE")
        
        if self.available:
            # Use the correct API endpoint
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
            self.stream_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent?key={self.api_key}"
            logger.info("✅ Gemini HTTP service initialized")
        else:
            logger.warning("❌ GOOGLE_API_KEY not set")
    
    async def generate_answer(self, question: str, context: str, stream: bool = False):
        """Generate answer using HTTP request"""
        
        if not self.available:
            return "⚠️ Gemini API not configured. Please add GOOGLE_API_KEY to .env file"
        
        prompt = f"""You are an AI assistant that answers questions based ONLY on the provided context. 
If the answer cannot be found in the context, say "I cannot find this information in the uploaded document."

Context:
{context}

Question: {question}

Provide a detailed, accurate answer based only on the context above.
Answer:"""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }
        
        try:
            if stream:
                return self._stream_response(payload)
            else:
                response = requests.post(self.api_url, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
                else:
                    return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Gemini HTTP error: {str(e)}")
            return f"Error: {str(e)}"
    
    async def _stream_response(self, payload):
        """Stream response"""
        async def generate():
            try:
                # For streaming, we'll just yield in chunks
                response = requests.post(self.stream_url, json=payload, stream=True, timeout=30)
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                if text:
                                    yield text
                            except:
                                continue
                else:
                    yield f"Error: {response.status_code}"
            except Exception as e:
                yield f"Error: {str(e)}"
        
        return generate()
    
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate summary"""
        if not self.available:
            return "Gemini API not configured"
        
        prompt = f"Summarize this text in {max_length} characters or less:\n\n{text[:8000]}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 300}
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Summary unavailable")
            else:
                return f"Summary unavailable: {response.status_code}"
        except Exception as e:
            return f"Summary error: {str(e)}"

# Use this service instead
llm_service = GeminiHTTPService()