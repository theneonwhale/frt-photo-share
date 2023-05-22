from fastapi import status

# import pytest
# from sqlalchemy import select

from src.conf import messages
from src.schemas.users import UserDb, UserResponseFull


def test_read_users_me(client, access_token):
    response = client.get('api/users/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/me/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data

    
def test_read_user_by_id(client, access_token):
    response = client.get('api/users/1/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/1000/', headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND

    response = client.get('api/users/1/', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserResponseFull.__fields__

    for field in expected_response:
        assert field in data


def test_update_user_profile(client, admin, access_token, user, access_token_user):  # ! need
    response = client.put('api/users/1/', json=admin)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/9/', headers=headers, json=admin)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, json=admin)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/2/', headers=headers, json=user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data


def test_update_your_profile(client, admin, access_token, user, access_token_user):  # ! need
    response = client.put('api/users/me/1/', json=admin)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/me/1/', headers=headers)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/me/1/', headers=headers, json=admin)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data
 
 
def test_update_avatar_user(client, admin, access_token, mocker):
    mock_avatar = 'https://pypi.org/static/images/logo-small.2a411bc6.svg'
    mocker.patch('src.routes.users.CloudImage.avatar_upload', return_value=mock_avatar)
    files = {'file': 'avatar_1.svg'}

    response = client.patch('api/users/avatar', files=files)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.patch('api/users/avatar', headers=headers, files=files)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data

    assert response.json()['email'] == admin['email']
    assert response.json()['avatar'] == mock_avatar
    

def test_ban_user(client, access_token, admin, access_token_user):
    response = client.patch('api/users/ban_user/1/true')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.patch('api/users/ban_user/999/true', headers=headers)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.patch('api/users/ban_user/1/true', headers=headers)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC403_USER_BANNED 

    response = client.patch('api/users/ban_user/2/false', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data
