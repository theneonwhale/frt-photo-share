from unittest.mock import patch, AsyncMock, MagicMock

import unittest.mock as um

from src.conf import messages
from src.services.auth import AuthUser
from src.database.models import User, Image

'''
Integration tests for the application.
'''

'''
Test src.routes.comments
1. test_create_image
2. test_get_image
3. test_get_images
4. test_get_image_by_tag_name
5. test_get_image_by_user
6. test_update_image
7. test_remove_image
8. test_transforme_image
9. test_image_qrcode
'''


def test_create_image(client, session, admin, admin_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.images.CloudImage.get_url_for_image', mock_src_url)
        current_user = session.query(User).filter_by(email=admin.get('email')).first()
        session.expunge(current_user)

        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': image['tags']},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
            )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['description'] == image['description']
        assert data['tags'][0]['name'] == image['tags'].split()[0]
        assert data['user_id'] == current_user.id
        assert 'id' in data


def test_create_image_by_user(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.images.CloudImage.get_url_for_image', mock_src_url)
        current_user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(current_user)

        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': image['tags']},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
            )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['description'] == image['description']
        assert data['tags'][0]['name'] == image['tags'].split()[0]
        assert data['user_id'] == current_user.id
        assert 'id' in data


def test_create_image_toomanytags(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.images.CloudImage.get_url_for_image', mock_src_url)
        user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(user)
        tags = ' '.join(['tag' for i in range(11)])
        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': tags},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
            )
        assert response.status_code == 409, response.text
        data = response.json()
        assert data['detail'] == messages.MSC409_TAGS


def test_create_image_no_token(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.images.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.images.CloudImage.get_url_for_image', mock_src_url)
        user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(user)

        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': image['tags']},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                # headers={'Authorization': f'Bearer some_token'}
            )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail'] == 'Not authenticated'


def test_get_image(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            '/api/images/1',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == image['description']
        assert 'id' in data


def test_image_no_such_image(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            '/api/images/999',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_get_images(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            '/api/images/',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['items'][0]['description'] == image['description']
        assert 'id' in data['items'][0]


def test_get_images_not_authenticated(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            '/api/images/',
            # headers={'Authorization': f'Bearer {token['access_token']}'}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail'] == 'Not authenticated'


def test_get_image_by_tag_name(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
                              f'''api//images/search_bytag/{image['tags'].split()[0]}''',
                              params={'sort_direction': 'asc'},
                              headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
                              )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['description'] == image['description']
        assert 'id' in data[0]


def test_get_image_by_tag_name_no_tags(client, session, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            # f'api//images/search_bytag/{image['tags'].split()[0]}',
            f'api//images/search_bytag/no_tag',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_TAG_NOT_FOUND


def test_get_image_by_user_userrole(client, session, user_token, user, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()

        response = client.get(
            f'/api/images/search_byuser/{user.id}',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 403, response.text
        assert data['detail'] == messages.MSC403_FORBIDDEN


def test_get_image_by_user_adminrole(client, session, admin_token, user, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(user)

        response = client.get(
            f'/api/images/search_byuser/{user.id}',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['user_id'] == user.id


def test_get_image_by_user_no_user(client, session, admin_token, user, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.get(
            f'/api/images/search_byuser/9999',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_USER_NOT_FOUND


def test_transforme_image(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.post(
            f'/api/images/transformation/{test_image.id}',
            params={'type': 'black_white'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert 'e_grayscale' in data['link']


def test_transforme_foreign_image(client, session, admin, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        admin = session.query(User).filter_by(email=admin.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=admin.id).first()

        response = client.post(
            f'/api/images/transformation/{test_image.id}',
            params={'type': 'black_white'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 400, response.text
        assert data['detail'] == messages.MSC400_BAD_REQUEST


def test_transforme_image_not_found(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        # user = session.query(User).filter_by(email=user.get('email')).first()
        # test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.post(
            f'/api/images/transformation/9999',
            params={'type': 'black_white'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_image_qrcode(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.get(
            f'/api/images/qrcode/{test_image.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'image/png'
        assert type(response._content) is bytes


def test_image_qrcode_not_found(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        # user = session.query(User).filter_by(email=user.get('email')).first()
        # test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.get(
            f'/api/images/qrcode/9999',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )

        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_update_image(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.put(
            f'/api/images/{test_image.id}',
            json={'description': 'update description', 'tags': 'update_tag'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == 'update description'
        assert data['tags'][0]['name'] == 'update_tag'
        assert 'id' in data


def test_update_foreign_image_by_user(client, session, admin, user_token, image, monkeypatch):
    # image.id = 1 user.id = 1 roles = admin
    # image.id = 2 user.id = 2 roles = user
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        admin = session.query(User).filter_by(email=admin.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=admin.id).first()

        response = client.put(
            f'/api/images/{test_image.id}',
            json={'description': 'update description', 'tags': 'update_tag'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_update_foreign_image_by_admin(client, session, user, admin_token, image, monkeypatch):
    # image.id = 1 user.id = 1 roles = admin
    # image.id = 2 user.id = 2 roles = user
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.put(
            f'/api/images/{test_image.id}',
            json={'description': 'update description', 'tags': 'update_tag'},
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == 'update description'
        assert data['tags'][0]['name'] == 'update_tag'
        assert 'id' in data


def test_remove_image(client, session, user, user_token, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.delete(
            f'/api/images/{test_image.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['message'] == messages.IMAGE_DELETED
        assert session.query(Image).filter_by(id=test_image.id).first() is None


def test_remove_foreign_image_by_user(client, session, admin, user_token, image, monkeypatch):
    # image.id = 1 user.id = 1 roles = admin
    # image.id = 2 user.id = 2 roles = user
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        admin = session.query(User).filter_by(email=admin.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=admin.id).first()

        response = client.delete(
            f'/api/images/{test_image.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_remove_foreign_image_by_admin(client, session, user, admin_token, image, monkeypatch):
    # image.id = 1 user.id = 1 roles = admin
    # image.id = 2 user.id = 2 roles = user
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.delete(
            f'/api/images/{test_image.id}',
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['message'] == messages.IMAGE_DELETED
        assert session.query(Image).filter_by(id=test_image.id).first() is None


def test_get_image_by_user_no_image(client, session, admin_token, user, image, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(user)
        images = session.query(Image).all()

        response = client.get(
            f'/api/images/search_byuser/{user.id}',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND
