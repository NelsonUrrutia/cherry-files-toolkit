# Cherry Files Picker UI Sketch

Search/results area on the left, selected files fixed on the right.

```text
+--------------------------------------------------------------------+
| Cherry Files Picker                                                |
+-------------------------------+------------------------------------+
| Search: [ app.py........... ] | Selected Files                    |
|-------------------------------|------------------------------------|
| > [ ] src/app.py              |  src/main.py              [x]     |
|   [x] src/main.py             |  docs/app.md              [x]     |
|   [ ] tests/test_app.py      |  README.md                [x]     |
|   [ ] docs/app.md            |                                    |
|                               |  [Clear all]                      |
|                               |                                    |
|                               |  Selected count: 3                |
+-------------------------------+------------------------------------+
```

Notes:
- Left side is the active search and results area.
- Right side stays persistent and shows the current selection.
- The selected panel should scroll when the list grows.
- `Clear all` belongs in the selected panel.
