Contributing
============

Setup
-----
```shell
$ git clone https://github.com/nuno-andre/checkvist
$ cd checkvist
$ pip install -e '.[tests,docs]'
```

Test
----
```shell
$ pytest -svv tests
```

Publish
-------
The `publish` script removes old artifacts, build current version, and uploads the wheel to PyPI.

Linux/MacOS:
```shell
$ cd checkvist/scripts
$ PYPI_TOKEN=<pypi_token>
$ ./publish
```

Windows:
```powershell
PS> cd checkvist\scripts
PS> $env:PYPI_TOKEN='<pypi_token>'
PS> py.exe .\publish
```

> `TODO`: check current code is commited, tag it, push, and make a release.

Formats
-------
- Changelog: [_Keep a Changelog_](https://keepachangelog.com/en/1.0.0/).
- Commits: [_Semantic commit messages_](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716).
- Versioning: [_Semantic Versioning_](https://semver.org/spec/v2.0.0.html).