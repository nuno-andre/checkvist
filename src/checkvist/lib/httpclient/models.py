from typing import NamedTuple
from httpx import Headers


class MediaType(NamedTuple):
    type:    str
    subtype: str

    @property
    def tree(self):
        return self.subtype.split('.')


# TODO: disposition, language, length, location, range,
#   security_policy, security_policy_report_only
class Content(NamedTuple):
    '''Content-headers.
    '''
    media:    MediaType
    nosniff:  bool
    encoding: str
    charset:  str = None
    boundary: str = None


def make_content(headers: Headers) -> Content:
    ''':class:`httpclient.Content` factory.
    '''
    mime, *kw = list(map(str.strip, headers['content-type'].split(';')))
    mime = MediaType(*mime.split('/', 1))
    kw = dict([kw[0].split('=')]) if kw else {}
    kw.update(encoding=headers.get('content-encoding', 'UTF-8'))
    nosniff = headers.get('x-content-type-options') == 'nosniff'
    return Content(mime, nosniff=nosniff, **kw)
