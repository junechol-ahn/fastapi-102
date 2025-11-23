from test.utils import test_engine, TestingSessionLocal, override_get_db, test_user
from routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from main import app
from jose import jwt 
from datetime import timedelta
import pytest
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db=TestingSessionLocal()

    user = authenticate_user(test_user.username, "1234", db)
    assert user is not None
    assert user.username == test_user.username

    user = authenticate_user('wronguser', '1234', db)
    assert user is None

def test_create_access_token():
    username='testuser'
    user_id=1
    role='user'
    expires_delta=timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert username == decoded_token.get('sub') # type: ignore
    assert user_id == decoded_token.get('id') # type: ignore
    assert role == decoded_token.get('role') # type: ignore

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role':'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'could not validate user'