import asyncio

from fastapi.testclient import TestClient

from app.main import app, root

client = TestClient(app)


def test_root():
    '''Test root function logic
    >>> asyncio.run(root())
    {'status': 'ok'}
    '''
    result = asyncio.run(root())
    assert result == {'status': 'ok'}


def test_root_endpoint():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_log_endpoint():
    response = client.get('/log?msg=hello_world')
    assert response.status_code == 200
    assert response.json() == {'msg': 'message logged successfully'}


def test_db_endpoint():
    response = client.get('/db')
    assert response.status_code == 200
    fields = response.json().keys()
    assert list(fields) == ['db']
