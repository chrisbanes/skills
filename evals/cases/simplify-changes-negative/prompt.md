Clean this up, report only. Only look at reuse in the supplied change to
`heading.py`. The new public function returns the supplied heading, including
an intentionally empty string, and falls back to the title only for None.

```python
def heading(value, title):
    return title if value is None else value
```

The existing shared helper is `label_or_default(value, default)`, implemented
as `return value or default`. Its callers depend on blank labels using the
default. This is the entire change.
