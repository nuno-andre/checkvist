"""
Clean some URLs.
"""
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs, ParseResult
from checkvist.app.models import Content, Link, get_site_class, make_url
from checkvist.lib import Task
import logging

log = logging.getLogger(__name__)


class CleanUrl(Link):
    def __init__(self, text: str, url: str):
        url = urlparse(url)
        self.query = parse_qs(url.query)
        self.text = text
        self.url = url

    @property
    def url(self) -> str:
        url = self._url + ('',) * (6 - len(self._url))
        return urlunparse(url)

    @url.setter
    def url(self, url: ParseResult):
        self._url = url


class Google(CleanUrl):
    @CleanUrl.url.setter
    def url(self, url):
        # remove all params except the query itself
        query = {'q': self.query['q'][0]}
        self._url = make_url(netloc='google.com', fragment=urlencode(query))


class Reddit(CleanUrl):
    @CleanUrl.url.setter
    def url(self, url):
        # removes article's title from url
        path = list(filter(None, url.path.split('/')))
        try:
            # if path[-3] == 'comments' and self.check.fullmatch(path[-2]):
            if path[-3] == 'comments':
                url = url._replace(path='/'.join(path[:-1]), query=None)
        except IndexError:
            pass
        self._url = url


class StackExchange(CleanUrl):
    @CleanUrl.url.setter
    def url(self, url):
        # remove question title from url
        path = url.path.split('/')
        if not path[-1].isnumeric():
            # question
            url = url._replace(path='/'.join(path[:-1]))
        else:
            # answer
            path = f'/a/{path[-1]}'
            url = url._replace(path=path, fragment=None)
        self._url = url


class YouTube(CleanUrl):
    @CleanUrl.url.setter
    def url(self, url):
        if list(self.query.keys()) == ['v']:
            url = ('https', 'youtu.be', self.query['v'][0])
        self._url = url


# TODO: add domains as an attr of the class
#       and another attr for excluded subdomains
DOMAINS = {
    'www.google.com': Google,
    'googl.com': Google,
    'gogle.com': Google,
    'reddit.com': Reddit,
    'stackexchange.com': StackExchange,
    'mathoverflow.net': StackExchange,
    'serverfault.com': StackExchange,
    'superuser.com': StackExchange,
    'stackoverflow.com': StackExchange,
    'youtube.com': YouTube,
}

SUBDOMAINS = {f'.{k}': v for k, v in DOMAINS.items()}


def main(task: Task) -> str:
    try:
        cont = Content(task.content)
        link = cont.find_link()
        cls  = get_site_class(link.url, DOMAINS, SUBDOMAINS)

        # TODO: move checks to class
        if cls is Google:
            # TODO: retrieve canonical URL
            if 'www.google.com/amp/s/' in link.url:
                log.warning('Google AMP: %s', link.url)
                return
            # TODO: image search
            elif 'search?tbs=' in link.url:
                log.warning('Google Image Search: %s', link.url)
                return

        new = cls(link.text, link.url).md()
        if new != link.md():
            log.info('URL cleaned: %s', new)
            cont.subst_link(new)
            return cont.content
    except (AttributeError, TypeError):
        pass

    # try:
    #     link = LINK.search(task.content).groupdict()
    #     cls  = get_site_class(link['url'], DOMAINS, SUBDOMAINS)
    #     if cls is Google:
    #         # TODO: retrieve canonical URL
    #         if 'www.google.com/amp/s/' in link['url']:
    #             log.warning('Google AMP: %s', link['url'])
    #             return
    #         # TODO: image search
    #         elif 'search?tbs=' in link['url']:
    #             log.warning('Google Image Search: %s', link['url'])
    #             return
    #     new  = cls(**link).md()
    #     log.info('URL cleaned: %s', new)
    #     return LINK.sub(new, task.content)
    # except (AttributeError, TypeError):
    #     pass
