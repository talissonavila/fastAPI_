from http import HTTPStatus

from fastapi_zero.schemas import UserPublic
from fastapi_zero.security import create_access_token


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'talisson',
            'email': 'avila@email.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'talisson',
        'email': 'avila@email.com',
        'id': 1,
    }


def test_create_user_should_return_400_username_exists__exercicio(
    client, user
):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_should_return_400_email_exists__exercicio(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'talisson',
            'email': 'avila@email.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'talisson',
        'email': 'avila@email.com',
        'id': user.id,
    }


def test_update_integrity_error_username(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'talisson',
            'email': 'avila@email.com',
            'password': 'senha',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'talisson',
            'email': 'teste@test.com',
            'password': 'senha123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_integrity_error_email(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'talisson',
            'email': 'avila@email.com',
            'password': 'senha',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Teste',
            'email': 'avila@email.com',
            'password': 'senha123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_update_user_should_return_not_enough_permissions(client, user, token):
    response = client.put(
        '/users/666',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_should_return_unauthorized(client):
    response = client.delete('/users/666')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_user_should_return_not_found(client, user):
    response = client.get('/users/666')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_user(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
