import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient, tmp_path):
    test_file = tmp_path / "test_report.txt"
    test_file.write_text("Revenue: $50,000,000\nEBITDA: $12,500,000\nNet Income: $8,000,000")

    with open(test_file, "rb") as f:
        res = await client.post(
            "/api/documents/upload",
            files={"file": ("test_report.txt", f, "text/plain")},
        )
    assert res.status_code == 201
    doc = res.json()
    assert doc["filename"] == "test_report.txt"
    assert doc["processing_status"] == "pending"
    assert doc["file_type"] == "txt"


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient):
    res = await client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert "documents" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_document_not_found(client: AsyncClient):
    res = await client.get("/api/documents/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
