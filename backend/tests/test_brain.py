import pytest
from backend.app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_brain_root():
    """Test the root endpoint of the Jarvis Brain."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "name" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert "version" in data
