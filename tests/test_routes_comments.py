from unittest.mock import patch, AsyncMock
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


def test_add_comment(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        mock_image = AsyncMock()
        monkeypatch.setattr("src.repository.images.get_image", mock_image)

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        response = client.post(
            "/api/comment/1",
            json={'comment': 'Test comment'},
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['comment'] == comment['comment']


def test_get_comments_by_image_id(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        mock_image = AsyncMock()
        monkeypatch.setattr("src.repository.images.get_image", mock_image)

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        response = client.get(
            "/api/comment/1",
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['comment'] == comment['comment']


def test_update_comment(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        test_comment = session.query(Comment).filter_by(user_id=comment['user_id']).first()
        response = client.put(
            "/api/comment/1",
            json={'comment': 'New comment'},
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['comment'] == 'New comment'
        assert test_comment.comment == 'New comment'
#

def test_remove_comment(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        test_comment = session.query(Comment).filter_by(user_id=comment['user_id']).first()
        response = client.delete(
            "/api/comment/1",
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        try_find = session.query(Comment).filter_by(id=test_comment.id).first()
        assert try_find == None

def test_update_comment_not_found(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        test_comment = session.query(Comment).filter_by(user_id=comment['user_id']).first()
        response = client.put(
            "/api/comment/3",
            json={'comment': 'New comment'},
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        data = response.json()
        assert response.status_code == 404, response.text
#

def test_remove_comment_not_found(client, session, token, user, comment, monkeypatch):
    with patch.object(AuthUser, 'redis_client') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', AsyncMock())
        monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', AsyncMock())

        current_user = session.query(User).filter_by(email=user.get('email')).first()
        comment['user_id'] = current_user.id
        test_comment = session.query(Comment).filter_by(user_id=comment['user_id']).first()
        response = client.delete(
            "/api/comment/3",
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        assert response.status_code == 404, response.text

