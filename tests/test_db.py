from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='talisson', password='senha123', email='avila@email.com'
        )
        session.add(new_user)
        session.commit()

    user_result = session.scalar(
        select(User).where(User.email == 'avila@email.com')
    )

    assert asdict(user_result) == {
        'id': 1,
        'username': 'talisson',
        'password': 'senha123',
        'email': 'avila@email.com',
        'created_at': time,
        'updated_at': time,
    }
