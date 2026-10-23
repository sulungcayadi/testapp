# uipath_robotdoc

Reads a UiPath package (`.nupkg`), a project folder or a single `.xaml` file, stores what it finds in SQLite, and writes robot documentation as **HTML, DOCX, PPTX, XLSX, PDF and PNG**.

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .                                    # installs the `uipath-robotdoc` command
uipath-robotdoc --make-sample demo.nupkg         # sample package to try
uipath-robotdoc demo.nupkg -o robot_docs         # writes every format into ./robot_docs
```

Other invocations:

```bash
python -m uipath_robotdoc MyRobot.nupkg -o robot_docs            # every format
python -m uipath_robotdoc MyRobot.nupkg Other.nupkg -f html,xlsx   # several inputs, chosen formats
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

## Deploying
Python 3.10+ and the bundled `sqlite3` module are all it needs; SQLite is a single file, so there is no database server to set up.

- **Server / CI / scheduled job**: `pip install .` in a virtualenv, then call `uipath-robotdoc <package> -o <dir> --db <path>.db` (for example from cron, or a pipeline step after publishing a package). Keep the `--db` file on persistent storage if you want history; the output folder can be thrown away.
- **Docker**: `docker build -t uipath-robotdoc .` then `docker run --rm -v "$PWD":/work uipath-robotdoc MyRobot.nupkg -o out`. The container runs as a non-root user and writes into the mounted folder.
- The tool is a command-line program, not a web service. To serve the results, publish the generated `.html` (it is self-contained) from any static host.
