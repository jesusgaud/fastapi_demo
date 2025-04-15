import pytest
from httpx import AsyncClient
from app.main import app  # Import your FastAPI app

@pytest.mark.asyncio
async def test_login_for_access_token():
    form_data = {
        "username": "admin",
        "password": "secret",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data=form_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_create_qr_code_unauthorized():
    # Attempt to create a QR code without authentication
    qr_request = {
        "url": "https://example.com",
        "fill_color": "red",
        "back_color": "white",
        "size": 10,
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/qr_codes/", json=qr_request)
    assert response.status_code == 401  # Unauthorized

@pytest.mark.asyncio
async def test_create_and_delete_qr_code():
    form_data = {
        "username": "admin",
        "password": "secret",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Login and get the access token
        token_response = await ac.post("/token", data=form_data)
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create a QR code
        qr_request = {
            "url": "https://example.com/test-delete",
            "fill_color": "red",
            "back_color": "white",
            "size": 10,
        }
        create_response = await ac.post("/qr_codes/", json=qr_request, headers=headers)
        assert create_response.status_code in [201, 409]  # Created or already exists

        # Try to extract filename from the 'links' or 'qr_code_url'
        if create_response.status_code == 201:
            qr_code_url = create_response.json()["qr_code_url"]
        else:
            qr_code_url = create_response.json()["links"][0]["href"]

        qr_filename = qr_code_url.split("/")[-1]

        # Delete QR Code
        delete_response = await ac.delete(f"/qr_codes/{qr_filename}", headers=headers)
        assert delete_response.status_code == 204  # No Content
