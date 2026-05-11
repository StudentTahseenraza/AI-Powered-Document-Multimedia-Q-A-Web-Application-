from io import BytesIO
from unittest.mock import AsyncMock, patch


def test_upload_file(client, auth_headers):

    client.headers.update(auth_headers)

    fake_file = BytesIO(b"fake pdf content")

    with patch(
        "app.routers.upload.FileProcessor.save_upload_file",
        new_callable=AsyncMock
    ) as mock_save:

        mock_save.return_value = (
            "/fake/path/test.pdf",
            "pdf"
        )

        response = client.post(
            "/api/upload/file",
            files={
                "file": (
                    "test.pdf",
                    fake_file,
                    "application/pdf"
                )
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "processing"