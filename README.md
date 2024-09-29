# piltext

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
