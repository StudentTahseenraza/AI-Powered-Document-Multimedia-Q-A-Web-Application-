from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch
import asyncio


def test_ask_question(client, auth_headers):
    from app.database import mongodb

    document_id = str(uuid4())

    document = {
        "_id": document_id,
        "user_id": "test-user-id",
        "filename": "chat.pdf",
        "extracted_text": "Artificial intelligence content",
        "created_at": datetime.utcnow()
    }

    asyncio.run(
        mongodb.db.documents.insert_one(document)
    )

    client.headers.update(auth_headers)

    with patch(
        "app.routers.chat.vector_store.search",
        new_callable=AsyncMock
    ) as mock_search, patch(
        "app.routers.chat.llm_service.generate_answer",
        new_callable=AsyncMock
    ) as mock_answer:

        mock_search.return_value = [
            {"text": "AI means artificial intelligence"}
        ]

        mock_answer.return_value = "AI means artificial intelligence"

        response = client.post(
            "/api/chat/ask",
            json={
                "document_id": document_id,
                "question": "What is AI?"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert "answer" in data


def test_ask_question_missing_fields(client, auth_headers):

    client.headers.update(auth_headers)

    response = client.post(
        "/api/chat/ask",
        json={}
    )

    assert response.status_code == 400