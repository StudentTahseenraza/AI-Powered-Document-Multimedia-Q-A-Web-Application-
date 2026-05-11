# backend/app/services/llm_service.py
import httpx
import logging
from typing import AsyncGenerator, Optional
import asyncio
import json
import os

logger = logging.getLogger(__name__)

class OpenRouterLLMService:
    """FREE LLM using OpenRouter's GPT-3.5 Turbo with Streaming Support"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        self.available = bool(self.api_key and self.api_key != "")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if self.available:
            logger.info(f"✅ OpenRouter initialized with model: {self.model}")
        else:
            logger.warning("❌ OPENROUTER_API_KEY not set")
    
    def _get_headers(self) -> dict:
        """Get request headers for OpenRouter"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Document Q&A App"
        }
    
    async def generate_answer(
        self, 
        question: str, 
        context: str, 
        stream: bool = False
    ):
        """Generate answer using OpenRouter GPT-3.5 Turbo
        
        Args:
            question: User's question
            context: Document context
            stream: If True, returns async generator for streaming response
                    If False, returns complete string response
        """
        
        if not self.available:
            error_msg = "OpenRouter API not configured. Please add OPENROUTER_API_KEY to .env file"
            if stream:
                async def error_gen():
                    yield error_msg
                return error_gen()
            return error_msg
        
        system_prompt = """You are an AI assistant that answers questions based ONLY on the provided context. 
If the answer cannot be found in the context, say "I cannot find this information in the uploaded document."
Be concise, accurate, and helpful."""

        user_prompt = f"""Context:
{context}

Question: {question}

Provide a detailed, accurate answer based only on the context above.
Answer:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            if stream:
                # Return async generator for streaming
                return self._stream_response(messages)
            else:
                # Return complete response (used by summarization)
                return await self._get_response(messages)
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            error_msg = f"Error generating response: {str(e)}"
            if stream:
                async def error_gen():
                    yield error_msg
                return error_gen()
            return error_msg
    
    async def _get_response(self, messages: list) -> str:
        """Get non-streaming response (used for summarization and non-streaming chat)"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                error_msg = f"API Error: {response.status_code}"
                logger.error(error_msg)
                return error_msg
    
    async def _stream_response(self, messages: list) -> AsyncGenerator:
        """Generate streaming response for real-time chat"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "stream": True
                }
            ) as response:
                if response.status_code != 200:
                    yield f"Error: {response.status_code}"
                    return
                
                async for line in response.aiter_lines():
                    if line and line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate summary using OpenRouter (non-streaming - keeps existing functionality)"""
        if not self.available:
            return "OpenRouter API not configured. Please add OPENROUTER_API_KEY to .env file"
        
        prompt = f"""Summarize the following text in {max_length} characters or less. 
Be concise and capture the main points.

Text:
{text[:8000]}

Summary:"""
        
        messages = [
            {"role": "system", "content": "You are a text summarization assistant."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self._get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 300,
                        "temperature": 0.3,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Summary API error: {response.status_code}")
                    return f"Summary unavailable (API error: {response.status_code})"
        except Exception as e:
            logger.error(f"Summary failed: {str(e)}")
            return f"Summary failed: {str(e)}"

# Global instance
llm_service = OpenRouterLLMService()