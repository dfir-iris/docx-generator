
# Common operations

This project uses [uv](https://docs.astral.sh/uv/).

* To build the distribution package:
```
uv build
```

* To serve the documentation:
```
uv --directory documentation/user_doc run mkdocs serve -a localhost:8888
```

* To build the documentation into directory `user_documentation/`:
```
uv --directory documentation/user_doc run mkdocs build --clean --site-dir ../../user_documentation/
```

