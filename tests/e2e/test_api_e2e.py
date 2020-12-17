"""
End-to-end tests.
"""
import pytest


@pytest.mark.dependency()
def test_list_creation(client):
    pytest.checklist = client.create_list(name=pytest.strings.list_name)
    assert pytest.checklist.name == pytest.strings.list_name


@pytest.mark.dependency(depends=['test_list_creation'])
def test_task_creation(client, checklist):
    pytest.task = client.create_task(
        list_id=pytest.checklist.id,
        content=pytest.strings.task_content,
    )
    assert pytest.task.content == pytest.strings.task_content
    assert pytest.task.checklist_id == checklist.id


@pytest.mark.dependency(depends=['test_task_creation'])
def test_note_creation(client, checklist, task, note):
    pass


@pytest.mark.dependency(depends=['test_note_creation'])
def test_note_deletion(client, checklist, task, note):
    pass


@pytest.mark.dependency(depends=['test_task_creation'])
def test_task_deletion(client):
    pass


@pytest.mark.dependency(depends=['test_list_creation'])
def test_list_deletion(client, checklist):
    # pytest.checklist = client.delete_list(checklist.id)
    pass
