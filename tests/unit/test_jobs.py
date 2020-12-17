from checkvist.app.jobs.clean_urls import (
    Google, Reddit, StackExchange, YouTube,
)


# region CLEAN URLS
def test_google():
    url  = 'https://www.googl.com/search?client=firefox-b-d&q=search+query'
    link = Google(text='', url=url)
    assert link.url == 'https://google.com#q=search+query'


def test_reddit():
    url  = 'https://www.reddit.com/r/reddit.com/comments/lggmm/damn_brilliant_idea/?utm_source=share&utm_medium=web2x&context=3'
    link = Reddit(text='', url=url)
    assert link.url == 'https://www.reddit.com/r/reddit.com/comments/lggmm'


def test_stackexchange():
    # question
    url  = 'https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array'
    link = StackExchange(text='', url=url)
    assert link.url == 'https://stackoverflow.com/questions/11227809'

    # answer
    url = 'https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array/11227902#11227902'
    link = StackExchange(text='', url=url)
    assert link.url == 'https://stackoverflow.com/a/11227902'


def test_youtube():
    url  = 'https://www.youtube.com/watch?v=lVPLIuBy9CY'
    link = YouTube(text='', url=url)
    assert link.url == 'https://youtu.be/lVPLIuBy9CY'

# endregion
