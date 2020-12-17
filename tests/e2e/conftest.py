import pytest
import os
from types import SimpleNamespace
from checkvist import Client


def pytest_configure():
    pytest.client = None
    pytest.checklist = None
    pytest.task = None
    pytest.note = None
    pytest.strings = SimpleNamespace(
        list_name='test_list',
        task_content='test_task',
        comment='test_note',
    )


@pytest.fixture(scope='session', autouse=True)
def client():
    print(dir(pytest))
    if pytest.client is None:
        try:
            username = os.environ['CHECKVIST_USERNAME']
            secret = os.environ['CHECKVIST_SECRET']
        except KeyError:
            raise Exception('Set CHECKVIST_USERNAME and CHECKVIST_SECRET '
                            'environment variables.')
        pytest.client = Client(username=username, secret=secret)
    yield pytest.client
    pytest.client.close()


@pytest.fixture(scope='session')
def checklist(client):
    if pytest.checklist is None:
        pytest.checklist = client.create_list(name=pytest.strings.list_name)
        print(('CHECKLIST', pytest.checklist))
    yield pytest.checklist
    if pytest.checklist is not None:
        client.delete_list(list_id=pytest.checklist.id)


@pytest.fixture(scope='session')
def task(client, checklist):
    if pytest.task is None:
        pytest.task = client.create_task(
            list_id=pytest.checklist.id,
            content=pytest.strings.task_content,
        )
        print(('TASK', pytest.task))
    yield pytest.task
    if pytest.task is not None:
        client.delete_task(list_id=pytest.checklist.id, task_id=pytest.task.id)


@pytest.fixture(scope='session')
def note(client, checklist, task):
    if pytest.note is None:
        pytest.note = client.create_note(
            list_id=pytest.checklist.id,
            task_id=pytest.task.id,
            comment=pytest.strings.comment,
        )
        print(('NOTE', pytest.note))
    yield pytest.note
    if pytest.note is not None:
        client.delete_note(
            list_id=pytest.checklist.id,
            task_id=pytest.task.id,
            note_id=pytest.note.id,
        )
