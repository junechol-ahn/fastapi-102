from test.utils import TestingSessionLocal, override_get_current_user, override_get_db, client, test_user
from routers.users import get_db, get_current_user
from fastapi import status
from main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get('/user/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'jon'


def test_change_password_success(test_user):
    response = client.put('/user/password', json={"password": "1234", "new_password": "111111"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put('/user/password', json={"password": "4444", "new_password": "111111"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail":"password mismatch"}


def test_change_phone_number_success(test_user):
    response = client.put('/user/phone_number/3334446666')
    assert response.status_code == status.HTTP_204_NO_CONTENT