
# Common operations

This project uses [uv](https://docs.astral.sh/uv/).

* build the distribution package:
```
uv build
```

* run tests:
```
uv run python -m unittest --verbose
```

* run ruff checks:
```
uv run ruff check .
```

* serve the documentation:
```
uv --directory documentation/user_doc run mkdocs serve -a localhost:8888
```

* build the documentation into directory `user_documentation/`:
```
uv --directory documentation/user_doc run mkdocs build --clean --site-dir ../../user_documentation/
```

# Publishing a release

The creation of a tag will automatically publish a release on Github. Ensure the tag is named with the version number:
```
VERSION=v$(uv version --short) && echo $VERSION
git tag -s $VERSION -m "Release $VERSION"
git push --tags
```
