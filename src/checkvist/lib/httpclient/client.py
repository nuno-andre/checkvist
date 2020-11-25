import abc
import httpx
from collections import ChainMap
from urllib.parse import urljoin
from typing import Union, Optional, Any, List, Dict
from typing_extensions import Literal
from .models import make_content

HttpMethod = Literal[
    'GET', 'HEAD', 'DELETE', 'OPTIONS',  # bodiless
    'POST', 'PUT', 'PATCH',  # bodied
]
Json = Union[List, Dict]


def chainmap(*maps: Optional[Dict]) -> ChainMap:
    ''':class:`collections.ChainMap` factory that filters ``None``s.
    '''
    return ChainMap(*[m or {} for m in maps])


class HttpClient(abc.ABC):
    #: Default request headers.
    headers: Dict[str, str] = dict()

    def __init__(self):
        self.session = httpx.Client()
        self.session.headers.update(self.headers)

    @property
    @classmethod
    @abc.abstractmethod
    def baseurl(cls) -> str:
        ...

    def __del__(self):
        return self.close()

    def request(
        self,
        method:    HttpMethod,
        path:      str = '',
        *, params: Optional[Dict] = None,
        **kwargs:  Any,
    ) -> httpx.Response:
        url    = self.url(path)
        params = self.params(params)
        resp   = self.session.request(method, url, params=params, **kwargs)
        resp.raise_for_status()
        return resp

    def url(self, path) -> str:
        '''Builds URL.
        '''
        return urljoin(self.baseurl, path)

    def params(self, params: Optional[Dict] = None) -> ChainMap:
        '''Joins default params to the query.

        If a default param is passed also in the query, this latter will
        take preference.
        '''
        return chainmap(params, getattr(self, 'default_params', None))

    def get(self, path, params=None):
        return self.request('GET', path, params=params)

    def delete(self, path, params=None):
        return self.request('DELETE', path, params=params)

    def head(self, path, params=None):
        return self.request('HEAD', path, params=params)

    def options(self, path, params=None):
        return self.request('OPTIONS', path, params=params)

    def post(self, path, data=None, *, params=None):
        return self.request('POST', path, data=data, params=params)

    def put(self, path, data=None, *, params=None):
        return self.request('PUT', path, data=data, params=params)

    def patch(self, path, data=None, *, params=None):
        return self.request('PATCH', path, data=data, params=params)

    def close(self):
        '''Closes the session.

        This method is intended to be overriden.
        '''
        return True


class HttpParsedClient(HttpClient, abc.ABC):
    def request(
        self,
        method:    HttpMethod,
        path:      str = '',
        *, params: Optional[Dict] = None,
        data:      Optional[Dict] = None,
    ) -> Any:
        # FIXME json
        response = super().request(method, path, params=params, json=data)
        content  = make_content(response.headers)

        if content.media.subtype == 'json':
            return response.json()
        else:
            return response.text
