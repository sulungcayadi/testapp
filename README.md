# uipath_robotdoc

Reads a UiPath package (`.nupkg`), a project folder or a single `.xaml` file, stores what it finds in SQLite, and writes robot documentation as **HTML, DOCX, PPTX, XLSX, PDF and PNG**.

```bash
pip install -r requirements.txt
python -m uipath_robotdoc MyRobot.nupkg -o robot_docs            # every format
python -m uipath_robotdoc MyRobot.nupkg Other.nupkg -f html,xlsx   # several inputs, chosen formats
python -m uipath_robotdoc --make-sample demo.nupkg                 # try it without a real package
```

## What is extracted
- **Package**: name, version, description, entry point, expression language, target framework, dependencies (`project.json` / `.nuspec`).
- **Per workflow** (`.xaml`): arguments (direction, type), variables (type, default, scope), full activity outline (type, display name, annotation, key property such as selector/file/URL), and invoked workflows.
- **Review notes**: workflows nobody invokes, invocations whose target is not in the package, files that fail to parse.

## Outputs
| Format | Best for |
|---|---|
| `html` | Single self-contained page with navigation and embedded diagrams |
| `docx` / `pdf` | Hand-over / sign-off document |
| `pptx` | Walkthrough slides (overview, diagrams, one slide per workflow) |
| `xlsx` | Filterable tables: workflows, arguments, variables, activities, invocations |
| `png` | Call graph and activity usage charts |

The parsed data is kept in `<out>/robot_docs.db` (override with `--db`); re-running on the same package name and version replaces its rows. Tables: `packages`, `dependencies`, `workflows`, `arguments`, `variables`, `activities`, `invocations`.

## Notes
- Input is parsed read-only; XAML containing DOCTYPE/ENTITY declarations is rejected and archive members over 50 MB are refused.
- PNG output and diagrams in other formats need matplotlib; without it the tool still writes the other formats.
- Activity detection is heuristic (display names, UiPath namespaces and core statements), so unusual custom activities without a `DisplayName` may be skipped.

Run the tests with `python -m pytest`.
