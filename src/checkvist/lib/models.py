from enum import Enum
from types import SimpleNamespace
from collections import UserString
from typing import Union, Any, Type, List, Dict
from datetime import datetime, date, timezone


DT_FMT = '%Y/%m/%d %H:%M:%S %z'
DATE_FMT = '%Y/%m/%d'


class Checklist(SimpleNamespace):
    pass


class Task(SimpleNamespace):
    '''A :class:`~lib.Task` is a :class:`~lib.Checklist` item.
    '''
    pass


class Note(SimpleNamespace):
    pass


class Date(UserString):
    def __init__(self, data):
        if isinstance(data, (datetime, date)):
            data = data.strftime('^%Y-%m-%d')
        elif isinstance(data, str) and not data.startswith('^'):
            data = f'^{data}'
        self.data = data


class Period(Enum):
    daily   = 'daily'
    weekly  = 'weekly'
    monthly = 'monthly'
    yearly  = 'yearly'


ApiResult = Union[Dict[str, Any], List[Dict[str, Any]]]
Resource = Union[Checklist, Task, Note]


# region FACTORIES
def _make_resource(
    obj: ApiResult,
    cls: Type[Resource],
) -> Union[Resource, List[Resource]]:
    '''Common resource factory.
    '''
    if isinstance(obj, list):
        return [_make_resource(o, cls) for o in obj]
    elif not isinstance(obj, dict):
        raise ValueError(f"'{obj!r}' is not a valid {type(cls)}.")

    if 'markdown?' in obj:
        obj['markdown'] = obj.pop('markdown?')

    if getattr(obj, 'due', None):
        obj['due'] = datetime.strptime(obj['due'], DATE_FMT).date()

    # TODO: make the normalized timezone configurable
    for k in ('created_at', 'updated_at', 'user_updated_at'):
        if obj.get(k):
            obj[k] = datetime.strptime(obj[k], DT_FMT).astimezone(timezone.utc)
    return cls(**obj)


def make_checklist(obj: ApiResult) -> Union[Checklist, List[Checklist]]:
    ''':class:`~lib.Checklist` factory.
    '''
    return _make_resource(obj, Checklist)


def make_task(obj: ApiResult) -> Union[Task, List[Task]]:
    ''':class:`~lib.Task` factory.
    '''
    return _make_resource(obj, Task)


def make_note(obj: ApiResult) -> Union[Note, List[Note]]:
    ''':class:`~lib.Note` factory.
    '''
    return _make_resource(obj, Note)
# endregion
