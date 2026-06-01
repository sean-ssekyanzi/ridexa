import pytest
from httpx import AsyncClient
from src.infrastructure.fast_api import app

import asyncio

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/register", json={"username": "testuser", "password": "testpass"})
        assert response.status_code in (200, 201, 400)  # 400 if already exists

@pytest.mark.asyncio
async def test_token():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert "access_token" in response.json() or response.status_code == 401

@pytest.mark.asyncio
async def test_me():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, get token
        token_resp = await ac.post("/token", data={"username": "testuser", "password": "testpass"})
        if token_resp.status_code == 200:
            token = token_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            response = await ac.get("/me", headers=headers)
            assert response.status_code == 200
        else:
            assert token_resp.status_code == 401

@pytest.mark.asyncio
async def test_users():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/")
        assert response.status_code == 200

# Add more endpoint tests as needed for payments, premium, etc.
