from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.user import UserGroup
from sqlalchemy.orm import sessionmaker
from app.models.user import User, ActivationToken


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    if not db.query(UserGroup).filter(UserGroup.name == "USER").first():
        db.add(UserGroup(name="USER"))
        db.commit()
    db.close()


def teardown_test_db():
    Base.metadata.drop_all(bind=engine)


def test_user_registration():
    teardown_test_db()
    setup_test_db()
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "alopar632@gmail.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "alopar632@gmail.com"
    assert response.json()["is_active"] is False
    teardown_test_db()


def test_user_registration_email_exists():
    teardown_test_db()
    setup_test_db()
    client.post(
        "/api/v1/auth/register",
        json={"email": "alopar632@gmail.com", "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "alopar632@gmail.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    teardown_test_db()


def test_user_activation():
    teardown_test_db()
    setup_test_db()
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "alopar632@gmail.com", "password": "password123"}
    )
    db = TestingSessionLocal()
    token = db.query(ActivationToken).filter_by(user_id=register_response.json()["id"]).first()
    db.close()

    assert token is not None

    activation_response = client.post(
        "/api/v1/auth/activate",
        json={"token": token.token}
    )

    assert activation_response.status_code == 200
    assert "Account activated successfully" in activation_response.json()["message"]

    db = TestingSessionLocal()
    user = db.query(User).filter_by(email="alopar632@gmail.com").first()
    db.close()
    assert user.is_active is True

    teardown_test_db()


def test_successful_login():
    teardown_test_db()
    setup_test_db()

    db = TestingSessionLocal()
    hashed_password = get_password_hash("test_password123")
    user = User(email="test@example.com", hashed_password=hashed_password, is_active=True)
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "test_password123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    teardown_test_db()


def test_login_with_incorrect_password():
    teardown_test_db()
    setup_test_db()

    db = TestingSessionLocal()
    hashed_password = get_password_hash("correct_password")
    user = User(email="test@example.com", hashed_password=hashed_password, is_active=True)
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong_password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    teardown_test_db()


def test_login_with_inactive_account():
    teardown_test_db()
    setup_test_db()

    db = TestingSessionLocal()
    hashed_password = get_password_hash("test_password123")
    user = User(email="inactive@example.com", hashed_password=hashed_password, is_active=False)
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "test_password123"}
    )

    assert response.status_code == 400
    assert "Account not activated" in response.json()["detail"]
    teardown_test_db()


def test_login_with_nonexistent_email():
    teardown_test_db()
    setup_test_db()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "some_password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    teardown_test_db()
