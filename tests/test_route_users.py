from pprint import pprint

from fastapi import status

import pytest
# import requests
from sqlalchemy import select
# from unittest.mock import Mock, patch

from src.conf import messages
from src.database.models import User
from src.schemas.users import UserDb, UserResponse, UserResponseFull


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


def test_update_user_profile(client, user, access_token, user_user, access_token_user):
    response = client.put('api/users/1/', json=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/9/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/2/', headers=headers, json=user_user)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data

'''

def test_update_user_profile(client, access_token, user, access_token_admin, user_admin):
    response = client.put('api/users/2/', json=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/9/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 
    
    response = client.put('api/users/1/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/2/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/1', headers=headers, json=user_admin)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data


'''
# def test_update_user_profile_admin_ok1(client, access_token, access_token_admin_2, user, user_admin):
#     headers = {'Authorization': f'Bearer {access_token}'}
#     response = client.put('api/users/1', headers=headers, json=user_admin)
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     expected_response: dict = UserDb.__fields__

#     for field in expected_response:
#         assert field in data

'''
def test_update_user_profile_admin_ok2(client, access_token_admin, user, user_admin_2):
    response = client.put('api/users/2/', json=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token_admin}'}
    response = client.put('api/users/9/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/2/', headers=headers, json=user_admin_2)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    expected_response: dict = UserDb.__fields__

    for field in expected_response:
        assert field in data
    




def test_update_user_profile_admin_false(client, access_token_admin, user):
    response = client.put('api/users/1/', json=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token_admin}'}
    response = client.put('api/users/9/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND


def test_update_your_profile(client, access_token, user):
    response = client.put('api/users/me/1/', json=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.put('api/users/9/', headers=headers, json=user)
    assert 'detail' in response.json()
    assert response.json()['detail'] == messages.MSC404_USER_NOT_FOUND 

    response = client.put('api/users/1/', headers=headers, json=user)
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
