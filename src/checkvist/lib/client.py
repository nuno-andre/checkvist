import os
from typing import Optional, List, Dict
from .httpclient import HttpParsedClient, HTTPStatusError
from .models import (
    Checklist, Task, Note, Date, Period,
    make_checklist, make_task, make_note,
)


class Client(HttpParsedClient):
    '''Checkvist REST API wrapper class.

    Args:
        username: User's email address.
        secret: User password or API key.
        token:

    Attributes:
        baseurl: API base url.
        headers: Headers added to all requests.
        default_params: Params passed in all requests.
        session: :class:`httpx.Client` instance.
    '''
    baseurl = 'https://checkvist.com'
    headers = {'Content-Type': 'application/json'}
    default_params = dict(version=2)

    def __init__(
        self,
        username: Optional[str] = None,
        secret:   Optional[str] = None,
        token:    Optional[str] = None,
    ):
        super().__init__()
        self.username = username or os.getenv('CHECKVIST_USERNAME')
        self.secret   = secret or os.getenv('CHECKVIST_SECRET')
        self._token   = token or os.getenv('CHECKVIST_TOKEN')
        # auth is optional to allow access to public lists without creds
        # TODO: lazy login at first 401
        if self._token or (self.username and self.secret):
            self.session.headers.update({'X-Client-Token': self.token})

    def request(self, *args, **kwargs):
        try:
            return super().request(*args, **kwargs)
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                if self.username and self.secret:
                    raise ValueError('Invalid credentials.') from None
                else:
                    raise ValueError('Credentials not found.') from None
            raise

    # TODO: if there isn't any param with None as useful value
    #       filter those in .params()
    def url(self, path) -> str:
        return super().url(f'{path}.json')

    @property
    def token(self):
        if self._token is None:
            data = dict(username=self.username, remote_key=self.secret)
            resp = self.post('/auth/login', data)
            self._token = resp['token']
        # TODO: refresh
        return self._token

    def get_user_info(self):
        return self.get('/auth/curr_user')

# region CHECKLISTS
    def get_lists(
        self,
        archived:    bool = False,
        order_by_id: bool = False,
        order_asc:   bool = False,
        skip_stats:  bool = False,
    ) -> List[Checklist]:
        # TODO
        params = dict()
        if archived:
            params.update(archived=archived)
        if order_by_id or order_asc:
            criterion = ['updated_at', 'id'][order_by_id]
            order     = ['desc', 'asc'][order_asc]
            params.update(order=f'{criterion}:{order}')
        if skip_stats:
            params.update(skip_stats=skip_stats)
        result = self.get('/checklists', params=params)
        return make_checklist(result)

    def get_list(self, list_id: int) -> Checklist:
        result = self.get(f'/checklists/{list_id}')
        return make_checklist(result)

    # TODO: expiry? password protection? https://checkvist.com/help#share
    def create_list(
        self,
        name:   Optional[str] = None,
        public: bool = False
    ) -> Checklist:
        '''
        Args:
            name: If ``None``, name will be "Name this list".
        '''
        data   = {'checklist': {'name': name, 'public': public}}
        result = self.post('/checklists', data)
        return make_checklist(result)

    def update_list_status(
        self,
        list_id: int,
        name:    Optional[str] = None,
        public:  Optional[bool] = None,
    ) -> Checklist:
        '''Update checklist name/public status.
        '''
        data = dict()
        # XXX: name=None -> "Name this list", public=None -> False
        if name is not None:
            data['name'] = name
        if public is not None:
            data['public'] = public
        result = self.put(f'/checklists/{list_id}', dict(checklist=data))
        return make_checklist(result)

    def delete_list(self, list_id: int) -> Checklist:
        '''Mark the checklist for deletion.

        Note:
            Actual data deletion occurs later, once a day.
        '''
        result = self.delete(f'/checklists/{list_id}')
        return make_checklist(result)
# endregion

