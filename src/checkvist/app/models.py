from urllib.parse import urlparse
from typing import Union, List
import abc
import re


LINK = re.compile(r'\[(?P<text>.*?)\]\((?P<url>\S*?)\)', re.M)


class Link:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    def md(self) -> str:
        return f'[{self.text}]({self.url})'

    # @classmethod
    # def from_content(cls, content):
    #     try:
    #         return cls(**LINK.search(content).groupdict())
    #     except AttributeError:
    #         pass


# TODO: search for more links
class Content:
    def __init__(self, content):
        self.content = content

    # def find_links(self) -> List[Link]:
    #     raise NotImplementedError

    # def subst_link(self, old, new):
    #     raise NotImplementedError

    def find_link(self) -> Link:
        try:
            return Link(**LINK.search(self.content).groupdict())
        except AttributeError:
            pass

    def subst_link(self, new):
        self.content = LINK.sub(new, self.content)


def get_site_class(url, domains, subdomains):
    domain = urlparse(url).netloc
    try:
        site = domains[domain]
    except KeyError:
        for k, v in subdomains.items():
            if domain.endswith(k):
                site = v
                break
        else:
            return

    return site


class MetaRegex(type, abc.ABC):
    '''Metaclass to compile regex patterns defined in class attributes.
    '''
    def __init_subclass__(cls, fields: Union[str, List[str]]):
        if isinstance(fields, str):
            fields = [fields]
        cls.fields = set(fields)

    def __new__(cls, name, bases, dict):
        for k, v in dict.items():
            if k in cls.fields and isinstance(v, str):
                dict[k] = re.compile(v)
        return super().__new__(cls, name, bases, dict)
