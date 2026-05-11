# backend/app/tests/test_basic.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_imports():
    """Test that all modules import correctly"""
    from app.routers import auth_routes, chat, documents, upload
    from app.services import file_processor, llm_service, vector_store
    assert True

def test_config_loaded():
    """Test configuration is loaded"""
    from app.config import settings
    assert settings is not None
    assert hasattr(settings, 'MONGODB_URL')

def test_openrouter_key_status():
    """Test OpenRouter key status"""
    from app.config import settings
    # Just check that the attribute exists
    assert hasattr(settings, 'OPENROUTER_API_KEY')