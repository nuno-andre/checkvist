[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://raw.githubusercontent.com/nuno-andre/checkvist/main/LICENSE) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/checkvist.svg)](https://pypi.python.org/pypi/checkvist/)

Checkvist
=========

[_Checkvist_][features] is an online list making app with minimalist UI and amazing keyboard and Markdown support. This package is an unofficial Python wrapper library over its [REST API][apidocs].

Setup
-----
```shell
$ pip install checkvist
```

Example
-------
```python
In [1]: from checkvist import Client
   ...:
   ...: client = Client(username=<username>, secret=<secret>)  # [1]

In [2]: client.create_list(name='next trip')
   ...: # a new list to organize my next trip
Checklist(archived=False,
          id=700700,
          item_count=0,
          markdown=True,
          name='next trip',
          options=2,
          percent_completed=0.0,
          public=False,
          read_only=False,
          tags={},
          tags_as_text='',
          task_completed=0,
          task_count=0,
          updated_at=datetime.datetime(2020, 11, 28, 10, 0, 0, tzinfo=datetime.timezone.utc),
          user_count=1,
          user_updated_at=None)

In [3]: client.create_task(list_id=700700, content='Search for air tickets', due_date='next friday')
   ...: # on Friday next week, I should have purchased the tickets
Task(assignee_ids=[],
     checklist_id=700700,
     collapsed=False,
     comments_count=0,
     content='Search for air tickets',
     details={},
     due=datetime.date(2020, 12, 11),
     due_user_ids=[170000],
     id=45004500,
     parent_id=0,
     position=1,
     status=0,
     tags={},
     tags_as_text='',
     tasks=[],
     update_line='created by <My Name>',
     updated_at=datetime.datetime(2020, 11, 28, 10, 1, 0, tzinfo=datetime.timezone.utc))
```

**[1]**: params only required if `CHECKVIST_USERNAME` and `CHECKVIST_SECRET` environment variables aren't set.

Links
-----
- [Checkvist features][features]
- [Online demo](https://beta.checkvist.com/checklists/783262-introduction-to-checkvist "Introduction to Checkvist")
- [Feedback](https://checkvist.com/auth/feedback)
- [API docs][apidocs]
- [API mail group](https://groups.google.com/g/checkvist-api)
- [Checkvist UserVoice](https://checkvist.uservoice.com/forums/2121-checkvist-web)


[features]: https://checkvist.com/auth/features "List making on steroids"
[apidocs]: https://checkvist.com/auth/api "Open API"

---

Copyright &copy; 2020 Nuno André
