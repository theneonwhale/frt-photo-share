from unittest.mock import patch, AsyncMock

from src.conf import messages
from src.services.auth import AuthUser
from src.database.models import User, Comment

'''
Integration tests for the application.
'''

'''
Test src.routes.comments
1. test_add_comment
2. test_get_comments_by_image_id
3. test_update_comment
4. test_remove_comment
'''


def test_add_comment(client, session, user_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        mock_image = AsyncMock()
        monkeypatch.setattr('src.repository.images.get_image', mock_image)

        response = client.post(
            f'''/api/comment/{comment['image_id']}''',
            json={'comment': 'Test comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['comment'] == comment['comment']


def test_get_comments_by_image_id(client, session, user_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        mock_image = AsyncMock()
        monkeypatch.setattr('src.repository.images.get_image', mock_image)

        response = client.get(
            f'''/api/comment/{comment['image_id']}''',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['comment'] == comment['comment']


def test_update_comment(client, session, user_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_comment = session.query(Comment).filter_by(user_id=user.id).first()
        response = client.put(
            '/api/comment/1',
            json={'comment': 'New comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['comment'] == 'New comment'
        assert test_comment.comment == 'New comment'


#

def test_remove_comment_by_user(client, session, user_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_comment = session.query(Comment).filter_by(user_id=user.id).first()
        response = client.delete(
            f'/api/comment/{test_comment.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 403, response.text
        assert data['detail'] == messages.MSC403_FORBIDDEN


def test_remove_comment_by_admin(client, session, admin_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_comment = session.query(Comment).filter_by(user_id=user.id).first()
        response = client.delete(
            f'/api/comment/{test_comment.id}',
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['message'] == messages.COMMENT_DELETED
        try_find = session.query(Comment).filter_by(id=test_comment.id).first()
        assert try_find == None


def test_update_comment_not_found(client, session, user_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        # user = session.query(User).fiomment).filter_by(user_id=comment['user_id']).first()
        response = client.put(
            '/api/comment/999',
            json={'comment': 'New comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 404, response.text
#

def test_remove_comment_not_found(client, session, admin_token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        response = client.delete(
            '/api/comment/9999',
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        assert response.status_code == 404, response.text
