from fastapi import status
import pytest
# import requests
from sqlalchemy import select
# from unittest.mock import Mock, patch

from src.conf import messages
from src.database.models import User


@pytest.fixture(scope='function')
def access_token(client, user, session, mocker) -> str:
    mocker.patch('src.routes.auth.send_email')  # mocker

    client.post('/api/auth/signup', json=user)

    current_user: User = session.scalar(select(User).filter(User.email == user['email']))
    current_user.confirmed = True
    session.commit()

    response = client.post(
                           '/api/auth/login',
                           data={'username': user.get('email'), 'password': user.get('password')},
                           )
    return response.json()['access_token']


def test_read_users_me(client, access_token):
    response = client.get('api/users/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/me/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    # assert 'roles' in response.json()
    # assert 'detail' in response.json()
    # assert 'status_active' in response.json()
  
'''
def test_read_user_by_id(client, access_token):
    response = client.get('api/users/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/1000/', headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND  # 'User Not Found.'

    response = client.get('api/users/1/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    assert 'roles' in response.json()
    assert 'detail' in response.json()
    assert 'status_active' in response.json()
    assert 'number_images' in response.json()


def test_update_user_profile_user(client, access_token, user):
    response = client.put('api/users/1/', body=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/1000/', headers=headers, body=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, body=user)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    assert 'roles' in response.json()
    assert 'detail' in response.json()
    assert 'status_active' in response.json()


def test_update_user_profile_admin(client, access_token, user_admin):
    response = client.put('api/users/1/', body=user_admin)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/1000/', headers=headers, body=user_admin)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, body=user_admin)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    assert 'roles' in response.json()
    assert 'detail' in response.json()
    assert 'status_active' in response.json()


def test_update_your_profile(client, access_token, user):
    response = client.put('api/users/me/1/', body=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/1000/', headers=headers, body=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, body=user)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    # assert 'roles' in response.json()
    # assert 'detail' in response.json()
    # assert 'status_active' in response.json()


# ----------------------------
def test_update_avatar_user(client, user, access_token, mocker):
    mock_avatar = 'https://pypi.org/static/images/logo-small.2a411bc6.svg'
    mocker.patch('src.routes.users.CloudImage.avatar_upload', return_value=mock_avatar)
    files = {'file': 'avatar_1.svg'}

    response = client.patch('api/users/avatar', files=files)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.patch('api/users/avatar', headers=headers, files=files)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
    assert response.json()['email'] == user['email']
    assert response.json()['avatar'] == mock_avatar
    

def test_ban_user(client, access_token, user):
    response = client.patch('api/ban_user', user_id=1, active_status=True)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.patch('api/ban_user', headers=headers, user_id=1000, active_status=True)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.patch('api/ban_user', headers=headers, user_id=1, active_status=True)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC403_USER_BANNED 

    response = client.patch('api/ban_user', headers=headers, user_id=3, active_status=True)
    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'created_at' in response.json()
    assert 'avatar' in response.json()
'''