# region TASKS
    def get_tasks(self, list_id: int) -> List[Task]:
        result = self.get(f'/checklists/{list_id}/tasks')
        return make_task(result)

    def get_task(
        self, list_id: int, task_id: int, with_notes: bool = True
    ) -> Task:
        path   = f'/checklists/{list_id}/tasks/{task_id}'
        params = dict(with_notes=with_notes)
        result = self.get(path, params)
        return make_task(result)

    def create_task(
        self,
        list_id:   int,
        content:   str,
        parent_id: Optional[int] = None,
        tags:      Optional[List[str]] = None,
        due_date:  Optional[str] = None,
        position:  Optional[int] = None,
        status:    Optional[int] = None,
    ) -> Task:
        '''
        Args:
            parent_id: Id of the parent task.
            # TODO:
            due_date:  Due for the task, in `smart syntax`_ format.
            position:  1-based position in the list (default: at the end).

        .. _smart syntax:
            https://checkvist.com/help#smartSyntax
        '''
        data = dict(content=content)
        if parent_id:
            data.update(parent_id=parent_id)
        if tags:
            data.update(tags=','.join(tags))
        if due_date:
            data.update(due_date=due_date)
        if position:
            data.update(position=position)
        if status:
            data.update(status=status)

        path   = f'/checklists/{list_id}/tasks'
        result = self.post(path, {'task': data})
        return make_task(result)

    def import_tasks(self):
        raise NotImplementedError

    def update_task(
        self,
        list_id:    int,
        task_id:    int,
        content:    Optional[str] = None,
        parent_id:  Optional[int] = None,
        tags:       Optional[List[str]] = None,
        due_date:   Optional[Date] = None,
        position:   Optional[int] = None,
        parse:      bool = True,
        with_notes: bool = True,
    ) -> Task:
        '''Updates the task information. This method won't change task status.

        Args:
            content:    New task text.
            parent_id:  New parent_id task.
            tags:       List of tags to set on the task.
            # TODO
            due_date:   Due for the task, in `smart syntax`_ format.
            position:   1-based position of the task.
            parse:      If ``True``, recognize ``^due`` and ``#tags`` syntax
                        in the updated item.
            with_notes: If ``True``, the result will contain information
                        about notes added to the tasks.

        .. _smart syntax:
            https://checkvist.com/help#smartSyntax
        '''
        data = dict()
        if content is not None:
            data.update(content=content)
        if parent_id is not None:
            data.update(parent_id=parent_id)
        if tags is not None:
            data.update(tags=','.join(tags))
        if due_date is not None:
            data.update(due_date=due_date)
        if position is not None:
            data.update(position=position)

        data = dict(task=data, parse=parse, with_notes=with_notes)
        result = self.put(f'/checklists/{list_id}/tasks/{task_id}', data)
        return make_task(result)

    def _set_task(
        self,
        list_id: int,
        task_id: int,
        action:  str,
        data:    Optional[Dict[str, Dict]] = None,
    ) -> Task:
        path   = f'/checklists/{list_id}/tasks/{task_id}/{action}'
        result = self.post(path, data)
        return make_task(result)

    def close_task(self, list_id: int, task_id: int) -> Task:
        return self._set_task(list_id, task_id, 'close')

    def reopen_task(self, list_id: int, task_id: int) -> Task:
        return self._set_task(list_id, task_id, 'reopen')

    def invalidate_task(self, list_id: int, task_id: int) -> Task:
        '''Checkvist UI marks these tasks with italics.
        '''
        return self._set_task(list_id, task_id, 'invalidate')

    def repeat_task(
        self,
        list_id:      int,
        task_id:      int,
        period:       Period,
        start_date:   Date,
        end_date:     Optional[Date] = None,
        period_count: int = 1,
    ) -> Task:
        '''
        Set repeating task information.

        Args:
            period:       One of ``daily|weekly|monthly|yearly``.
            start_date:   The start date for the first repeating due.
            end_date:     The end date for the repeating due (optional).
            period_count: It is '5' in repeat every 5 weeks (default 1).
        '''
        data = dict(period=Period(period).value, period_count=period_count,
                    start_date=start_date, end_date=end_date)
        return self._set_task(list_id, task_id, 'repeat', {'repeat': data})

    def delete_task(self, list_id: int, task_id: int) -> Task:
        path   = f'/checklists/{list_id}/tasks/{task_id}'
        result = self.delete(path)
        return make_task(result)
# endregion

# region NOTES
    def get_notes(
        self,
        list_id: int,
        task_id: Optional[int] = None,
    ) -> List[Note]:
        if task_id is None:
            path = f'/checklists/{list_id}/comments'
        else:
            path = f'/checklists/{list_id}/tasks/{task_id}/comments'
        result = self.get(path)
        return make_note(result)

    def create_note(self, list_id: int, task_id: int, comment: str) -> Note:
        path   = f'/checklists/{list_id}/tasks/{task_id}/comments'
        params = {'comment': {'comment': comment}}
        result = self.post(path, params)
        return make_note(result)

    def update_note(
        self, list_id: int, task_id: int, note_id: int, comment: str
    ) -> Note:
        path   = f'/checklists/{list_id}/tasks/{task_id}/comments/{note_id}'
        params = {'comment': {'comment': comment}}
        result = self.put(path, params)
        return make_note(result)

    def delete_note(self, list_id: int, task_id: int, note_id: int) -> Note:
        path   = f'/checklists/{list_id}/tasks/{task_id}/comments/{note_id}'
        result = self.delete(path)
        return make_note(result)
# endregion
