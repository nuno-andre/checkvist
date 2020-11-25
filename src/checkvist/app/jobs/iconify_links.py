"""
Prepends site's icon to link and removes site's name.
"""
from checkvist.app.models import Content, Link, get_site_class, MetaRegex
from checkvist.lib import Task
import logging

log = logging.getLogger(__name__)


class CleanRegex(MetaRegex, fields='clean'):
    ...


class IconLink(Link, metaclass=CleanRegex):
    @Link.text.setter
    def text(self, value: str):
        if hasattr(self, 'clean'):
            clean = self.clean.sub('', value).strip()
            value = clean or value.strip()
        if hasattr(self, 'icon') and f'fa-{self.icon}' not in value:
            value = f'<i class="fab fa-{self.icon} fa-lg"></i> {value}'
        self._text = value


class Dev(IconLink):
    icon = 'dev'
    clean = r'\s\-\sDEV.*?$'


class DigitalOcean(IconLink):
    icon = 'digital-ocean'
    clean = r'\s(\|\s)?DigitalOcean$'


class GitHub(IconLink):
    icon = 'github'
    clean = r'^GitHub\s\-\s'


class GitLab(IconLink):
    icon = 'gitlab'
    clean = r'\s·\sGitLab$'


class Google(IconLink):
    icon = 'google'
    clean = r'\s\-\s.*?Google(\sSearch)?$'


class HackerNews(IconLink):
    icon = 'hacker-news'
    clean = r'\s(\|\s)?Hacker News$'


class Medium(IconLink):
    icon = 'medium'
    clean = r'\s\|\sMedium$'


class Reddit(IconLink):
    icon = 'reddit'
    check = r'^[a-z0-9]*$'


class ResearchGate(IconLink):
    icon = 'researchgate'


class StackExchange(IconLink):
    icon = 'stack-exchange'


class StackOverflow(IconLink):
    icon = 'stack-overflow'
    clean = r'\s\-\sStack Overflow$'


class Wikipedia(IconLink):
    icon = 'wikipedia-w'
    clean = r'\s\-\sWikipedia.*?$'


class YouTube(IconLink):
    icon = 'youtube'
    clean = r'\s\-\sYouTube'


# TODO: add domains as attr of the class
DOMAINS = {
    'dev.to': Dev,
    'digitalocean.com': DigitalOcean,
    'github.com': GitHub,
    'gitlab.com': GitLab,
    'www.google.com': Google,
    'news.ycombinator.com': HackerNews,
    'medium.com': Medium,
    'towardsdatascience.com': Medium,
    'uxdesign.cc': Medium,
    'uxplanet.org': Medium,
    'writingcooperative.com': Medium,
    'blog.prototypr.io': Medium,
    'festivalpeak.com': Medium,
    'reddit.com': Reddit,
    'researchgate.net': ResearchGate,
    'stackexchange.com': StackExchange,
    'mathoverflow.net': StackExchange,
    'serverfault.com': StackExchange,
    'superuser.com': StackExchange,
    'stackoverflow.com': StackOverflow,
    'wikipedia.org': Wikipedia,
    'youtube.com': YouTube,
}

SUBDOMAINS = {f'.{k}': v for k, v in DOMAINS.items()}


def main(task: Task) -> str:
    try:
        cont = Content(task.content)
        link = cont.find_link()
        cls  = get_site_class(link.url, DOMAINS, SUBDOMAINS)
        new  = cls(link.text, link.url).md()
        if new != link.md():
            log.info('Link iconified: %s', new)
            cont.subst_link(new)
            return cont.content
    except (AttributeError, TypeError):
        pass
