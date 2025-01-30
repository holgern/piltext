# piltext

[![codecov](https://codecov.io/gh/holgern/piltext/graph/badge.svg?token=VyIU0ZxwpD)](https://codecov.io/gh/holgern/piltext)
[![PyPi Version](https://img.shields.io/pypi/v/piltext.svg)](https://pypi.python.org/pypi/piltext/)

Creates PNG from text using Pillow

### Installation

PyPI

```bash
pip install piltext
```

or from source

```bash
git clone https://github.com/holgern/piltext.git
cd piltext
python3 setup.py install
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Pre-commit-config

### Installation

```
$ pip install pre-commit
```

### Using homebrew:

```
$ brew install pre-commit
```

```
$ pre-commit --version
pre-commit 2.10.0
```

### Install the git hook scripts

```
$ pre-commit install
```

### Run against all the files

```
pre-commit run --all-files
pre-commit run --show-diff-on-failure --color=always --all-files
```

### Update package rev in pre-commit yaml

```bash
pre-commit autoupdate
pre-commit run --show-diff-on-failure --color=always --all-files
```
