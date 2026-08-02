import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def registered_user(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "tenant_name": "Test Company"
    })
    return res.json()


@pytest_asyncio.fixture
async def auth_headers(client, registered_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Health ---

@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] in ["healthy", "degraded"]


@pytest.mark.asyncio
async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200


# --- Auth ---

@pytest.mark.asyncio
async def test_register(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "testpass123",
        "full_name": "New User",
        "tenant_name": "New Company"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "new@example.com"
    assert data["tenant"]["name"] == "New Company"
    assert data["tenant"]["api_key"].startswith("sk_")


@pytest.mark.asyncio
async def test_register_duplicate_email(client, registered_user):
    res = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "tenant_name": "Another Company"
    })
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert "refresh_token" in res.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    res = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 403


# --- Documents ---

@pytest.mark.asyncio
async def test_list_documents_empty(client, auth_headers):
    res = await client.get("/api/v1/documents", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0


@pytest.mark.asyncio
async def test_upload_txt_document(client, auth_headers):
    content = b"What are business hours? We are open 9am to 5pm Monday to Friday."
    res = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.txt", content, "text/plain")}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "test.txt"
    assert data["status"] == "completed"
    assert data["chunk_count"] >= 1


@pytest.mark.asyncio
async def test_upload_invalid_type(client, auth_headers):
    res = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.exe", b"binary", "application/octet-stream")}
    )
    assert res.status_code == 400


# --- Chat ---

@pytest.mark.asyncio
async def test_chat_no_documents(client, auth_headers):
    res = await client.post("/api/v1/chat", headers=auth_headers, json={
        "message": "What are business hours?",
        "session_id": None
    })
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "session_id" in data


@pytest.mark.asyncio
async def test_chat_with_document(client, auth_headers):
    # Upload a document first
    content = b"Our business hours are Monday to Friday 9am to 6pm."
    await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("faq.txt", content, "text/plain")}
    )
    # Chat
    res = await client.post("/api/v1/chat", headers=auth_headers, json={
        "message": "What are business hours?",
        "session_id": None
    })
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_chat_session_continuity(client, auth_headers):
    res1 = await client.post("/api/v1/chat", headers=auth_headers, json={
        "message": "Hello",
        "session_id": None
    })
    session_id = res1.json()["session_id"]

    res2 = await client.post("/api/v1/chat", headers=auth_headers, json={
        "message": "How are you?",
        "session_id": session_id
    })
    assert res2.json()["session_id"] == session_id


# --- Widget ---

@pytest.mark.asyncio
async def test_widget_invalid_api_key(client):
    res = await client.post("/api/v1/chat/widget", json={
        "message": "Hello",
        "api_key": "sk_invalid_key_here"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_widget_valid_api_key(client, registered_user):
    api_key = registered_user["tenant"]["api_key"]
    res = await client.post("/api/v1/chat/widget", json={
        "message": "Hello",
        "api_key": api_key
    })
    assert res.status_code == 200
    assert "answer" in res.json()
