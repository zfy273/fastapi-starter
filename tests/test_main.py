"""API 集成测试 - 使用 TestClient + SQLite 内存数据库"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.utils.security import hash_password
from app.models.user import User

# 使用 SQLite 内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    """创建测试客户端，每个测试用例使用独立的内存数据库"""
    Base.metadata.create_all(bind=engine)

    # 创建测试用户
    db = TestingSessionLocal()
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User",
        is_active=True,
        is_admin=True,
    )
    db.add(test_user)
    db.commit()
    db.close()

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def get_token(client: TestClient) -> str:
    """获取测试用户的 JWT 令牌"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"},
    )
    return response.json()["access_token"]


# ---------- 系统接口测试 ----------

class TestSystem:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "docs" in response.json()


# ---------- 认证接口测试 ----------

class TestAuth:
    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        assert response.json()["username"] == "newuser"

    def test_register_duplicate_username(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "pass123456",
            },
        )
        assert response.status_code == 400

    def test_login_success(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "wrongpass"},
        )
        assert response.status_code == 401


# ---------- 用户接口测试 ----------

class TestUser:
    def test_get_me(self, client):
        token = get_token(client)
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_get_me_unauthorized(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_list_users_admin(self, client):
        token = get_token(client)
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
