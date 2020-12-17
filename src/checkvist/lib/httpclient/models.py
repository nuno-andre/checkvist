from typing import NamedTuple, TypeVar, Generic, Type
from httpx import Headers, Response as _Response


T = TypeVar('T')


class MediaType(NamedTuple):
    type:    str
    subtype: str

    @property
    def tree(self):
        return self.subtype.split('.')


# TODO: disposition, language, length, location, range,
#   security_policy, security_policy_report_only,
#   and content itself
class Content(NamedTuple):
    '''Content-headers.
    '''
    media:    MediaType
    nosniff:  bool
    encoding: str
    charset:  str = None
    boundary: str = None


class Response(Generic[T]):

    def __init__(self, response: _Response, model: Type[T]):
        self.response = response
        self.model = model

    @property
    def content(self) -> Content:
        if getattr(self, '_content', None) is None:
            self._content = make_content(self.response.headers)
        return self._content

    @property
    def result(self) -> T:
        if self.content.media.subtype == 'json':
            return self.model(**self.response.json())
        else:
            raise NotImplementedError


def make_content(headers: Headers) -> Content:
    ''':class:`httpclient.Content` factory.
    '''
    mime, *kw = list(map(str.strip, headers['content-type'].split(';')))
    mime = MediaType(*mime.split('/', 1))
    kw = dict([kw[0].split('=')]) if kw else {}
    kw.update(encoding=headers.get('content-encoding', 'UTF-8'))
    nosniff = headers.get('x-content-type-options') == 'nosniff'
    return Content(mime, nosniff=nosniff, **kw)
