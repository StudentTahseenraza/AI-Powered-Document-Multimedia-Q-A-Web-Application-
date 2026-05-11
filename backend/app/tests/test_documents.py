from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.auth import get_current_user
from app.database import get_db


def override_current_user():
    return {"id": "test-user-id"}


def test_get_documents(client):

    fake_docs = [
        {
            "_id": str(uuid4()),
            "user_id": "test-user-id",
            "filename": "test.pdf",
            "created_at": datetime.utcnow()
        }
    ]

    mock_db = MagicMock()

    mock_cursor = MagicMock()

    mock_cursor.sort.return_value.to_list = AsyncMock(
        return_value=fake_docs
    )

    mock_db.documents.find.return_value = mock_cursor

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/documents/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["filename"] == "test.pdf"

    app.dependency_overrides.clear()


def test_delete_document_not_found(client):

    mock_db = MagicMock()

    mock_db.documents.find_one = AsyncMock(
        return_value=None
    )

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.delete(
        f"/api/documents/{uuid4()}"
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()